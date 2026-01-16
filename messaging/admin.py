from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'contact_revealed', 'created_at']
    list_filter = ['contact_revealed', 'created_at']
    search_fields = ['participant1__username', 'participant2__username']
    raw_id_fields = ['participant1', 'participant2', 'booking']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['conversation', 'sender']
    date_hierarchy = 'created_at'
