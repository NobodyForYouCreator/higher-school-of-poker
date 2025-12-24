from fastapi import APIRouter

from .tables import router as tables_router

router = APIRouter()
router.include_router(tables_router)
