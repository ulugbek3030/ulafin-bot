"""Main menu Reply keyboard — persistent bottom buttons."""

from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_EXPENSE = "🔴 Расход"
BTN_INCOME = "🟢 Приход"
BTN_REPORT = "📊 Отчёты"
BTN_SETTINGS = "⚙️ Настройки"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_EXPENSE), KeyboardButton(text=BTN_INCOME)],
        [KeyboardButton(text=BTN_REPORT), KeyboardButton(text=BTN_SETTINGS)],
    ],
    resize_keyboard=True,
)
