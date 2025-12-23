from pydantic import BaseModel, Field


class TableCreateRequest(BaseModel):
    max_players: int = Field(ge=2, le=9)
    buy_in: int = Field(ge=0)
    private: bool = False


class TableSummary(BaseModel):
    id: str
    max_players: int
    buy_in: int
    private: bool
    players_count: int
    spectators_count: int


class TableSeat(BaseModel):
    position: int
    user_id: int
    stack: int
    is_spectator: bool


class TableDetail(TableSummary):
    seats: list[TableSeat]

