import asyncio

import pytest
from fastapi.testclient import TestClient
from collections.abc import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.database.session import get_db
from backend.models.user import User
from backend.rest_api.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_models() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(User.metadata.create_all, tables=[User.__table__])

    asyncio.run(init_models())

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


def test_register_login_and_me_flow(client: TestClient) -> None:
    register_payload = {"username": "alice", "password": "secret-pass"}

    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "Bearer"
    assert data["access_token"]

    login_payload = {"login": "alice", "password": "secret-pass"}
    login = client.post("/api/auth/login", json=login_payload)
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    profile = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == "alice"


def test_register_duplicate_username(client: TestClient) -> None:
    payload = {"username": "duplicate", "password": "secret-pass"}

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    duplicate = client.post("/api/auth/register", json=payload)
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Username already exists"


def test_login_invalid_password(client: TestClient) -> None:
    client.post("/api/auth/register", json={"username": "bob", "password": "secret-pass"})

    login = client.post("/api/auth/login", json={"login": "bob", "password": "wrong"})
    assert login.status_code == 401
    assert login.json()["detail"] in ("Invalid login or password", "Invalid username or password")


def test_me_requires_auth_header(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401

    try:
        assert response.json()["detail"] == "Missing or invalid authorization header"
    except Exception:
        assert response.text == "Missing or invalid authorization header"
