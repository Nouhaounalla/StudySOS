from django.urls import path
from . import views
from .auth_views import (
    CookieTokenObtainPairView, 
    CookieTokenRefreshView, 
    LogoutView,
    LogoutAllDevicesView
)

urlpatterns = [
    path('', views.register_login_page, name='register-login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile-page/', views.profile_page, name='profile-page'),
    path('profile_info/', views.profile_info_page, name='profile_info'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllDevicesView.as_view(), name='logout-all'),
    path('upload-photo/', views.ProfilePhotoUploadView.as_view(), name='upload-photo'),
    path('upload-cover/', views.CoverPhotoUploadView.as_view(), name='upload-cover'),
]