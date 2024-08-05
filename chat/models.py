# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)  # For text messages
    audio_url = models.URLField(blank=True, null=True)  # For audio messages
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    def mark_as_delivered(self):
        if self.status == 'sent':
            self.status = 'delivered'
            self.save()

    def mark_as_read(self):
        if self.status in ['sent', 'delivered']:
            self.status = 'read'
            self.save()
    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.content}"
    