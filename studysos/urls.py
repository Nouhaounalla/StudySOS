from django.contrib import admin
from django.urls import path, include
from users.views import home
from users.views import profile_page

urlpatterns = [
    path('', home),  
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('profile/', profile_page),
]