from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from tortoise import Tortoise


class Cfg(BaseSettings):
	APP_NAME: str = "Watermark System"
	API_V1: str = "/api/v1"
	VERSION: str = "1.0.0"
	CORS_ORIGINS: List[AnyHttpUrl] = []
	
	# model 配置
	MODEL_PATH: str = "gpt2"  # 所用模型
	MODEL_CACHE_DIR: str = ".cache/models"  # 缓存目录
	
	# JWT配置
	SECRET_KEY: str = "your-secret-key-here"  # 生产环境中应使用环境变量
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	
	# 数据库配置
	TORTOISE_ORM: dict = {
		"connections": {
			"default": {
				"engine": "tortoise.backends.mysql",
				"credentials": {
					"host": "localhost",
					"port": "3306",
					"user": "root",
					"password": "Rinux",
					"database": "watermark",  # db名（需提前创建db）
					"minsize": 1,  # 最少连接
					"maxsize": 5,  # 最大连接
					"charset": "utf8mb4",  # 编码
					"echo": True  # 打印SQL语句
				},
			}
		},
		"apps": {
			"models": {
				"models": ["backend.app.models.user"],
				"default_connection": "default"
			}
		},
		"use_tz": False,  # 时区开关
		'timezone': 'Asia/Shanghai'
	}
	
	class Config:
		case_sensitive = True
		env_file = ".env"
	
	@field_validator("CORS_ORIGINS", mode="before")
	def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
		if isinstance(v, str) and not v.startswith("["):
			return [i.strip() for i in v.split(",")]
		elif isinstance(v, (list, str)):
			return v
		raise ValueError(v)


cfg = Cfg()

Tortoise.init_models(
	["backend.app.models.user"],
	"models"
)
