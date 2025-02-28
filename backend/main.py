from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.api import api_router
from .app.core.config import settings
from .app.core.llm import llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""应用启动时执行"""
	llm_service.load_model()
	yield
	"""应用关闭时执行"""# 可以在这里添加清理代码
	pass


app = FastAPI(
	title=settings.PROJECT_NAME,
	version=settings.VERSION,
	openapi_url=f"{settings.API_V1_STR}/openapi.json",
	lifespan=lifespan
)

# 配置CORS
if settings.BACKEND_CORS_ORIGINS:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
