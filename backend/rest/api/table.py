from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.database.session import get_db
from backend.rest.api.deps import get_current_user_id, get_table_service
from backend.rest.errors import http_error
from backend.rest.schemas.common import OkResponse
from backend.rest.schemas.table import TableCreateRequest, TableDetail, TableSummary
from backend.services.table_service import InsufficientBalanceError, TableNotFoundError, TableService, UserNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("/", response_model=list[TableSummary])
def list_tables(service: TableService = Depends(get_table_service)) -> list[TableSummary]:
    return service.list_tables()


@router.post("/create", response_model=TableSummary)
def create_table(
    payload: TableCreateRequest,
    service: TableService = Depends(get_table_service),
) -> TableSummary:
    return service.create_table(payload)


@router.get("/{table_id}", response_model=TableDetail)
def get_table_info(
    table_id: int,
    service: TableService = Depends(get_table_service),
) -> TableDetail:
    try:
        return service.get_table_info(table_id)
    except TableNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="table_not_found", message="Table not found") from exc


@router.post("/{table_id}/join", response_model=OkResponse)
async def join_table(
    table_id: int,
    user_id: int = Depends(get_current_user_id),
    service: TableService = Depends(get_table_service),
    db: AsyncSession = Depends(get_db),
) -> OkResponse:
    try:
        return await service.join_table(table_id, user_id=user_id, db=db)
    except TableNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="table_not_found", message="Table not found") from exc
    except UserNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="user_not_found", message="User not found") from exc
    except InsufficientBalanceError as exc:
        raise http_error(
            status.HTTP_400_BAD_REQUEST,
            code="insufficient_balance",
            message="Not enough balance for buy-in",
        ) from exc


@router.post("/{table_id}/leave", response_model=OkResponse)
async def leave_table(
    table_id: int,
    user_id: int = Depends(get_current_user_id),
    service: TableService = Depends(get_table_service),
    db: AsyncSession = Depends(get_db),
) -> OkResponse:
    try:
        return await service.leave_table(table_id, user_id=user_id, db=db)
    except TableNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="table_not_found", message="Table not found") from exc
    except UserNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="user_not_found", message="User not found") from exc


@router.post("/{table_id}/spectate", response_model=OkResponse)
async def spectate_table(
    table_id: int,
    user_id: int = Depends(get_current_user_id),
    service: TableService = Depends(get_table_service),
    db: AsyncSession = Depends(get_db),
) -> OkResponse:
    try:
        return await service.spectate_table(table_id, user_id=user_id, db=db)
    except TableNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="table_not_found", message="Table not found") from exc
    except UserNotFoundError as exc:
        raise http_error(status.HTTP_404_NOT_FOUND, code="user_not_found", message="User not found") from exc
