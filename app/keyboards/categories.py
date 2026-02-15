"""Category selection inline keyboard."""

from __future__ import annotations

from typing import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.category import Category


def build_category_keyboard(categories: Sequence[Category]) -> InlineKeyboardMarkup:
    """Build inline keyboard with categories in 2-column grid + 'New category' button.

    Args:
        categories: List of Category objects.

    Returns:
        InlineKeyboardMarkup with category buttons.
    """
    buttons: list[list[InlineKeyboardButton]] = []
    items = list(categories)

    for i in range(0, len(items), 2):
        row = []
        for cat in items[i : i + 2]:
            row.append(
                InlineKeyboardButton(
                    text=cat.label,
                    callback_data=f"cat:{cat.id}",
                )
            )
        buttons.append(row)

    # Add "New category" button at the bottom
    buttons.append(
        [InlineKeyboardButton(text="➕ Новая категория", callback_data="newcat")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
