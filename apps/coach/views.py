"""
Server-rendered AI coach chat (Django + HTMX).

The page shows the conversation; the composer posts to ``send`` via HTMX, which
runs the same ``send_message`` service the API uses and returns just the new
message bubbles to append — no full-page reload.
"""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from .models import Conversation, Message
from .services import send_message, start_conversation


def _current_conversation(user) -> Conversation:
    convo = user.conversations.first()
    return convo or start_conversation(user=user, title="Coaching session")


class CoachHomeView(LoginRequiredMixin, View):
    def get(self, request):
        convo = _current_conversation(request.user)
        return render(
            request,
            "coach/home.html",
            {"conversation": convo, "messages": convo.messages.all()},
        )


class SendMessageView(LoginRequiredMixin, View):
    """HTMX endpoint: accept a turn, return the user + assistant bubbles."""

    def post(self, request, pk):
        convo = get_object_or_404(Conversation, pk=pk, user=request.user)
        text = (request.POST.get("text") or "").strip()
        if not text:
            return render(request, "coach/_turn.html", {"messages": []})

        reply = send_message(user=request.user, conversation=convo, text=text)
        # The user turn we just created is the one immediately before the reply.
        user_turn = (
            Message.objects.filter(conversation=convo, role=Message.Role.USER)
            .order_by("-created")
            .first()
        )
        return render(request, "coach/_turn.html", {"messages": [user_turn, reply]})
