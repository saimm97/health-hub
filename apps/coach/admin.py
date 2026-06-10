from __future__ import annotations

from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["role", "content", "was_blocked", "block_reason", "created"]
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "created"]
    search_fields = ["user__email", "title"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "role", "was_blocked", "created"]
    list_filter = ["role", "was_blocked"]
    search_fields = ["content"]
