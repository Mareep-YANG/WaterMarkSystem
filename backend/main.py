from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router, init_db
from app.core import cfg, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
	print('\033[7;37m启动！\033[0m')
	
	yield
	
	print('\033[7;37m关闭！\033[0m')


app = FastAPI(
	title=cfg.APP_NAME,
	version=cfg.VERSION,
	openapi_url=f"{cfg.API_V1}/openapi.json",
	lifespan=lifespan
)

# CORS配置
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
	expose_headers=["*"],
	max_age=3600  # 预检请求缓存时间
)

app.include_router(
	api_router,
	prefix=cfg.API_V1
)

app.include_router(
	tasks.router,
	prefix=cfg.API_V1
)

init_db(app)

if __name__ == "__main__":
	import uvicorn
	import logging
	
	# 配置日志
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	)
	logger = logging.getLogger("uvicorn")
	
	try:
		uvicorn.run(
			'main:app',
			host="127.0.0.1",
			port=8000,
			reload=True,
			use_colors=True,
			workers=1,
			loop="auto",
			http="auto",
			proxy_headers=True,
			server_header=True,
			date_header=True,
			log_level="info",
			access_log=True,
			timeout_keep_alive=30
		)
	except Exception as e:
		logger.error(f"服务器启动失败: {str(e)}")
		raise
