from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterSerializer, JobSerializer, JobApplicationSerializer
from .serializers import SkillSerializer, LanguageSerializer, ProfileSerializer
from .serializers import ConnectionSerializer, MessageSerializer, NotificationSerializer
from .models import Skill, Language, Profile, ProfileSkill, ProfileLanguage, Job, JobApplication, Account
from .models import Connection, Message, Notification
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db import models


class SkillListView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)


class LanguageListView(APIView):
    def get(self, request):
        langs = Language.objects.all()
        serializer = LanguageSerializer(langs, many=True)
        return Response(serializer.data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        # If user_id is provided, get that user's profile; otherwise get current user's profile
        if user_id:
            try:
                target_user = Account.objects.get(id=user_id)
            except Account.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            target_user = request.user

        profile, _ = Profile.objects.get_or_create(user=target_user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, user_id=None):
        # Only allow editing your own profile
        if user_id and user_id != request.user.id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        profile, _ = Profile.objects.get_or_create(user=request.user)

        # handle simple fields
        profile.description = request.data.get('description', profile.description)
        profile.currently = request.data.get('currently', profile.currently)
        profile.job_preference = request.data.get('job_preference', profile.job_preference)
        profile.experience = request.data.get('experience', profile.experience)
        profile.it_details = request.data.get('it_details', profile.it_details)
        recruiting = request.data.get('recruiting')
        if recruiting is not None:
            # accept 'true'/'false' strings too
            profile.recruiting = str(recruiting).lower() in ('1', 'true', 'yes')

        # handle enable flags
        profile.experience_enabled = str(request.data.get('experience_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.urls_enabled = str(request.data.get('urls_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.certifications_enabled = str(request.data.get('certifications_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.resume_enabled = str(request.data.get('resume_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.skills_enabled = str(request.data.get('skills_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.languages_enabled = str(request.data.get('languages_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.currently_enabled = str(request.data.get('currently_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.job_preference_enabled = str(request.data.get('job_preference_enabled', 'true')).lower() in ('1', 'true', 'yes')
        profile.it_details_enabled = str(request.data.get('it_details_enabled', 'true')).lower() in ('1', 'true', 'yes')

        # files
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'resume' in request.FILES:
            profile.resume = request.FILES['resume']

        # handle certifications (multiple file uploads as certification_0, certification_1, etc)
        certifications_urls = []
        i = 0
        while f'certification_{i}' in request.FILES:
            cert_file = request.FILES[f'certification_{i}']
            # Save the file to the profile
            from django.core.files.storage import default_storage
            from django.utils.text import slugify
            import time
            filename = f"certifications/{request.user.id}_{time.time()}_{cert_file.name}"
            path = default_storage.save(filename, cert_file)
            certifications_urls.append(path)
            i += 1
        
        # Update certifications list if new ones were uploaded
        if certifications_urls:
            profile.certifications = certifications_urls

        # handle website URLs (JSON)
        import json
        urls_raw = request.data.get('website_urls')
        if urls_raw:
            try:
                profile.website_urls = json.loads(urls_raw)
            except Exception:
                profile.website_urls = []

        # handle posted works (JSON)
        works_raw = request.data.get('posted_works')
        if works_raw:
            try:
                profile.posted_works = json.loads(works_raw)
            except Exception:
                profile.posted_works = []

        profile.save()

        # skills: expect JSON list of ids OR list of objects with id and proficiency
        skills_raw = request.data.get('skills')
        if skills_raw:
            try:
                skills_list = json.loads(skills_raw)
            except Exception:
                skills_list = []

            # normalize to list of dicts {id, proficiency}
            normalized = []
            for item in skills_list:
                if isinstance(item, dict):
                    sid = item.get('id')
                    prof = item.get('proficiency') or 'beg'
                else:
                    sid = item
                    prof = 'beg'
                if sid:
                    normalized.append({'id': sid, 'proficiency': prof})

            # clear existing
            ProfileSkill.objects.filter(profile=profile).delete()
            for it in normalized:
                try:
                    s = Skill.objects.get(pk=it['id'])
                    ProfileSkill.objects.create(profile=profile, skill=s, proficiency=it.get('proficiency', 'beg'))
                except Skill.DoesNotExist:
                    continue

        # languages: expect JSON list of objects {id, read, write, speak}
        langs_raw = request.data.get('languages')
        if langs_raw:
            try:
                langs_list = json.loads(langs_raw)
            except Exception:
                langs_list = []

            ProfileLanguage.objects.filter(profile=profile).delete()
            for it in langs_list:
                lid = it.get('id') if isinstance(it, dict) else it
                try:
                    lang = Language.objects.get(pk=lid)
                    read = bool(it.get('read')) if isinstance(it, dict) else False
                    write = bool(it.get('write')) if isinstance(it, dict) else False
                    speak = bool(it.get('speak')) if isinstance(it, dict) else False
                    proficiency = it.get('proficiency') if isinstance(it, dict) else 'beg'
                    ProfileLanguage.objects.create(profile=profile, language=lang, read=read, write=write, speak=speak, proficiency=proficiency)
                except Language.DoesNotExist:
                    continue

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=201)
        return Response(serializer.errors, status=400)


class JobListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')
        serializer = JobSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Only companies can post jobs
        if request.user.role != 'company':
            return Response({"error": "Only companies can post jobs"}, status=403)

        data = request.data.copy()
        data['posted_by'] = request.user.id
        serializer = JobSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        serializer = JobSerializer(job, context={'request': request})
        return Response(serializer.data)


class JobApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        # Check if user already applied
        existing = JobApplication.objects.filter(job=job, applied_by=request.user).exists()
        if existing:
            return Response({"error": "You have already applied for this job"}, status=400)

        # Create application
        application = JobApplication.objects.create(job=job, applied_by=request.user)

        # Create notification for the job poster
        try:
            if job.posted_by != request.user:
                Notification.objects.create(
                    recipient=job.posted_by,
                    actor=request.user,
                    verb=f"{request.user.username} applied for your job '{job.role}'",
                    job=job
                )
        except Exception:
            # don't fail application if notification fails
            pass

        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=201)

    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        try:
            application = JobApplication.objects.get(job=job, applied_by=request.user)
            application.delete()
            return Response({"message": "Application withdrawn"}, status=200)
        except JobApplication.DoesNotExist:
            return Response({"error": "No application found"}, status=404)


class JobApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        # Only job poster can view applicants
        if job.posted_by != request.user:
            return Response({"error": "You can only view applicants for your own jobs"}, status=403)

        applications = job.applications.all()
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class UserSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('search', '').strip()
        if not query or len(query) < 2:
            return Response([])

        # Search by username (case-insensitive partial match)
        from django.db.models import Q
        users = Account.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id if request.user.is_authenticated else None)[:20]

        results = []
        for user in users:
            profile = Profile.objects.filter(user=user).first()
            results.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'company_name': user.company_name,
                'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None,
                'description': profile.description if profile else None,
            })
        return Response(results)


class JobSearchFilterView(APIView):
    def get(self, request):
        jobs = Job.objects.all()

        # Filter by role/title
        role_query = request.query_params.get('role', '').strip()
        if role_query:
            jobs = jobs.filter(role__icontains=role_query)

        # Filter by location
        location_query = request.query_params.get('location', '').strip()
        if location_query:
            jobs = jobs.filter(location__icontains=location_query)

        # Filter by job type
        job_type = request.query_params.get('job_type', '').strip()
        if job_type:
            jobs = jobs.filter(job_type=job_type)

        # Filter by salary (range: min_salary to max_salary)
        # Note: We're storing salary as text, so filtering is limited
        # For proper implementation, consider storing min_salary and max_salary as separate fields

        # Sort by newest first
        jobs = jobs.order_by('-created_at')

        serializer = JobSerializer(jobs[:50], many=True, context={'request': request})
        return Response(serializer.data)


# --- Connection/Network Views ---
class ConnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a connection to another user"""
        to_user_id = request.data.get('to_user_id')
        
        if not to_user_id:
            return Response({"error": "to_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = Account.objects.get(id=to_user_id)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if to_user_id == request.user.id:
            return Response({"error": "Cannot connect to yourself"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if connection already exists
        connection, created = Connection.objects.get_or_create(
            from_user=request.user,
            to_user=to_user
        )

        if created:
            serializer = ConnectionSerializer(connection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Connection already exists"}, status=status.HTTP_200_OK)

    def get(self, request):
        """Get all connections for current user"""
        connections = Connection.objects.filter(from_user=request.user)
        serializer = ConnectionSerializer(connections, many=True)
        return Response(serializer.data)

    def delete(self, request):
        """Remove a connection"""
        to_user_id = request.data.get('to_user_id')
        
        if not to_user_id:
            return Response({"error": "to_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            connection = Connection.objects.get(from_user=request.user, to_user_id=to_user_id)
            connection.delete()
            return Response({"message": "Connection removed"}, status=status.HTTP_200_OK)
        except Connection.DoesNotExist:
            return Response({"error": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)


# --- Messaging Views ---
class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Send a message to another user"""
        to_user_id = request.data.get('to_user_id')
        content = request.data.get('content')

        if not to_user_id or not content:
            return Response({"error": "to_user_id and content are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = Account.objects.get(id=to_user_id)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            sender=request.user,
            recipient=to_user,
            content=content
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Get messages with a specific user"""
        other_user_id = request.query_params.get('user_id')

        if not other_user_id:
            # Get list of all users we've messaged
            users_messaged = Account.objects.filter(
                messages_received__sender=request.user
            ).distinct() | Account.objects.filter(
                messages_sent__recipient=request.user
            ).distinct()

            return Response([{
                'id': user.id,
                'username': user.username,
                'email': user.email,
            } for user in users_messaged])

        try:
            other_user = Account.objects.get(id=other_user_id)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get messages between current user and other user
        messages = Message.objects.filter(
            (models.Q(sender=request.user, recipient=other_user) |
             models.Q(sender=other_user, recipient=request.user))
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class ApproveApplicantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id, application_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        # Only poster can approve
        if job.posted_by != request.user:
            return Response({"error": "You can only approve applicants for your own jobs"}, status=403)

        try:
            application = JobApplication.objects.get(id=application_id, job=job)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)

        if application.approved:
            return Response({"message": "Applicant already approved"}, status=200)

        application.approved = True
        application.approved_at = timezone.now()
        application.save()

        # Notify the applicant
        try:
            Notification.objects.create(
                recipient=application.applied_by,
                actor=request.user,
                verb=f"Your application for '{job.role}' was approved",
                job=job
            )
        except Exception:
            pass

        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:100]
        serializer = NotificationSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Mark notification(s) as read. Accepts {'id': <id>} or {'mark_all': true}
        nid = request.data.get('id')
        mark_all = request.data.get('mark_all')

        if mark_all:
            Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
            return Response({"message": "All notifications marked read"})

        if not nid:
            return Response({"error": "id or mark_all required"}, status=400)

        try:
            note = Notification.objects.get(id=nid, recipient=request.user)
            note.is_read = True
            note.save()
            return Response({"message": "Notification marked read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)
