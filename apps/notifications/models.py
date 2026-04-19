from django.db import models
from apps.users.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_answer', 'Nouvelle réponse'),
        ('answer_accepted', 'Réponse acceptée'),
        ('session_request', 'Demande de session'),
        ('session_update', 'Mise à jour session'),
        ('new_message', 'Nouveau message'),
        ('general', 'Général'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    reference_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notif → {self.recipient.username}: {self.message[:50]}'
