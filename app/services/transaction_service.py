"""Transaction service — business logic for expenses and incomes."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.transaction_repo import TransactionRepository


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = TransactionRepository(session)
        self._session = session

    async def add_transaction(
        self,
        user_id: int,
        type_: str,
        amount: Decimal,
        currency: str = "UZS",
        amount_base: Decimal | None = None,
        category_id: int | None = None,
        description: str = "",
        source: str = "text",
        family_id: int | None = None,
    ) -> Transaction:
        """Create a new transaction (expense or income)."""
        transaction = await self._repo.add(
            user_id=user_id,
            type_=type_,
            amount=amount,
            currency=currency,
            amount_base=amount_base or amount,
            category_id=category_id,
            description=description,
            source=source,
            family_id=family_id,
        )
        await self._session.commit()
        return transaction

    async def get_monthly_summary(
        self,
        user_id: int,
        year: int,
        month: int,
    ) -> dict:
        """Get aggregated monthly financial summary."""
        return await self._repo.get_monthly_summary(user_id, year, month)

    async def get_by_month(
        self,
        user_id: int,
        year: int,
        month: int,
        entry_type: str | None = None,
    ):
        return await self._repo.get_by_month(user_id, year, month, entry_type)

    async def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Delete a transaction (only if owned by user)."""
        result = await self._repo.delete_transaction(transaction_id, user_id)
        await self._session.commit()
        return result

    async def get_category_total(
        self,
        user_id: int,
        category_id: int,
        year: int,
        month: int,
    ) -> Decimal:
        """Get total spending for a category in a given month."""
        return await self._repo.get_category_total(user_id, category_id, year, month)
