from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin-dashboard'),
    path('users/', views.manage_users, name='admin-users'),
    path('users/<int:pk>/toggle/', views.toggle_user_active, name='admin-user-toggle'),
    path('users/<int:pk>/delete/', views.delete_user, name='admin-user-delete'),
    path('questions/', views.manage_questions, name='admin-questions'),
    path('questions/<int:pk>/delete/', views.delete_question, name='admin-question-delete'),
    path('reports/', views.manage_reports, name='admin-reports'),
    path('reports/<int:pk>/resolve/', views.resolve_report, name='admin-report-resolve'),
    path('tutoringsessions/', views.manage_tutoringsessions, name='admin-tutoringsessions'),
    path('statistics/', views.statistics, name='admin-statistics'),
]
