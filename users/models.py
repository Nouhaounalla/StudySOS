from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator  # ← ajouter cette ligne en haut

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name  = models.CharField(max_length=100, blank=True)
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
    bio     = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.email


# ↓↓↓ TOUT CE QUI SUIT EST NOUVEAU — colle ici ↓↓↓

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réponse de {self.user} à {self.question}"


class RatingAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('answer', 'user')


class RatingTutor(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_ratings')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'student')


class UserSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    subject = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'subject')