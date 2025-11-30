from django.urls import path
from .views import (
    RegisterView, SkillListView, LanguageListView, ProfileView,
    JobListCreateView, JobDetailView, JobApplyView, JobApplicantsView,
    UserSearchView, JobSearchFilterView, ConnectionView, MessageView
)
from .views import ApproveApplicantView, NotificationsView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", CustomTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("profile/<int:user_id>/", ProfileView.as_view()),
    path("skills/", SkillListView.as_view()),
    path("languages/", LanguageListView.as_view()),
    path("jobs/", JobListCreateView.as_view()),
    path("jobs/<int:job_id>/", JobDetailView.as_view()),
    path("jobs/<int:job_id>/apply/", JobApplyView.as_view()),
    path("jobs/<int:job_id>/applicants/", JobApplicantsView.as_view()),
    path("jobs/<int:job_id>/applicants/<int:application_id>/approve/", ApproveApplicantView.as_view()),
    path("search/users/", UserSearchView.as_view()),
    path("search/jobs/", JobSearchFilterView.as_view()),
    path("connections/", ConnectionView.as_view()),
    path("messages/", MessageView.as_view()),
    path("notifications/", NotificationsView.as_view()),
]
