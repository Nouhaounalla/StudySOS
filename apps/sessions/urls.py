from django.urls import path
from . import views

urlpatterns = [
    path('', views.sessions_list, name='api-sessions'),
    path('<int:pk>/', views.session_detail, name='api-session-detail'),
    path('<int:pk>/review/', views.submit_review, name='api-session-review'),
]
