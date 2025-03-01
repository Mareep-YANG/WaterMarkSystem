from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.endpoints.users import api_router
from core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""启动时执行"""
	print('启动！')
	yield
	"""关闭时执行""" # 可以在这里添加清理代码
	print('关闭！')

app = FastAPI(
	title=settings.APP_NAME,
	version=settings.VERSION,
	openapi_url=f"{settings.API_V1}/openapi.json",
	lifespan=lifespan
)

if settings.CORS_ORIGINS:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"]
	)

app.include_router(api_router, prefix=settings.API_V1)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
