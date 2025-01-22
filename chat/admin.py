from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp')  # Display user, content, and timestamp
    search_fields = ('user__username', 'content')  # Allow search by username or message content
    list_filter = ('timestamp',)  # Filter messages by timestamp

admin.site.register(Message, MessageAdmin)
