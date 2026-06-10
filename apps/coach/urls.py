from __future__ import annotations

from django.urls import path

from .views import CoachHomeView, SendMessageView

app_name = "coach"

urlpatterns = [
    path("", CoachHomeView.as_view(), name="home"),
    path("<int:pk>/send/", SendMessageView.as_view(), name="send"),
]
