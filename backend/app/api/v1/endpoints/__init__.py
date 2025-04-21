from fastapi import APIRouter

from . import auth, dataset, evaluate, model, watermark, system

api_router = APIRouter()

api_router.include_router(
	auth.router,
	prefix="/auth",
	tags=["auth"]
)

api_router.include_router(
	system.router,
	prefix="/system",
	tags=["system"]
)

api_router.include_router(
	evaluate.router,
	prefix="/evaluate",
	tags=["evaluate"]
)

api_router.include_router(
	watermark.router,
	prefix="/watermark",
	tags=["watermark"]
)

api_router.include_router(
	dataset.router,
	prefix="/dataset",
	tags=["dataset"]
)

api_router.include_router(
	model.router,
	prefix="/model",
	tags=["model"]
)
