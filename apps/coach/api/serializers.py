from __future__ import annotations

from rest_framework import serializers

from apps.coach.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "was_blocked", "block_reason", "created"]
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created"]
        read_only_fields = ["id", "created"]


class SendMessageSerializer(serializers.Serializer):
    """Input for posting a turn to a conversation."""

    text = serializers.CharField(max_length=4000)
