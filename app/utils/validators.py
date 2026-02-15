"""Pydantic validation models for incoming data."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseInput(BaseModel):
    """Validated expense/income input."""

    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    description: str = Field(max_length=500, default="Без описания")
    currency: str | None = Field(default=None, max_length=3)
    source: str = Field(default="text", max_length=20)
    entry_type: str = Field(default="expense", pattern="^(expense|income)$")


class CategoryInput(BaseModel):
    """Validated category name input."""

    name: str = Field(min_length=1, max_length=40)


class SettingsInput(BaseModel):
    """Validated user settings update."""

    language: str | None = Field(default=None, pattern="^(ru|uz|en)$")
    default_currency: str | None = Field(default=None, max_length=3)
    timezone: str | None = Field(default=None, max_length=50)
