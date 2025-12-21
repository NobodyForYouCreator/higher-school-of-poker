from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["stats"])


def _placeholder_stats(user_id: int) -> Dict[str, Any]:
    return {
        "hands_won": 0,
        "hands_lost": 0,
        "max_balance": 0,
        "max_bet": 0,
        "lost_stack": 0,
        "won_stack": 0,
    }


def _placeholder_history(user_id: int) -> List[Dict[str, Any]]:
    return []


def _current_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return int(user_id)


@router.get("/stats/me/stats")
def get_my_stats(request: Request) -> Dict[str, Any]:
    user_id = _current_user_id(request)
    return _placeholder_stats(user_id)


@router.get("/stats/me/history")
def get_my_history(request: Request) -> List[Dict[str, Any]]:
    user_id = _current_user_id(request)
    return _placeholder_history(user_id)


@router.get("/stats/{user_id}/stats")
def get_user_stats(user_id: int) -> Dict[str, Any]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    return _placeholder_stats(user_id)


@router.get("/stats/{user_id}/history")
def get_user_history(user_id: int) -> List[Dict[str, Any]]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")
    return _placeholder_history(user_id)

