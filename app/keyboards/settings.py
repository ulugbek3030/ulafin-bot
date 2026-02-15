"""Settings keyboards — language, currency, timezone selection."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    """Settings main menu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Язык", callback_data="settings:lang")],
            [InlineKeyboardButton(text="💱 Валюта", callback_data="settings:currency")],
            [InlineKeyboardButton(text="🕐 Часовой пояс", callback_data="settings:tz")],
        ]
    )


def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings:back")],
        ]
    )


def currency_keyboard() -> InlineKeyboardMarkup:
    """Default currency selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 UZS (сум)", callback_data="cur:UZS"),
                InlineKeyboardButton(text="🇺🇸 USD ($)", callback_data="cur:USD"),
            ],
            [
                InlineKeyboardButton(text="🇪🇺 EUR (€)", callback_data="cur:EUR"),
                InlineKeyboardButton(text="🇷🇺 RUB (₽)", callback_data="cur:RUB"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings:back")],
        ]
    )
