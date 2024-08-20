from django.contrib import admin
from chat.models import Message, MessageFile



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sender', 'receiver',
        'chat_id', 'reply_id', 'is_read', 
        'created_at', 'updated_at',
        'text',
    )
    list_editable = (
        'sender', 'receiver',
        'chat_id', 'reply_id', 
        'is_read', 'text',
    )

admin.site.register(MessageFile)
