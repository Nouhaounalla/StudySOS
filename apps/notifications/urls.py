from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_notifications, name='api-notifications'),
    path('unread-count/', views.unread_count, name='api-notifications-count'),
    path('mark-all-read/', views.mark_all_read, name='api-notifications-mark-all'),
    path('<int:pk>/read/', views.mark_read, name='api-notification-read'),
]
