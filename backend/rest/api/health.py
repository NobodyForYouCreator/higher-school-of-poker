from http import HTTPStatus

from fastapi import APIRouter, Response


router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> Response:
    return Response(status_code=HTTPStatus.OK)
