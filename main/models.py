from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages')
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{
            self.sender.username} → {self.receiver.username}: {self.text[:20]}'
