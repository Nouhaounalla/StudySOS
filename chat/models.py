from django.db import models
from users.models import User

class Message(models.Model):
    room_name = models.CharField(max_length=100, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room_name', 'created_at']),
        ]