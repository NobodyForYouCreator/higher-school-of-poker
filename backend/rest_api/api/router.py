from fastapi import APIRouter
from .health import router as h_router
from .table import router as t_router
from .stats import router as s_router
from .auth import router as a_router


router = APIRouter()
router.include_router(h_router)
router.include_router(t_router)
router.include_router(s_router)
router.include_router(a_router)