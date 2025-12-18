from fastapi import APIRouter
from .health import router as h_router

router = APIRouter()
router.include_router(h_router)
