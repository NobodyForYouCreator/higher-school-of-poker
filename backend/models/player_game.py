from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.finished_game import FinishedGame
    from backend.models.user import User


class PlayerGame(Base):
    __tablename__ = "player_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    finished_game_uuid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("finished_games.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    table_id: Mapped[int] = mapped_column(Integer, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    hole_cards: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    bet: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    net_stack_delta: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    resulting_balance: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    won_hand: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    game: Mapped[FinishedGame] = relationship(
        "FinishedGame",
        back_populates="players",
    )

    user: Mapped[User] = relationship("User")
