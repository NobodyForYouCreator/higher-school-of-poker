from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    username: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=5000, server_default="5000")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
