from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('tuteur', 'Tuteur'),
        ('admin', 'Administrateur'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    bio = models.TextField(blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='covers/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)

    # Tutor-specific
    subjects = models.JSONField(default=list, blank=True)  # list of subjects tutor teaches
    availability = models.JSONField(default=dict, blank=True)  # weekly availability slots

    # Stats (denormalized for performance)
    sessions_count = models.IntegerField(default=0)
    students_count = models.IntegerField(default=0)
    satisfaction_score = models.FloatField(default=0.0)
    experience_years = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.username} ({self.role})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username

    def get_initials(self):
        if self.first_name and self.last_name:
            return f'{self.first_name[0]}{self.last_name[0]}'.upper()
        return self.username[:2].upper()

    def profile_completion(self):
        fields = [self.first_name, self.last_name, self.bio, self.profile_photo,
                  self.date_of_birth, self.purpose, self.location]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
