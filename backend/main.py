from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.llm import llm_service

app = FastAPI(
	title=settings.PROJECT_NAME,
	version=settings.VERSION,
	openapi_url=f"{settings.API_V1_STR}/openapi.json"
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


@app.on_event("startup")
async def startup_event():
	"""应用启动时执行"""
	# 加载语言模型
	llm_service.load_model()


@app.on_event("shutdown")
async def shutdown_event():
	"""应用关闭时执行"""
	# 可以在这里添加清理代码
	pass


if __name__ == "__main__":
	import uvicorn
	
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
