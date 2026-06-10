from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.coach.models import Conversation, Message
from apps.coach.services import send_message

from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)


class ConversationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Manage the caller's coaching conversations and post messages to them."""

    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        data = MessageSerializer(conversation.messages.all(), many=True).data
        return Response(data)

    @action(detail=True, methods=["post"], serializer_class=SendMessageSerializer)
    def send(self, request, pk=None):
        """Post a user turn; returns the assistant's (possibly guarded) reply."""
        conversation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply: Message = send_message(
            user=request.user,
            conversation=conversation,
            text=serializer.validated_data["text"],
        )
        return Response(MessageSerializer(reply).data)
