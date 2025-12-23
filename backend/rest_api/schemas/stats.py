from pydantic import BaseModel


class PlayerStatsOut(BaseModel):
    user_id: int
    hands_won: int
    hands_lost: int
    max_balance: int
    max_bet: int
    lost_stack: int
    won_stack: int


class PlayerHistoryEntry(BaseModel):
    game_id: str | None
    table_id: int | None
    user_id: int
    hole_cards: list[str] | None
    bet: int | None
    net_stack_delta: int | None
    resulting_balance: int | None
    won_hand: bool | None
    board: list[str]
    winners: list[int]
    pot: int

