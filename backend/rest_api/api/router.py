from fastapi import APIRouter
from .health import router as h_router
from .table import router as t_router


router = APIRouter()
router.include_router(h_router)
router.include_router(t_router)


