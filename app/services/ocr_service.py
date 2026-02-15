"""OCR service — extract financial data from screenshots."""

from __future__ import annotations

import os
import tempfile

from aiogram import Bot

from app.utils.ocr import OCRResult, extract_amount_from_image


class OCRService:
    """Service for processing bank app screenshots."""

    @staticmethod
    async def process_photo(bot: Bot, photo_file_id: str) -> OCRResult | None:
        """Download photo from Telegram and run OCR.

        Args:
            bot: The aiogram Bot instance.
            photo_file_id: Telegram file_id of the photo.

        Returns:
            OCRResult or None if recognition failed.
        """
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            await bot.download(photo_file_id, destination=tmp_path)
            return extract_amount_from_image(tmp_path)
        except Exception:
            return None
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
