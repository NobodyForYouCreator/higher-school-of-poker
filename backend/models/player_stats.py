from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    hands_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hands_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    max_balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    max_bet: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    lost_stack: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    won_stack: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)


@dataclass(frozen=True)
class StatsDelta:
    """
    Изменение статистики игрока после одной раздачи.

    user_id — чей это апдейт
    won_hand — выиграл ли раздачу
    bet — ставка/вклад игрока (для max_bet)
    net_stack_delta — итог по фишкам за раздачу:
        > 0 игрок в плюсе
        < 0 игрок в минусе
    resulting_balance — баланс игрока ПОСЛЕ раздачи (для max_balance)
    """

    user_id: int
    won_hand: bool
    bet: int
    net_stack_delta: int
    resulting_balance: Optional[int] = None


def update_stats(current: PlayerStats, deltas: Iterable[StatsDelta]) -> PlayerStats:
    current.hands_won = int(current.hands_won or 0)
    current.hands_lost = int(current.hands_lost or 0)
    current.max_balance = int(current.max_balance or 0)
    current.max_bet = int(current.max_bet or 0)
    current.lost_stack = int(current.lost_stack or 0)
    current.won_stack = int(current.won_stack or 0)

    for d in deltas:
        if d.user_id != current.user_id:
            continue

        if d.won_hand:
            current.hands_won += 1
        else:
            current.hands_lost += 1

        if d.bet > current.max_bet:
            current.max_bet = d.bet

        if d.net_stack_delta >= 0:
            current.won_stack += d.net_stack_delta
        else:
            current.lost_stack += (-d.net_stack_delta)

        if d.resulting_balance is not None and d.resulting_balance > current.max_balance:
            current.max_balance = d.resulting_balance

    return current
