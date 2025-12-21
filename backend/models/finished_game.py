from __future__ import annotations

from typing import List

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class FinishedGame(Base):
    __tablename__ = "finished_games"
    uuid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)


    pot: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    board: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    winners: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False, default=list)

    players: Mapped[List["PlayerGame"]] = relationship(
        "PlayerGame",
        back_populates="game",
        cascade="all, delete-orphan",
    )