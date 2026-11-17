import asyncio
import logging
import os
import time

from google import genai
from google.genai import types

from delivery.models import Product


logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
AI_TIMEOUT = 20


async def ask_ai(question: str) -> str:
    """AI-консультант Nurlight с доступом к каталогу Django."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "⚠️ Gemini API-ключ не настроен."

    # Получаем актуальные товары из базы Django
    products = (
        Product.objects
        .filter(is_available=True)
        .order_by("id")[:50]
    )

    catalog = []

    async for product in products:
        catalog.append(
            f"{product.name} — {product.price:.0f} ₸"
        )

    catalog_text = "\n".join(catalog) or "Каталог пуст."

    instruction = f"""
Ты — AI-помощник службы доставки Nurlight Delivery.

Твои задачи:
1. Приветствовать клиентов.
2. Помогать выбирать товары из каталога.
3. Рекомендовать подходящие товары.
4. Объяснять процесс оформления заказа.
5. Отвечать на вопросы о доставке.

Актуальный каталог Nurlight:
{catalog_text}

Правила:
- Отвечай на языке клиента.
- Отвечай кратко: обычно 2–5 предложений.
- Не придумывай товары и цены.
- Используй только товары из каталога.
- Не обещай точное время доставки.
- Не утверждай, что заказ оформлен или оплачен.
- Для заказа предлагай использовать
  кнопки «Каталог» и «Корзина».
- Не выдавай себя за человека.
- Не используй Markdown-разметку.
- Приветствуй клиента только в начале разговора
  или если клиент сам поздоровался.
- Не начинай каждый ответ со слов
  «Здравствуйте», «Привет» или «Добрый день».
- Если клиент задаёт конкретный вопрос,
  сразу отвечай по существу.
- Не повторяй представление AI-помощника.
- Пиши естественно, как консультант магазина.
"""

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=18000,
            retry_options=types.HttpRetryOptions(
                attempts=1,
            ),
        ),
    )

    start_time = time.perf_counter()

    try:
        print("🤖 Gemini: отправляем запрос...", flush=True)

        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    temperature=0.3,
                    max_output_tokens=250,
                ),
            ),
            timeout=AI_TIMEOUT,
        )

        elapsed = time.perf_counter() - start_time

        print(
            f"✅ Gemini ответил за {elapsed:.2f} секунд",
            flush=True,
        )

        return (
            response.text
            or "Не удалось получить ответ. Попробуйте ещё раз."
        )

    except (asyncio.TimeoutError, TimeoutError):
        elapsed = time.perf_counter() - start_time

        logger.warning(
            "Gemini превысил время ожидания: %.2f секунд",
            elapsed,
        )

        return (
            "⏳ AI отвечает слишком долго. "
            "Пожалуйста, попробуйте ещё раз через некоторое время."
        )

    except Exception:
        logger.exception("Ошибка запроса Gemini API")

        return (
            "⚠️ Сейчас не удалось связаться с AI. "
            "Попробуйте позже."
        )

    finally:
        await client.aio.aclose()
