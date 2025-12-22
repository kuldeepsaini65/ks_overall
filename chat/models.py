from django.db import models
from homecontrol.models import LogFolder
from django.contrib.auth.models import User
import hashlib



class Conversation(LogFolder):
    users = models.ManyToManyField(User,related_name='conversations_user')
    is_group = models.BooleanField(default=False, db_index=True)
    group_name = models.CharField(max_length=150, null=True, blank=True)
    group_image = models.ImageField(upload_to='chat/groups/', null=True, blank=True)
    unique_hash = models.CharField(max_length=64, unique=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group:
            return f'Group: {self.group_name}'
        
    def save(self, *args, **kwargs):
        if not self.is_group and not self.unique_hash:
            super().save(*args, **kwargs)
            self.generate_private_hash()
            # return

        super().save(*args, **kwargs)

    def generate_private_hash(self):
        users = list(self.users.values_list('id', flat=True))

        if len(users) == 2:
            users.sort()
            raw_string = f"{users[0]}_{users[1]}"
            self.unique_hash = hashlib.sha256(raw_string.encode()).hexdigest()
            super().save(update_fields=['unique_hash'])
        
        return f'Chat: {", ".join([u.username for u in self.users.all()])}'



class Chats(LogFolder):
    chat_conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages_conversation',db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user_sender', db_index=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user_reveiver', db_index=True)

    chat = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} → {self.receiver} at {self.created_at}'

