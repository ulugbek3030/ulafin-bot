"""Settings handlers — language, currency, timezone."""

from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.settings import (
    currency_keyboard,
    language_keyboard,
    settings_menu_keyboard,
)
from app.models.user import User
from app.services.user_service import UserService

router = Router()


@router.callback_query(lambda c: c.data == "settings:lang")
async def on_language_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🌐 Выбери язык / Tilni tanlang / Choose language:",
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:currency")
async def on_currency_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "💱 Выбери валюту по умолчанию:",
        reply_markup=currency_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:tz")
async def on_timezone_settings(callback: CallbackQuery) -> None:
    # Simplified — just show current and allow common ones
    await callback.answer(
        "🕐 Часовой пояс — Asia/Tashkent (UTC+5). "
        "Чтобы изменить, напишите: /timezone <zone>",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "settings:back")
async def on_settings_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>",
        reply_markup=settings_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def on_language_chosen(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
) -> None:
    lang = callback.data.split(":", 1)[1]
    service = UserService(session)
    await service.update_language(user.id, lang)

    labels = {"ru": "🇷🇺 Русский", "uz": "🇺🇿 O'zbek", "en": "🇬🇧 English"}
    await callback.message.edit_text(
        f"✅ Язык изменён на <b>{labels.get(lang, lang)}</b>",
        reply_markup=settings_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("cur:"))
async def on_currency_chosen(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
) -> None:
    currency = callback.data.split(":", 1)[1]
    service = UserService(session)
    await service.update_currency(user.id, currency)

    await callback.message.edit_text(
        f"✅ Валюта по умолчанию: <b>{currency}</b>",
        reply_markup=settings_menu_keyboard(),
    )
    await callback.answer()
