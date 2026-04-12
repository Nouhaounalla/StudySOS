from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('etudiant', 'Étudiant'),
            ('tuteur', 'Tuteur')
        ],
        blank=True
    )
    purpose = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    cover_photo = models.ImageField(
    upload_to='covers/',
    blank=True,
    null=True
)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email