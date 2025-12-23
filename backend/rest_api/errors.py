from __future__ import annotations

from fastapi import HTTPException

from backend.rest_api.schemas.error import ErrorDetail


def http_error(status_code: int, *, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=ErrorDetail(code=code, message=message).model_dump())

