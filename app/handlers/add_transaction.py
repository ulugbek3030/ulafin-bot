"""Add transaction handlers — text and photo input."""

from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.session_store import SessionStore
from app.keyboards.categories import build_category_keyboard
from app.models.user import User
from app.services.category_service import CategoryService
from app.services.ocr_service import OCRService
from app.utils.formatting import format_amount_short
from app.utils.parsing import parse_expense_text

router = Router()

MODE_LABELS = {
    "expense": "🔴",
    "income": "🟢",
}


@router.message(F.photo)
async def handle_photo(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    session_store: SessionStore,
) -> None:
    """Handle screenshot from banking app. Supports caption as override."""
    mode = await session_store.get_mode(user.telegram_id)
    icon = MODE_LABELS[mode]

    # If photo has caption, try to parse it
    if message.caption:
        result = parse_expense_text(message.caption)
        if result:
            cat_service = CategoryService(session)
            categories = await cat_service.get_for_user(user.id)

            formatted = format_amount_short(result.amount)
            reply = await message.answer(
                f"{icon} 📷 <b>{formatted}</b> — {result.description}\n\nВыбери категорию:",
                reply_markup=build_category_keyboard(categories),
            )
            await session_store.set_pending(reply.message_id, {
                "amount": str(result.amount),
                "description": result.description,
                "currency": result.currency or user.default_currency,
                "source": "photo",
                "entry_type": mode,
            })
            return

    # Try OCR
    photo = message.photo[-1]
    ocr_result = await OCRService.process_photo(bot, photo.file_id)

    if ocr_result is None:
        await message.answer(
            "Не удалось распознать сумму на скриншоте.\n\n"
            "Отправь скриншот с подписью — сумма и описание:\n"
            "<code>1000000 газ</code>",
        )
        return

    cat_service = CategoryService(session)
    categories = await cat_service.get_for_user(user.id)

    formatted = format_amount_short(ocr_result.amount)
    reply = await message.answer(
        f"{icon} Распознано: <b>{formatted}</b> — {ocr_result.description}\n\nВыбери категорию:",
        reply_markup=build_category_keyboard(categories),
    )
    await session_store.set_pending(reply.message_id, {
        "amount": str(ocr_result.amount),
        "description": ocr_result.description,
        "currency": user.default_currency,
        "source": "photo",
        "entry_type": mode,
    })


@router.message(F.text)
async def handle_text(
    message: Message,
    user: User,
    session: AsyncSession,
    session_store: SessionStore,
) -> None:
    """Handle text expense like '50000 обед в кафе'."""
    if not message.text or message.text.startswith("/"):
        return

    # Skip if user is typing a new category name
    if await session_store.is_waiting_category(user.telegram_id):
        return

    result = parse_expense_text(message.text)
    if result is None:
        await message.answer(
            "Не понял. Напиши сумму и описание:\n<code>50000 обед в кафе</code>",
        )
        return

    mode = await session_store.get_mode(user.telegram_id)
    icon = MODE_LABELS[mode]

    cat_service = CategoryService(session)
    categories = await cat_service.get_for_user(user.id)

    formatted = format_amount_short(result.amount)
    reply = await message.answer(
        f"{icon} <b>{formatted}</b> — {result.description}\n\nВыбери категорию:",
        reply_markup=build_category_keyboard(categories),
    )
    await session_store.set_pending(reply.message_id, {
        "amount": str(result.amount),
        "description": result.description,
        "currency": result.currency or user.default_currency,
        "source": "text",
        "entry_type": mode,
    })
