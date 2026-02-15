"""Category handlers — category selection and custom category creation."""

from __future__ import annotations

from decimal import Decimal

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.session_store import SessionStore
from app.models.user import User
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService
from app.utils.formatting import format_amount_short

router = Router()


@router.callback_query(lambda c: c.data == "newcat")
async def on_new_category(
    callback: CallbackQuery,
    user: User,
    session_store: SessionStore,
) -> None:
    """User wants to create a new category."""
    msg_id = callback.message.message_id
    expense_data = await session_store.pop_pending(msg_id)

    if expense_data is None:
        await callback.answer("Расход уже сохранён или устарел.", show_alert=True)
        return

    # Store data in waiting state
    await session_store.set_waiting_category(user.telegram_id, {
        **expense_data,
        "expense_msg_id": msg_id,
    })

    await callback.message.edit_text(
        "Напиши название новой категории (например: <i>Продукты</i>, <i>Спорт</i>):",
    )
    await callback.answer()


@router.message(lambda m: True)  # This is filtered by priority — see register order
async def on_new_category_name(
    message: Message,
    user: User,
    session: AsyncSession,
    session_store: SessionStore,
) -> None:
    """User typed the name for a new category. Called when is_waiting_category."""
    if not await session_store.is_waiting_category(user.telegram_id):
        return  # Not waiting for category name — skip

    data = await session_store.pop_waiting_category(user.telegram_id)
    if data is None:
        return

    name = (message.text or "").strip()
    if not name or len(name) > 40:
        await session_store.set_waiting_category(user.telegram_id, data)
        await message.answer("Название должно быть от 1 до 40 символов. Попробуй ещё:")
        return

    # Create custom category
    cat_service = CategoryService(session)
    category = await cat_service.create_custom(user_id=user.id, name=name)

    # Save the transaction
    entry_type = data.get("entry_type", "expense")
    amount = Decimal(data["amount"])
    currency = data.get("currency", user.default_currency)

    tx_service = TransactionService(session)
    transaction = await tx_service.add_transaction(
        user_id=user.id,
        type_=entry_type,
        amount=amount,
        currency=currency,
        category_id=category.id,
        description=data["description"],
        source=data["source"],
    )

    type_icon = "🔴" if entry_type == "expense" else "🟢"
    formatted = format_amount_short(amount)
    await message.answer(
        f"✅ Категория <b>{category.label}</b> создана!\n\n"
        f"{type_icon} <b>{formatted}</b> — {data['description']} [{category.label}]\n"
        f"<i>ID: {transaction.id}</i>",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("cat:"))
async def on_category_chosen(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    session_store: SessionStore,
) -> None:
    """Save transaction when user picks a category."""
    category_id = int(callback.data.split(":", 1)[1])
    msg_id = callback.message.message_id

    expense_data = await session_store.pop_pending(msg_id)
    if expense_data is None:
        await callback.answer("Расход уже сохранён или устарел.", show_alert=True)
        return

    entry_type = expense_data.get("entry_type", "expense")
    amount = Decimal(expense_data["amount"])
    currency = expense_data.get("currency", user.default_currency)

    # Get category label
    cat_service = CategoryService(session)
    category = await cat_service.get_by_id(category_id)
    cat_label = category.label if category else "📦 Другое"

    # Save transaction
    tx_service = TransactionService(session)
    transaction = await tx_service.add_transaction(
        user_id=user.id,
        type_=entry_type,
        amount=amount,
        currency=currency,
        category_id=category_id,
        description=expense_data["description"],
        source=expense_data["source"],
    )

    type_icon = "🔴" if entry_type == "expense" else "🟢"
    formatted = format_amount_short(amount)

    await callback.message.edit_text(
        f"{type_icon} <b>{formatted}</b> — {expense_data['description']} [{cat_label}]\n"
        f"<i>ID: {transaction.id}</i>",
    )
    await callback.answer("Сохранено!")
