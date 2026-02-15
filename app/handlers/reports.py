"""Report handlers — text reports + chart placeholders."""

from __future__ import annotations

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.common import report_type_keyboard
from app.models.user import User
from app.services.report_service import ReportService

router = Router()


@router.message(Command("report"))
async def cmd_report(
    message: Message,
    user: User,
    session: AsyncSession,
    **kwargs,
) -> None:
    """Show monthly report — offers text / chart options."""
    now = datetime.now()

    report_service = ReportService(session)
    text = await report_service.build_monthly_text_report(
        user_id=user.id,
        year=now.year,
        month=now.month,
        currency=user.default_currency,
        lang=user.language,
    )

    await message.answer(text, reply_markup=report_type_keyboard())


@router.callback_query(lambda c: c.data and c.data.startswith("report:"))
async def on_report_type(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
) -> None:
    """Handle report type selection."""
    report_type = callback.data.split(":", 1)[1]
    now = datetime.now()

    if report_type == "text":
        report_service = ReportService(session)
        text = await report_service.build_monthly_text_report(
            user_id=user.id,
            year=now.year,
            month=now.month,
            currency=user.default_currency,
            lang=user.language,
        )
        await callback.message.edit_text(text, reply_markup=report_type_keyboard())
        await callback.answer()
    elif report_type in ("pie", "bar", "trend"):
        # TODO: Phase 7 — chart generation with matplotlib
        await callback.answer(
            f"📊 Графики ({report_type}) будут в следующем обновлении!",
            show_alert=True,
        )
    else:
        await callback.answer("Неизвестный тип отчёта.", show_alert=True)
