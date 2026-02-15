"""Initial schema — all tables for v2.0.

Revision ID: 001_initial
Revises: None
Create Date: 2025-02-14
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger, unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("is_registered", sa.Boolean, server_default="false"),
        sa.Column("language", sa.String(5), server_default="ru"),
        sa.Column("default_currency", sa.String(3), server_default="UZS"),
        sa.Column("timezone", sa.String(50), server_default="Asia/Tashkent"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── categories ────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(50), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(10), server_default="📌"),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "key", name="uq_category_user_key"),
    )

    # ── currencies ────────────────────────────────────────────
    op.create_table(
        "currencies",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(3), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("symbol", sa.String(10), nullable=False),
        sa.Column("decimal_places", sa.Integer, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── exchange_rates ────────────────────────────────────────
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("from_currency", sa.String(3), nullable=False, index=True),
        sa.Column("to_currency", sa.String(3), nullable=False, index=True),
        sa.Column("rate", sa.Numeric(18, 6), nullable=False),
        sa.Column("source", sa.String(50), server_default="cbu.uz"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── families ──────────────────────────────────────────────
    op.create_table(
        "families",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "owner_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("currency", sa.String(3), server_default="UZS"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── family_members ────────────────────────────────────────
    op.create_table(
        "family_members",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "family_id",
            sa.BigInteger,
            sa.ForeignKey("families.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(10), server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("family_id", "user_id", name="uq_family_member"),
        sa.CheckConstraint("role IN ('owner', 'admin', 'member')", name="ck_family_member_role"),
    )

    # ── family_invites ────────────────────────────────────────
    op.create_table(
        "family_invites",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "family_id",
            sa.BigInteger,
            sa.ForeignKey("families.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("invite_code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("max_uses", sa.Integer, server_default="10"),
        sa.Column("used_count", sa.Integer, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── transactions ──────────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "family_id",
            sa.BigInteger,
            sa.ForeignKey("families.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("type", sa.String(10), nullable=False, server_default="expense"),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="UZS"),
        sa.Column("amount_base", sa.Numeric(18, 2), nullable=True),
        sa.Column(
            "category_id",
            sa.Integer,
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.String(500), server_default=""),
        sa.Column("source", sa.String(20), server_default="text"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('expense', 'income')", name="ck_transaction_type"),
    )
    op.create_index(
        "ix_transaction_user_created", "transactions", ["user_id", "created_at"]
    )
    op.create_index(
        "ix_transaction_user_type_created", "transactions", ["user_id", "type", "created_at"]
    )

    # ── budgets ───────────────────────────────────────────────
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "family_id",
            sa.BigInteger,
            sa.ForeignKey("families.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "category_id",
            sa.Integer,
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("amount_limit", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="UZS"),
        sa.Column("period", sa.String(10), server_default="monthly"),
        sa.Column("alert_at_percent", sa.Integer, server_default="80"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "period IN ('weekly', 'monthly', 'yearly')", name="ck_budget_period"
        ),
    )

    # ── budget_alerts ─────────────────────────────────────────
    op.create_table(
        "budget_alerts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "budget_id",
            sa.Integer,
            sa.ForeignKey("budgets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("percent_reached", sa.Integer, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── reminders ─────────────────────────────────────────────
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(10), nullable=False, server_default="daily"),
        sa.Column("time", sa.Time, nullable=False),
        sa.Column("day_of_week", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('daily', 'weekly')", name="ck_reminder_type"),
    )


def downgrade() -> None:
    op.drop_table("reminders")
    op.drop_table("budget_alerts")
    op.drop_table("budgets")
    op.drop_index("ix_transaction_user_type_created", table_name="transactions")
    op.drop_index("ix_transaction_user_created", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("family_invites")
    op.drop_table("family_members")
    op.drop_table("families")
    op.drop_table("exchange_rates")
    op.drop_table("currencies")
    op.drop_table("categories")
    op.drop_table("users")
