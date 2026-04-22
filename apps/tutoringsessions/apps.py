# apps/tutoringsessions/apps.py
from django.apps import AppConfig

class TutoringsessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tutoringsessions'  # Updated path
    label = 'tutoringsessions'       # Unique label to avoid collision