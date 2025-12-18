from __future__ import annotations
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException


router = APIRouter(tags=["stats"])


def _placeholder_stats(user_id: int) -> Dict[str, Any]:
    #заглушка, пока нули
    return {
        "user_id": user_id,
        "hands_won": 0,
        "hands_lost": 0,
        "max_balance": 0,
        "max_bet": 0,
        "lost_stack": 0,
        "won_stack": 0,
    }


def _placeholder_history(user_id: int) -> List[Dict[str, Any]]:
    # История пустая, потому что FinishedGame/PlayerGame ещё не реализованы.
    return []


@router.get("/stats/me/stats")
def get_my_stats() -> Dict[str, Any]:
    fake_me_user_id = 1
    return {"status": 200, "stats": _placeholder_stats(fake_me_user_id)}


@router.get("/stats/me/history")
def get_my_history() -> Dict[str, Any]:
    fake_me_user_id = 1
    return {"status": 200, "history": _placeholder_history(fake_me_user_id)}


@router.get("/stats/{user_id}/stats")
def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Статистика пользователя по user_id."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    return {"status": 200, "stats": _placeholder_stats(user_id)}


@router.get("/stats/{user_id}/history")
def get_user_history(user_id: int) -> Dict[str, Any]:
    """История раздач пользователя по user_id."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    return {"status": 200, "history": _placeholder_history(user_id)}
