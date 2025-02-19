from fastapi import APIRouter
from app.api.endpoints import auth, watermark, evaluate

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(watermark.router, prefix="/watermark", tags=["watermark"])
api_router.include_router(evaluate.router, prefix="/evaluate", tags=["evaluation"])