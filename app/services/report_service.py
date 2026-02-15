"""Report service — build formatted text reports."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repo import CategoryRepository
from app.repositories.transaction_repo import TransactionRepository
from app.utils.formatting import format_amount, get_month_name


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self._tx_repo = TransactionRepository(session)
        self._cat_repo = CategoryRepository(session)

    async def build_monthly_text_report(
        self,
        user_id: int,
        year: int,
        month: int,
        currency: str = "UZS",
        lang: str = "ru",
    ) -> str:
        """Build a formatted text report for a given month.

        Returns HTML-formatted string ready to send via Telegram.
        """
        summary = await self._tx_repo.get_monthly_summary(user_id, year, month)
        categories = await self._cat_repo.get_for_user(user_id)
        cat_map: dict[int, Category] = {c.id: c for c in categories}

        month_name = get_month_name(month, lang)

        lines = [f"<b>📊 {month_name} {year}</b>\n"]

        # Totals
        total_exp = format_amount(summary["total_expense"], currency)
        total_inc = format_amount(summary["total_income"], currency)
        balance = summary["balance"]
        balance_icon = "🟢" if balance >= 0 else "🔴"
        balance_fmt = format_amount(abs(balance), currency)

        lines.append(f"🔴 Расходы: <b>{total_exp}</b> ({summary['expense_count']})")
        lines.append(f"🟢 Доходы: <b>{total_inc}</b> ({summary['income_count']})")
        lines.append(f"{balance_icon} Баланс: <b>{'+' if balance >= 0 else '-'}{balance_fmt}</b>")

        # By category
        by_cat = summary["by_category"]
        if by_cat:
            lines.append("\n<b>По категориям:</b>")
            sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
            for cat_id, amount in sorted_cats:
                cat = cat_map.get(cat_id)
                cat_label = cat.label if cat else "📦 Другое"
                pct = (
                    int(amount / summary["total_expense"] * 100)
                    if summary["total_expense"]
                    else 0
                )
                amt_fmt = format_amount(amount, currency)
                lines.append(f"  {cat_label}: {amt_fmt} ({pct}%)")

        # Top expenses
        top = summary["top_expenses"]
        if top:
            lines.append("\n<b>Топ-5 расходов:</b>")
            for i, tx in enumerate(top, 1):
                cat = cat_map.get(tx.category_id)
                cat_label = cat.label if cat else "📦"
                amt_fmt = format_amount(tx.amount, tx.currency)
                lines.append(f"  {i}. {amt_fmt} — {tx.description} [{cat_label}]")

        return "\n".join(lines)
