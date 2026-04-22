from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.questions.models import Subject

class Command(BaseCommand):
    help = 'Populate subjects'

    def handle(self, *args, **kwargs):
        subjects = [
            'Mathématiques', 'Physique', 'Chimie', 'Biologie',
            'Informatique', 'Français', 'Anglais', 'Histoire',
            'Géographie', 'Philosophie', 'Économie', 'Droit'
        ]
        
        for name in subjects:
            slug = slugify(name)
            Subject.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Subject.objects.count()} subjects'))