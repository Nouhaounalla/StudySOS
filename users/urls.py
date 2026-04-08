from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    DeleteAccountView,
    register_page,
    profile_page
)

urlpatterns = [
    path('', register_page),
    path('register/', RegisterView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('delete-account/', DeleteAccountView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('profile-page/', profile_page),
]
