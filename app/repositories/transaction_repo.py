"""Transaction repository — database operations for income/expenses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import extract, func, select

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    model = Transaction

    async def add(
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
        """Create a new transaction."""
        return await self.create(
            user_id=user_id,
            type=type_,
            amount=amount,
            currency=currency,
            amount_base=amount_base or amount,
            category_id=category_id,
            description=description,
            source=source,
            family_id=family_id,
        )

    async def get_by_month(
        self,
        user_id: int,
        year: int,
        month: int,
        entry_type: str | None = None,
    ) -> Sequence[Transaction]:
        """Get all transactions for a user in a given month."""
        stmt = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                extract("year", Transaction.created_at) == year,
                extract("month", Transaction.created_at) == month,
            )
            .order_by(Transaction.created_at.desc())
        )
        if entry_type:
            stmt = stmt.where(Transaction.type == entry_type)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_monthly_summary(
        self,
        user_id: int,
        year: int,
        month: int,
    ) -> dict:
        """Get aggregated monthly summary for a user."""
        transactions = await self.get_by_month(user_id, year, month)

        expenses = [t for t in transactions if t.type == "expense"]
        incomes = [t for t in transactions if t.type == "income"]

        total_expense = sum(t.amount_base or t.amount for t in expenses)
        total_income = sum(t.amount_base or t.amount for t in incomes)

        by_category: dict[int | None, Decimal] = {}
        for t in expenses:
            by_category[t.category_id] = by_category.get(t.category_id, Decimal(0)) + (
                t.amount_base or t.amount
            )

        top_expenses = sorted(expenses, key=lambda x: x.amount, reverse=True)[:5]

        return {
            "total_expense": total_expense,
            "total_income": total_income,
            "balance": total_income - total_expense,
            "expense_count": len(expenses),
            "income_count": len(incomes),
            "by_category": by_category,
            "top_expenses": top_expenses,
        }

    async def get_by_family_month(
        self,
        family_id: int,
        year: int,
        month: int,
        entry_type: str | None = None,
    ) -> Sequence[Transaction]:
        """Get all transactions for a family in a given month."""
        stmt = (
            select(Transaction)
            .where(
                Transaction.family_id == family_id,
                extract("year", Transaction.created_at) == year,
                extract("month", Transaction.created_at) == month,
            )
            .order_by(Transaction.created_at.desc())
        )
        if entry_type:
            stmt = stmt.where(Transaction.type == entry_type)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_category_total(
        self,
        user_id: int,
        category_id: int,
        year: int,
        month: int,
    ) -> Decimal:
        """Get total spending for a specific category in a month."""
        stmt = select(func.coalesce(func.sum(Transaction.amount_base), 0)).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.type == "expense",
            extract("year", Transaction.created_at) == year,
            extract("month", Transaction.created_at) == month,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Delete a transaction (only if owned by user)."""
        from sqlalchemy import delete

        stmt = delete(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
