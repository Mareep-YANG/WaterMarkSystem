from fastapi import APIRouter

from . import (evaluate, users, watermark)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(evaluate.router, prefix="/evaluate", tags=["evaluate"])
api_router.include_router(watermark.router, prefix="/watermark", tags=["watermark"])
