from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models


today = timezone.now()

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_messages')
    text = models.CharField(max_length=1000, null=True, blank=True)
    chat_id = models.PositiveSmallIntegerField(null=True, blank=True)
    reply_id = models.ForeignKey('self', on_delete=models.SET_NULL,
                                related_name='reply_messages', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField('Created date', auto_now_add=True)
    updated_at = models.DateTimeField('Updated date', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def save(self, *args, **kwargs):
        if self.is_read:
            self.read_time = today
        return super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class MessageFile(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='msg_files', null=True, blank=True)
    file = models.FileField(upload_to='chat/files/')

    created_at = models.DateTimeField('Created date', auto_now_add=True) 
    updated_at = models.DateTimeField('Created At', auto_now=True)

    def __str__(self):
        return f"{self.id} {self.message}"

    class Meta:
        verbose_name = 'Message file'
        verbose_name_plural = 'Message files'
