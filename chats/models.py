import uuid
from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    session_id = models.UUIDField(default=uuid.uuid4)
    message = models.TextField()
    sender = models.CharField(max_length=50) # 'user' veya 'ai'
    created_at = models.DateTimeField(auto_now_add=True)