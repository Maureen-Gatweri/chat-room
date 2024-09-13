# from django.db import models
# from django.contrib.auth.models import User
# from django.conf import settings


# class ChatRoom(models.Model):
#     name = models.CharField(max_length=255)
#     users = models.ManyToManyField(User, related_name='chat_rooms')
#     def __str__(self):
#         return self.name
# class ChatMessage(models.Model):
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return f"{self.user.username}: {self.message}"

# class Invitation(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=20)
#     invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)  

#     def __str__(self):  

#       return f"Invitation for {self.first_name} {self.last_name}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='chat_rooms')

class Invitation(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)