"""Start & mode handlers — /start, registration, mode buttons."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.session_store import SessionStore
from app.keyboards.main_menu import (
    BTN_EXPENSE,
    BTN_INCOME,
    BTN_REPORT,
    BTN_SETTINGS,
    main_keyboard,
)
from app.models.user import User
from app.services.user_service import UserService

router = Router()

HELP_TEXT = """\
<b>UlaFin — Финансовый трекер</b>

<b>Кнопки:</b>
🔴 <b>Расход</b> — переключиться на ввод расходов
🟢 <b>Приход</b> — переключиться на ввод доходов
📊 <b>Отчёты</b> — отчёт за текущий месяц
⚙️ <b>Настройки</b> — язык, валюта, часовой пояс

<b>Как добавить запись:</b>
• Нажми кнопку (Расход/Приход) и напиши: <code>50000 обед</code>
• Или отправь скриншот (с подписью: <code>1000000 газ</code>)
• Мультивалютность: <code>$100 lunch</code>, <code>100€ ужин</code>
"""

# Keyboard for registration — share phone number
register_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(CommandStart())
async def cmd_start(
    message: Message, user: User, session_store: SessionStore
) -> None:
    if not user.is_registered:
        await message.answer(
            f"Привет, {user.first_name or 'друг'}! 👋\n\n"
            "Я <b>UlaFin</b> — твой личный финансовый трекер.\n\n"
            "Для начала пройди быструю регистрацию — нажми кнопку ниже, "
            "чтобы поделиться номером телефона:",
            reply_markup=register_keyboard,
        )
        return

    await session_store.set_mode(user.telegram_id, "expense")
    await message.answer(
        f"С возвращением, {user.first_name or 'друг'}! 👋\n\n" + HELP_TEXT,
        reply_markup=main_keyboard,
    )


@router.message(F.contact)
async def on_contact_shared(
    message: Message,
    user: User,
    session: AsyncSession,
    session_store: SessionStore,
) -> None:
    """User shared their phone number — complete registration."""
    contact = message.contact

    # Verify that user shared their OWN contact (not someone else's)
    if contact.user_id != message.from_user.id:
        await message.answer(
            "Нужно поделиться <b>своим</b> номером телефона. "
            "Нажми кнопку «📱 Поделиться номером».",
            reply_markup=register_keyboard,
        )
        return

    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    # Save phone and mark as registered
    service = UserService(session)
    await service.complete_registration(user.id, phone)

    await session_store.set_mode(user.telegram_id, "expense")
    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"📱 Номер: <b>{phone}</b>\n\n" + HELP_TEXT,
        reply_markup=main_keyboard,
    )


@router.message(Command("help"))
async def cmd_help(message: Message, user: User) -> None:
    if not user.is_registered:
        await message.answer(
            "Сначала пройди регистрацию — нажми /start",
            reply_markup=register_keyboard,
        )
        return
    await message.answer(HELP_TEXT, reply_markup=main_keyboard)


@router.message(F.text == BTN_EXPENSE)
async def on_expense_mode(
    message: Message, user: User, session_store: SessionStore
) -> None:
    await session_store.set_mode(user.telegram_id, "expense")
    await message.answer("🔴 Режим <b>расхода</b>. Напиши сумму и описание:")


@router.message(F.text == BTN_INCOME)
async def on_income_mode(
    message: Message, user: User, session_store: SessionStore
) -> None:
    await session_store.set_mode(user.telegram_id, "income")
    await message.answer("🟢 Режим <b>прихода</b>. Напиши сумму и описание:")


@router.message(F.text == BTN_REPORT)
async def on_report_button(message: Message, user: User, **kwargs) -> None:
    """Delegate to /report handler."""
    from app.handlers.reports import cmd_report

    await cmd_report(message, user=user, **kwargs)


@router.message(F.text == BTN_SETTINGS)
async def on_settings_button(message: Message) -> None:
    from app.keyboards.settings import settings_menu_keyboard

    await message.answer("⚙️ <b>Настройки</b>", reply_markup=settings_menu_keyboard())
