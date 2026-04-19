from django.urls import path
from . import template_views

urlpatterns = [
    path('', template_views.home, name='home'),
    path('auth/', template_views.auth_page, name='auth'),
    path('profile/complete/', template_views.profile_info, name='profile-info'),
    path('profile/', template_views.profile_page, name='profile'),
    path('profile/<str:username>/', template_views.public_profile_page, name='public-profile'),
    path('tutors/', template_views.tutors_page, name='tutors'),
]
