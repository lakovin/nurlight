from delivery.models import FAQ


async def get_faq_questions(language: str = "ru") -> list[dict]:
    """Получить вопросы FAQ из базы Django."""

    questions = FAQ.objects.filter(
        language=language
    ).order_by("id")

    return [
        {
            "id": item.id,
            "question": item.question,
        }
        async for item in questions
    ]


async def get_faq_answer(
    faq_id: int,
    language: str = "ru",
) -> dict | None:
    """Получить ответ на выбранный вопрос."""

    item = await FAQ.objects.filter(
        id=faq_id,
        language=language,
    ).afirst()

    if item is None:
        return None

    return {
        "question": item.question,
        "answer": item.answer,
    }