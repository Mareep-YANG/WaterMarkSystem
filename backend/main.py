import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router, init_db
from app.core import cfg, llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
	print('\033[7;37m启动！\033[0m')
	await llm_service.load_model()
	
	yield
	
	print('\033[7;37m关闭！\033[0m')


app = FastAPI(
	title=cfg.APP_NAME,
	version=cfg.VERSION,
	openapi_url=f"{cfg.API_V1}/openapi.json",
	lifespan=lifespan
)


if cfg.CORS_ORIGINS:
	app.add_middleware(
		CORSMiddleware,
	#	allow_origins=[str(origin) for origin in cfg.CORS_ORIGINS],
		allow_origins=["*"], #TODO:生产环境下改为前端地址
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"]
	)

app.include_router(
	api_router,
	prefix=cfg.API_V1
)

init_db(app)

if __name__ == "__main__":
	import uvicorn
	
	uvicorn.run(
		'main:app',
		host="0.0.0.0",
		port=8000,
		reload=True,
		use_colors=True
	)
