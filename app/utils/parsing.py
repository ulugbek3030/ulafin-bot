"""Text parsing utilities — extracted from old handlers/add_expense.py.

Parses user text like "50000 обед в кафе" or "$100 lunch" into amount + description.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class ParsedExpense:
    """Result of parsing expense text."""

    amount: Decimal
    description: str
    currency: str | None = None  # None means user's default currency


# Currency symbols and prefixes → ISO code
CURRENCY_PATTERNS: dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₽": "RUB",
    "₸": "KZT",
}

# Regex patterns for amount with optional currency
# Matches: 50000, $100, 100€, 1 000 000, 50000.50, $1,000.50
_AMOUNT_RE = re.compile(
    r"^"
    r"(?P<pre_symbol>[€$£₽₸])?\s*"  # Optional currency symbol before
    r"(?P<amount>[\d][\d\s]*[.,]?\d*)"  # Amount with spaces/commas
    r"\s*(?P<post_symbol>[€$£₽₸сумsomsumруб]*)?"  # Optional currency after
    r"\s*(?P<desc>.*)",  # Description
    re.IGNORECASE,
)


def parse_expense_text(text: str) -> ParsedExpense | None:
    """Parse text like '50000 обед в кафе' or '$100 lunch' into structured data.

    Returns:
        ParsedExpense or None if text cannot be parsed.
    """
    text = text.strip()
    if not text:
        return None

    match = _AMOUNT_RE.match(text)
    if not match:
        return None

    amount_str = match.group("amount").replace(" ", "").replace(",", ".")
    try:
        amount = Decimal(amount_str)
    except (InvalidOperation, ValueError):
        return None

    if amount <= 0:
        return None

    description = (match.group("desc") or "").strip() or "Без описания"

    # Detect currency
    currency: str | None = None
    pre_sym = match.group("pre_symbol") or ""
    post_sym = (match.group("post_symbol") or "").lower()

    if pre_sym in CURRENCY_PATTERNS:
        currency = CURRENCY_PATTERNS[pre_sym]
    elif post_sym:
        for sym, code in CURRENCY_PATTERNS.items():
            if sym in post_sym:
                currency = code
                break
        if post_sym in ("руб", "rub"):
            currency = "RUB"
        elif post_sym in ("сум", "sum", "som"):
            currency = "UZS"

    return ParsedExpense(
        amount=amount,
        description=description,
        currency=currency,
    )
