from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import JSONField

class AccountManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='user', company_name=None):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, company_name=company_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('company', 'Company'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    company_name = models.CharField(max_length=255, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = AccountManager()

    def __str__(self):
        return self.username


# --- Profile, Skill, Language models for profile editing and dropdowns ---
class Skill(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    JOB_PREFERENCE = (
        ("remote", "Remote"),
        ("onsite", "Onsite"),
        ("hybrid", "Hybrid"),
    )

    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    currently = models.CharField(max_length=255, null=True, blank=True)
    skills = models.ManyToManyField(Skill, through="ProfileSkill", blank=True)
    languages = models.ManyToManyField(Language, through="ProfileLanguage", blank=True)
    job_preference = models.CharField(max_length=20, choices=JOB_PREFERENCE, default="remote")
    experience = models.CharField(max_length=255, null=True, blank=True)
    it_details = models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    certifications = JSONField(default=list, blank=True)
    recruiting = models.BooleanField(default=False)
    
    # Enable flags for profile fields
    experience_enabled = models.BooleanField(default=True)
    urls_enabled = models.BooleanField(default=True)
    certifications_enabled = models.BooleanField(default=True)
    resume_enabled = models.BooleanField(default=True)
    skills_enabled = models.BooleanField(default=True)
    languages_enabled = models.BooleanField(default=True)
    currently_enabled = models.BooleanField(default=True)
    job_preference_enabled = models.BooleanField(default=True)
    it_details_enabled = models.BooleanField(default=True)
    
    # Website URLs for individual users and companies
    website_urls = JSONField(default=list, blank=True)
    # Posted works for companies
    posted_works = JSONField(default=list, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class ProfileSkill(models.Model):
    PROFICIENCY = (
        ("beg", "Beginner"),
        ("inter", "Intermediate"),
        ("expert", "Expert"),
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=10, choices=PROFICIENCY, default="beg")

    class Meta:
        unique_together = ("profile", "skill")

    def __str__(self):
        return f"{self.profile.user.username} - {self.skill.name} ({self.proficiency})"


class ProfileLanguage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    speak = models.BooleanField(default=False)
    proficiency = models.CharField(max_length=10, choices=ProfileSkill.PROFICIENCY, default="beg")

    class Meta:
        unique_together = ("profile", "language")

    def __str__(self):
        flags = []
        if self.read:
            flags.append("R")
        if self.write:
            flags.append("W")
        if self.speak:
            flags.append("S")
        return f"{self.profile.user.username} - {self.language.name} [{','.join(flags)}]"


# auto-create Profile when an Account is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Exception:
        # profile may not exist yet
        pass


# --- Job Posting Models ---
class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    )

    posted_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='jobs_posted')
    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=255, null=True, blank=True)
    max_members = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.role} at {self.company_name}"


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applied_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='job_applications')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('job', 'applied_by')

    def __str__(self):
        return f"{self.applied_by.username} applied for {self.job.role}"


# --- Connection/Network Models ---
class Connection(models.Model):
    from_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='connections_sent')
    to_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='connections_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} connected with {self.to_user.username}"


# --- Messaging Models ---
class Message(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='messages_received')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


# --- Notifications ---
class Notification(models.Model):
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    verb = models.CharField(max_length=255)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.verb}"
