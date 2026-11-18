"""AI-консультант на сайте: тот же агент, что в Telegram-боте (bot/services/ai_agent.py).

Сайт только передаёт вопрос и историю диалога из сессии посетителя. Логику, промпт и
модель ведёт Нурадыл в боте; когда агент переедет в общий модуль, поменяется импорт ниже.
"""
import sys
import time

from asgiref.sync import async_to_sync
from django.conf import settings

if str(settings.REPO_DIR) not in sys.path:
    sys.path.append(str(settings.REPO_DIR))

from bot.services.ai_agent import MAX_HISTORY_MESSAGES, ask_ai  # noqa: E402

HISTORY_KEY = "assistant_history"
RATE_KEY = "assistant_calls"
MAX_QUESTION = 1000
# Не больше 20 вопросов за 10 минут с одного браузера — чтобы не сжечь лимиты Gemini
RATE_LIMIT = 20
RATE_WINDOW = 600


def history(session) -> list[dict]:
    return session.get(HISTORY_KEY, [])


def clear(session):
    session[HISTORY_KEY] = []


def rate_limited(session) -> bool:
    now = time.time()
    calls = [t for t in session.get(RATE_KEY, []) if now - t < RATE_WINDOW]
    limited = len(calls) >= RATE_LIMIT
    if not limited:
        calls.append(now)
    session[RATE_KEY] = calls
    return limited


def ask(session, question: str) -> tuple[str, bool]:
    """Задать вопрос агенту; удачный ответ сохраняется в историю диалога."""
    past = history(session)
    answer, ok = async_to_sync(ask_ai)(question, past)
    if ok:
        past = past + [{"role": "user", "text": question}, {"role": "model", "text": answer}]
        session[HISTORY_KEY] = past[-MAX_HISTORY_MESSAGES:]
    return answer, ok
