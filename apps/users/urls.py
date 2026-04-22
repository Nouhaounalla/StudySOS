from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='api-register'),
    path('login/', views.login, name='api-login'),
    path('logout/', views.logout, name='api-logout'),
    path('profile/', views.profile, name='api-profile'),
    path('upload-photo/', views.upload_profile_photo, name='api-upload-photo'),
    path('upload-cover/', views.upload_cover_photo, name='api-upload-cover'),
    path('change-password/', views.change_password, name='api-change-password'),
    path("delete/", views.delete_account, name="delete_account"),
    path('tutors/', views.list_tutors, name='api-tutors'),
    path('profile/<str:username>/', views.public_profile, name='api-public-profile'),
]
