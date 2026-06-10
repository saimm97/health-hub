"""Forms for the server-rendered accounts pages."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

_INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none"
)


class RegistrationForm(UserCreationForm):
    """Email-based registration (the custom user has no username)."""

    class Meta:
        model = User
        fields = ["email", "full_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", _INPUT)
