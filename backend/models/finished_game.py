from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.player_game import PlayerGame


class FinishedGame(Base):
    __tablename__ = "finished_games"
    uuid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)


    pot: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    board: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    winners: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=list)

    players: Mapped[list[PlayerGame]] = relationship(
        "PlayerGame",
        back_populates="game",
        cascade="all, delete-orphan",
    )
