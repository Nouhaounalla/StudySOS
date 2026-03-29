from django.urls import path
from .views import RegisterView, ProfileView, ChangePasswordView, register_page, profile_page

urlpatterns = [
    path('', register_page, name='register-page'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),           # GET + POST (own profile)
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile-page/', profile_page, name='profile-page'),
]
