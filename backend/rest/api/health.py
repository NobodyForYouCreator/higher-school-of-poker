from http import HTTPStatus

from fastapi import APIRouter, Response

from backend.rest.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> Response:
    return Response(status_code=HTTPStatus.OK)


@router.get("/health/settings")
def health_settings() -> dict:
    return {
        "api_prefix": settings.api_prefix,
        "cors_origins": settings.cors_origins,
        "database_url": settings.database_url_redacted(),
        "env_source": settings.env_source(),
    }
