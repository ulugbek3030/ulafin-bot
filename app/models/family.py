"""Family models — shared budgets between users."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), server_default="UZS")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    owner: Mapped["User"] = relationship()  # noqa: F821
    members: Mapped[list["FamilyMember"]] = relationship(
        back_populates="family", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Family id={self.id} name={self.name!r} owner={self.owner_id}>"


class FamilyMember(Base):
    __tablename__ = "family_members"
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_member"),
        CheckConstraint(
            "role IN ('owner', 'admin', 'member')", name="ck_family_member_role"
        ),
    )

    family_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("families.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), server_default="member")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    family: Mapped["Family"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<FamilyMember family={self.family_id} user={self.user_id} role={self.role}>"


class FamilyInvite(Base):
    __tablename__ = "family_invites"

    family_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("families.id", ondelete="CASCADE"), nullable=False
    )
    invite_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    max_uses: Mapped[int] = mapped_column(Integer, server_default="10")
    used_count: Mapped[int] = mapped_column(Integer, server_default="0")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    family: Mapped["Family"] = relationship()

    def __repr__(self) -> str:
        return f"<FamilyInvite code={self.invite_code!r} family={self.family_id}>"
