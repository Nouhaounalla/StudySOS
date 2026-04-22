from django.db import models
from apps.users.models import User
from apps.questions.models import Subject


class Session(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_sessions')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='tutoringsessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tutoringsessions'
        ordering = ['-start_datetime']

    def __str__(self):
        return f'{self.student.username} → {self.tutor.username}: {self.title}'

    def duration_minutes(self):
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() / 60)


class Review(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'

    def __str__(self):
        return f'Review by {self.reviewer.username} → {self.reviewed.username}: {self.rating}/5'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update tutor satisfaction score
        from django.db.models import Avg
        avg = Review.objects.filter(reviewed=self.reviewed).aggregate(Avg('rating'))['rating__avg']
        if avg:
            self.reviewed.satisfaction_score = round(avg * 20, 1)  # convert to 0-100
            self.reviewed.save(update_fields=['satisfaction_score'])
