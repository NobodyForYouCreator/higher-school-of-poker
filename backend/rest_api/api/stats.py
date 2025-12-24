from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.models.player_stats import PlayerStats
from backend.models.player_game import PlayerGame
from backend.rest_api.api.deps import get_current_user_id
from backend.rest_api.errors import http_error
from backend.rest_api.schemas.stats import PlayerHistoryEntry, PlayerStatsOut


router = APIRouter(prefix="/stats", tags=["stats"])


async def _get_player_stats(db: AsyncSession, user_id: int) -> PlayerStatsOut:
    stats = await db.get(PlayerStats, user_id)
    if stats is None:
        return PlayerStatsOut(
            user_id=user_id,
            hands_won=0,
            hands_lost=0,
            max_balance=0,
            max_bet=0,
            lost_stack=0,
            won_stack=0,
        )
    return PlayerStatsOut(
        user_id=stats.user_id,
        hands_won=stats.hands_won,
        hands_lost=stats.hands_lost,
        max_balance=stats.max_balance,
        max_bet=stats.max_bet,
        lost_stack=stats.lost_stack,
        won_stack=stats.won_stack,
    )


async def _get_player_history(db: AsyncSession, user_id: int, *, limit: int, offset: int) -> list[PlayerHistoryEntry]:
    query = (
        select(PlayerGame)
        .options(selectinload(PlayerGame.game))
        .where(PlayerGame.user_id == user_id)
        .order_by(PlayerGame.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    games = list(result.scalars().all())
    history: list[PlayerHistoryEntry] = []
    for pg in games:
        game = pg.game
        history.append(
            PlayerHistoryEntry(
                game_id=str(pg.finished_game_uuid) if pg.finished_game_uuid is not None else None,
                table_id=pg.table_id,
                user_id=pg.user_id,
                hole_cards=pg.hole_cards,
                bet=pg.bet,
                net_stack_delta=pg.net_stack_delta,
                resulting_balance=pg.resulting_balance,
                won_hand=pg.won_hand,
                board=game.board if game else [],
                winners=game.winners if game else [],
                pot=game.pot if game else 0,
            )
        )
    return history


@router.get("/me/stats", response_model=PlayerStatsOut)
async def get_my_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> PlayerStatsOut:
    return await _get_player_stats(db, user_id)


@router.get("/me/history", response_model=list[PlayerHistoryEntry])
async def get_my_history(
    user_id: int = Depends(get_current_user_id),
    *,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[PlayerHistoryEntry]:
    return await _get_player_history(db, user_id, limit=limit, offset=offset)


@router.get("/{user_id}/stats", response_model=PlayerStatsOut)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)) -> PlayerStatsOut:
    if user_id <= 0:
        raise http_error(
            status.HTTP_400_BAD_REQUEST,
            code="invalid_user_id",
            message="user_id должен быть положительным",
        )
    return await _get_player_stats(db, user_id)


@router.get("/{user_id}/history", response_model=list[PlayerHistoryEntry])
async def get_user_history(
    user_id: int,
    *,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[PlayerHistoryEntry]:
    if user_id <= 0:
        raise http_error(
            status.HTTP_400_BAD_REQUEST,
            code="invalid_user_id",
            message="user_id должен быть положительным",
        )
    return await _get_player_history(db, user_id, limit=limit, offset=offset)
