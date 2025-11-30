from rest_framework import serializers
from .models import Account

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'company_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        return Account.objects.create_user(password=password, **validated_data)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = getattr(user, 'role', None)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'role': getattr(self.user, 'role', None),
                'company_name': getattr(self.user, 'company_name', None),
            }
        })
        return data


from .models import Skill, Language, Profile, ProfileSkill, ProfileLanguage, Job, JobApplication, Connection, Message, Notification
from rest_framework import serializers


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']


class ProfileSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='skill.id', read_only=True)
    name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = ProfileSkill
        fields = ['id', 'name', 'proficiency']


class ProfileLanguageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='language.id', read_only=True)
    name = serializers.CharField(source='language.name', read_only=True)

    class Meta:
        model = ProfileLanguage
        fields = ['id', 'name', 'read', 'write', 'speak', 'proficiency']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    skills = ProfileSkillSerializer(source='profileskill_set', many=True, read_only=True)
    languages = ProfileLanguageSerializer(source='profilelanguage_set', many=True, read_only=True)
    applications = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'user', 'profile_picture', 'description', 'currently', 'skills', 'languages', 'job_preference',
            'experience', 'it_details', 'resume', 'certifications', 'recruiting',
            'experience_enabled', 'urls_enabled', 'certifications_enabled', 'resume_enabled',
            'skills_enabled', 'languages_enabled', 'currently_enabled', 'job_preference_enabled', 'it_details_enabled',
            'website_urls', 'posted_works', 'applications'
        ]

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'role': obj.user.role,
            'company_name': obj.user.company_name,
        }

    def get_applications(self, obj):
        # Get all job applications for this user
        applications = JobApplication.objects.filter(applied_by=obj.user)
        return JobApplicationSerializer(applications, many=True).data


class JobApplicationSerializer(serializers.ModelSerializer):
    applied_by = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    approved = serializers.BooleanField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'applied_by', 'created_at', 'approved', 'approved_at']

    def get_applied_by(self, obj):
        user = obj.applied_by
        profile = Profile.objects.filter(user=user).first()
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None,
            'description': profile.description if profile else None,
            'currently': profile.currently if profile else None,
            'experience': profile.experience if profile else None,
        }

    def get_job(self, obj):
        job = obj.job
        posted_by_user = job.posted_by
        return {
            'id': job.id,
            'posted_by': {
                'id': posted_by_user.id,
                'username': posted_by_user.username,
                'email': posted_by_user.email,
                'company_name': posted_by_user.company_name,
            },
            'company_name': job.company_name,
            'role': job.role,
            'description': job.description,
            'job_type': job.job_type,
            'location': job.location,
            'salary': job.salary,
            'max_members': job.max_members,
            'deadline': job.deadline,
            'created_at': job.created_at,
            'applications_count': job.applications.count(),
            'has_applied': True,
        }


class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField()
    applications = JobApplicationSerializer(many=True, read_only=True)
    applications_count = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'posted_by', 'company_name', 'role', 'description', 'job_type',
            'location', 'salary', 'max_members', 'deadline', 'created_at',
            'applications', 'applications_count', 'has_applied'
        ]

    def get_posted_by(self, obj):
        return {
            'id': obj.posted_by.id,
            'username': obj.posted_by.username,
            'email': obj.posted_by.email,
            'company_name': obj.posted_by.company_name,
        }

    def get_applications_count(self, obj):
        return obj.applications.count()

    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(applied_by=request.user).exists()
        return False


class ConnectionSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ['id', 'from_user', 'to_user', 'created_at']

    def get_from_user(self, obj):
        profile = Profile.objects.filter(user=obj.from_user).first()
        return {
            'id': obj.from_user.id,
            'username': obj.from_user.username,
            'email': obj.from_user.email,
            'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None,
            'description': profile.description if profile else None,
        }

    def get_to_user(self, obj):
        profile = Profile.objects.filter(user=obj.to_user).first()
        return {
            'id': obj.to_user.id,
            'username': obj.to_user.username,
            'email': obj.to_user.email,
            'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None,
            'description': profile.description if profile else None,
        }


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'created_at', 'is_read']

    def get_sender(self, obj):
        return {
            'id': obj.sender.id,
            'username': obj.sender.username,
            'email': obj.sender.email,
        }

    def get_recipient(self, obj):
        return {
            'id': obj.recipient.id,
            'username': obj.recipient.username,
            'email': obj.recipient.email,
        }


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'recipient', 'verb', 'job', 'is_read', 'created_at']

    def get_actor(self, obj):
        if not obj.actor:
            return None
        return {
            'id': obj.actor.id,
            'username': obj.actor.username,
            'email': obj.actor.email,
        }

    def get_recipient(self, obj):
        return {
            'id': obj.recipient.id,
            'username': obj.recipient.username,
            'email': obj.recipient.email,
        }

    def get_job(self, obj):
        if not obj.job:
            return None
        return {
            'id': obj.job.id,
            'role': obj.job.role,
            'company_name': obj.job.company_name,
        }
