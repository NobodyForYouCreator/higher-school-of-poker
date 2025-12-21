import asyncio
from typing import Any, AsyncGenerator, Generator, List

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.base import Base
from backend.database.session import get_db
from backend.models.player_game import PlayerGame
from backend.models.player_stats import PlayerStats
from backend.rest_api.api.stats import router as stats_router
from backend.services.game_service import GameService
from backend.poker_engine.table import Table
from backend.poker_engine.game_state import PlayerAction


@pytest.fixture
async def async_test_engine() -> AsyncGenerator[sessionmaker, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    yield async_session


@pytest.fixture
def test_app(async_test_engine: sessionmaker) -> Generator[FastAPI, None, None]:
    app = FastAPI()
    app.include_router(stats_router)
    async_session = async_test_engine

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return app


async def _simulate_hand(gs: GameService, table: Table, fold_user_id: int, db_session: AsyncSession) -> None:
    await gs.start_hand(table)
    await gs.apply_action(table, fold_user_id, PlayerAction.FOLD, 0, db_session)


@pytest.mark.asyncio
async def test_aggregated_stats_and_history(test_app: FastAPI, async_test_engine: sessionmaker) -> None:
    async_session = async_test_engine
    table = Table(table_id=42)
    table.seat_player(1, 1500)
    table.seat_player(2, 1500)
    gs = GameService()
    async with async_session() as session:
        await _simulate_hand(gs, table, fold_user_id=2, db_session=session)
    client = TestClient(test_app)
    resp = client.get("/stats/1/stats")
    assert resp.status_code == 200
    data = resp.json()["stats"]
    assert data["hands_won"] == 1
    assert data["hands_lost"] == 0
    assert data["won_stack"] == 50
    assert data["lost_stack"] == 0
    assert data["max_bet"] == 100
    assert data["max_balance"] == 1550
    resp_hist = client.get("/stats/1/history")
    assert resp_hist.status_code == 200
    history = resp_hist.json()["history"]
    assert len(history) == 1
    entry = history[0]
    assert entry["pot"] == 150
    assert entry["board"] == []
    assert entry["net_stack_delta"] == 50
    assert entry["won_hand"] is True
    resp2 = client.get("/stats/2/stats")
    assert resp2.status_code == 200
    stats2 = resp2.json()["stats"]
    assert stats2["hands_won"] == 0
    assert stats2["hands_lost"] == 1
    assert stats2["won_stack"] == 0
    assert stats2["lost_stack"] == 50
    assert stats2["max_bet"] == 50
    assert stats2["max_balance"] == 1450
    resp2_hist = client.get("/stats/2/history")
    history2 = resp2_hist.json()["history"]
    assert len(history2) == 1
    entry2 = history2[0]
    assert entry2["net_stack_delta"] == -50
    assert entry2["won_hand"] is False


@pytest.mark.asyncio
async def test_pagination_and_multiple_hands(test_app: FastAPI, async_test_engine: sessionmaker) -> None:
    async_session = async_test_engine
    table = Table(table_id=7)
    table.seat_player(1, 1500)
    table.seat_player(2, 1500)
    gs = GameService()
    async with async_session() as session:
        await _simulate_hand(gs, table, fold_user_id=2, db_session=session)
    async with async_session() as session:
        await gs.start_hand(table)
        await gs.apply_action(table, 1, PlayerAction.FOLD, 0, session)
    async with async_session() as session:
        result1 = await session.execute(
            select(PlayerGame).where(PlayerGame.user_id == 1).order_by(PlayerGame.id)
        )
        games1: List[PlayerGame] = result1.scalars().all()
        hands_won1 = sum(1 for pg in games1 if pg.won_hand)
        hands_lost1 = len(games1) - hands_won1
        max_bet1 = max(pg.bet for pg in games1) if games1 else 0
        max_bal1 = max(pg.resulting_balance or 0 for pg in games1) if games1 else 0
        won_stack1 = sum(pg.net_stack_delta for pg in games1 if pg.net_stack_delta > 0)
        lost_stack1 = sum(-pg.net_stack_delta for pg in games1 if pg.net_stack_delta < 0)
        result2 = await session.execute(
            select(PlayerGame).where(PlayerGame.user_id == 2).order_by(PlayerGame.id)
        )
        games2: List[PlayerGame] = result2.scalars().all()
        hands_won2 = sum(1 for pg in games2 if pg.won_hand)
        hands_lost2 = len(games2) - hands_won2
        max_bet2 = max(pg.bet for pg in games2) if games2 else 0
        max_bal2 = max(pg.resulting_balance or 0 for pg in games2) if games2 else 0
        won_stack2 = sum(pg.net_stack_delta for pg in games2 if pg.net_stack_delta > 0)
        lost_stack2 = sum(-pg.net_stack_delta for pg in games2 if pg.net_stack_delta < 0)
        finished_ids_user1 = [pg.finished_game_uuid for pg in games1[::-1]]
        finished_ids_user2 = [pg.finished_game_uuid for pg in games2[::-1]]
    client = TestClient(test_app)
    resp1 = client.get("/stats/1/stats")
    stats1 = resp1.json()["stats"]
    assert stats1["hands_won"] == hands_won1
    assert stats1["hands_lost"] == hands_lost1
    assert stats1["max_bet"] == max_bet1
    assert stats1["max_balance"] == max_bal1
    assert stats1["won_stack"] == won_stack1
    assert stats1["lost_stack"] == lost_stack1
    resp2 = client.get("/stats/2/stats")
    stats2 = resp2.json()["stats"]
    assert stats2["hands_won"] == hands_won2
    assert stats2["hands_lost"] == hands_lost2
    assert stats2["max_bet"] == max_bet2
    assert stats2["max_balance"] == max_bal2
    assert stats2["won_stack"] == won_stack2
    assert stats2["lost_stack"] == lost_stack2
    hist_all = client.get("/stats/1/history").json()["history"]
    assert [entry["game_id"] for entry in hist_all] == finished_ids_user1
    hist_limit1 = client.get("/stats/1/history", params={"limit": 1}).json()["history"]
    assert len(hist_limit1) == 1
    assert hist_limit1[0]["game_id"] == finished_ids_user1[0]
    hist_offset = client.get("/stats/1/history", params={"limit": 1, "offset": 1}).json()["history"]
    assert len(hist_offset) == 1
    assert hist_offset[0]["game_id"] == finished_ids_user1[1]
    bad_limit_resp = client.get("/stats/1/history", params={"limit": 0})
    assert bad_limit_resp.status_code == 400
    bad_offset_resp = client.get("/stats/1/history", params={"limit": 1, "offset": -1})
    assert bad_offset_resp.status_code == 400