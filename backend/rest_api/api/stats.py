from __future__ import annotations
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.models.player_stats import PlayerStats
from backend.models.player_game import PlayerGame


router = APIRouter(tags=["stats"])


async def _get_player_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    stats = await db.get(PlayerStats, user_id)
    if stats is None:
        return {
            "user_id": user_id,
            "hands_won": 0,
            "hands_lost": 0,
            "max_balance": 0,
            "max_bet": 0,
            "lost_stack": 0,
            "won_stack": 0,
        }
    return {
        "user_id": stats.user_id,
        "hands_won": stats.hands_won,
        "hands_lost": stats.hands_lost,
        "max_balance": stats.max_balance,
        "max_bet": stats.max_bet,
        "lost_stack": stats.lost_stack,
        "won_stack": stats.won_stack,
    }


async def _get_player_history(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
    query = (
        select(PlayerGame)
        .options(selectinload(PlayerGame.game))
        .where(PlayerGame.user_id == user_id)
        .order_by(PlayerGame.id.desc())
    )
    result = await db.execute(query)
    games: List[PlayerGame] = result.scalars().all()
    history: List[Dict[str, Any]] = []
    for pg in games:
        game = pg.game
        history.append(
            {
                "game_id": pg.finished_game_uuid,
                "table_id": pg.table_id,
                "user_id": pg.user_id,
                "hole_cards": pg.hole_cards,
                "bet": pg.bet,
                "net_stack_delta": pg.net_stack_delta,
                "resulting_balance": pg.resulting_balance,
                "won_hand": pg.won_hand,
                "board": game.board if game else [],
                "winners": game.winners if game else [],
                "pot": game.pot if game else 0,
            }
        )
    return history


@router.get("/stats/me/stats")
async def get_my_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    user_id = 1
    stats = await _get_player_stats(db, user_id)
    return {"status": 200, "stats": stats}


@router.get("/stats/me/history")
async def get_my_history(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    user_id = 1
    history = await _get_player_history(db, user_id)
    return {"status": 200, "history": history}


@router.get("/stats/{user_id}/stats")
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    stats = await _get_player_stats(db, user_id)
    return {"status": 200, "stats": stats}


@router.get("/stats/{user_id}/history")
async def get_user_history(user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    history = await _get_player_history(db, user_id)
    return {"status": 200, "history": history}
