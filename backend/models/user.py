from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    username: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)



    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
