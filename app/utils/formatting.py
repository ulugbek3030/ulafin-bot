"""Formatting utilities for numbers, currencies, and dates."""

from __future__ import annotations

from decimal import Decimal


MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

MONTHS_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr",
}

MONTHS_EN = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

CURRENCY_SYMBOLS = {
    "UZS": "сум",
    "USD": "$",
    "EUR": "€",
    "RUB": "₽",
    "GBP": "£",
    "KZT": "₸",
}


def format_amount(amount: Decimal | float, currency: str = "UZS") -> str:
    """Format amount with thousand separators and currency symbol.

    Examples:
        format_amount(1000000, "UZS") → "1 000 000 сум"
        format_amount(100.50, "USD") → "$100.50"
    """
    if isinstance(amount, float):
        amount = Decimal(str(amount))

    symbol = CURRENCY_SYMBOLS.get(currency, currency)

    if currency in ("UZS", "KZT"):
        # No decimals for these currencies
        formatted = f"{int(amount):,}".replace(",", " ")
        return f"{formatted} {symbol}"
    else:
        # With decimals
        formatted = f"{amount:,.2f}".replace(",", " ")
        if currency == "USD":
            return f"${formatted}"
        elif currency == "EUR":
            return f"€{formatted}"
        elif currency == "GBP":
            return f"£{formatted}"
        elif currency == "RUB":
            return f"{formatted} ₽"
        else:
            return f"{formatted} {symbol}"


def format_amount_short(amount: Decimal | float) -> str:
    """Format amount with space separator, no currency.

    Example: 1000000 → "1 000 000"
    """
    if isinstance(amount, float):
        amount = Decimal(str(amount))
    return f"{int(amount):,}".replace(",", " ")


def get_month_name(month: int, lang: str = "ru") -> str:
    """Get localized month name."""
    months = {
        "ru": MONTHS_RU,
        "uz": MONTHS_UZ,
        "en": MONTHS_EN,
    }
    return months.get(lang, MONTHS_RU).get(month, str(month))
