from fastapi import APIRouter
from .posts import router as posts_router
from .items import router as items_router

router = APIRouter()
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(items_router, prefix="/items", tags=["items"])