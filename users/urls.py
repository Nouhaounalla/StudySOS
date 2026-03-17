from django.urls import path
from .views import RegisterView, ProfileView, register_page, profile_page

urlpatterns = [
    path('', register_page, name='register-page'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('profile-page/', profile_page, name='profile-page'),
]