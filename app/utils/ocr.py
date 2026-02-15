"""OCR utilities — extract amounts from bank app screenshots.

Copied from old ocr.py with minimal changes (Decimal instead of float).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import pytesseract
from PIL import Image


@dataclass
class OCRResult:
    """Result of OCR extraction."""

    amount: Decimal
    description: str
    raw_text: str


def extract_amount_from_image(image_path: str) -> OCRResult | None:
    """Extract amount and description from a bank app screenshot using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="rus+eng")
    except Exception:
        return None

    return parse_ocr_text(text)


def parse_ocr_text(text: str) -> OCRResult | None:
    """Parse OCR text to find amount and description."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    amount = _find_amount(text)
    if amount is None:
        return None

    description = _find_description(lines)

    return OCRResult(
        amount=amount,
        description=description,
        raw_text=text,
    )


def _find_amount(text: str) -> Decimal | None:
    """Find the most likely payment amount in OCR text."""
    patterns = [
        r"[-\u2212\u2013]\s*([\d\s]+[.,]\d{2})\b",
        r"(?:сумма|итого|всего|оплата|списан[оа]?|перевод)\s*:?\s*([\d\s]+[.,]?\d*)",
        r"([\d\s]+[.,]\d{2})\s*(?:сум|сўм|UZS|USD|руб|₽|\$)",
        r"([\d\s]+[.,]\d{2})",
    ]

    amounts: list[Decimal] = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = match.replace(" ", "").replace(",", ".")
            try:
                value = Decimal(cleaned)
                if value > 0:
                    amounts.append(value)
            except (InvalidOperation, ValueError):
                continue

    if not amounts:
        return None

    return max(amounts)


def _find_description(lines: list[str]) -> str:
    """Try to extract a meaningful description from OCR text."""
    skip_words = {"сумма", "итого", "баланс", "комиссия", "дата", "время", "номер"}

    for line in lines:
        lower = line.lower()
        if any(word in lower for word in skip_words):
            continue
        if re.match(r"^[\d\s.,:%+\-\u2212\u2013]+$", line):
            continue
        if len(line) > 3:
            return line[:100]

    return "Платёж (из скриншота)"
