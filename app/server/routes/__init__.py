from fastapi import APIRouter

from .monitoring import router as monitoring_router
from .route import router as constraint_router


router = APIRouter()

router.include_router(monitoring_router)
router.include_router(constraint_router)
