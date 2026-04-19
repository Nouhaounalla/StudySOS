from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/questions/', include('apps.questions.urls')),
    path('api/sessions/', include('apps.sessions.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    # Template views
    path('', include('apps.users.template_urls')),
    path('questions/', include('apps.questions.template_urls')),
    path('sessions/', include('apps.sessions.template_urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
