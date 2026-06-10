"""
Prompt builder — grounds the LLM in the user's real data instead of letting it
invent context. Produces the system prompt and the message list sent to the
provider.
"""
from __future__ import annotations

from apps.accounts.models import User
from apps.fitness.services import weekly_summary

SYSTEM_PROMPT = """You are HealthHub Coach, a supportive fitness and wellness assistant.

Rules you must always follow:
- You give guidance on exercise, workout routines, general nutrition, sleep, and
  healthy habits only.
- You are NOT a doctor. Never diagnose conditions, interpret symptoms, or give
  medical, prescription, or emergency advice. If asked, tell the user to consult
  a doctor through HealthHub.
- Be concrete and encouraging. Prefer specific, actionable suggestions grounded
  in the user's data below.
- Keep answers concise.
"""


def build_user_context(user: User) -> str:
    """A compact, factual snapshot of the user for grounding."""
    profile = getattr(user, "profile", None)
    summary = weekly_summary(user=user)

    lines = ["Here is the current user's data:"]
    if profile is not None:
        lines += [
            f"- Age: {profile.age if profile.age is not None else 'unknown'}",
            f"- Sex: {profile.get_sex_display()}",
            f"- Activity level: {profile.get_activity_level_display()}",
            f"- Stated goal: {profile.goal or 'none provided'}",
        ]
    lines += [
        f"- Workouts in the last 7 days: {summary['workout_sessions']}",
        f"- Latest recorded weight (kg): {summary['latest_weight_kg'] or 'unknown'}",
    ]
    return "\n".join(lines)


def build_messages(user: User, history: list[dict], user_message: str) -> list[dict]:
    """Assemble the provider-agnostic message list.

    ``history`` is a list of ``{"role", "content"}`` dicts (prior turns).
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": build_user_context(user)})
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages
