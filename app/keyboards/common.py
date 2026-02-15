"""Common reusable keyboard elements."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_cancel_keyboard(
    confirm_data: str = "confirm",
    cancel_data: str = "cancel",
) -> InlineKeyboardMarkup:
    """Simple Confirm / Cancel inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=confirm_data),
                InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_data),
            ]
        ]
    )


def back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Single 'Back' button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]
        ]
    )


def report_type_keyboard() -> InlineKeyboardMarkup:
    """Report format selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Текст", callback_data="report:text"),
                InlineKeyboardButton(text="🥧 Пирог", callback_data="report:pie"),
            ],
            [
                InlineKeyboardButton(text="📊 Столбцы", callback_data="report:bar"),
                InlineKeyboardButton(text="📈 Тренд", callback_data="report:trend"),
            ],
        ]
    )
