from functools import lru_cache
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator, SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
	# 应用信息
	ENVIRONMENT: str = "development"
	APP_NAME: str = "Watermark System"
	VERSION: str = "1.0.0"
	API_V1: str = "/api/v1"
	
	# 安全设置
	CORS_ORIGINS: List[AnyHttpUrl] = []
	JWT_SECRET_KEY: str
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	
	# 数据库设置
	SQL_HOST: str = "localhost"
	SQL_PORT: int = 3306
	SQL_USER: str
	SQL_PASSWORD: SecretStr
	SQL_DBNAME: str
	
	# 模型配置
	MODEL_PATH: str = "gpt2"
	MODEL_CACHE_DIR: str = ".cache/models"
	
	class Config:
		case_sensitive = True
		env_file = ".env"
		env_file_encoding = "utf-8"
	
	@field_validator("CORS_ORIGINS", mode="before")
	def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
		if isinstance(v, str) and not v.startswith("["):
			return [i.strip() for i in v.split(",")]
		elif isinstance(v, (list, str)):
			return v
		raise ValueError(v)
	
	@property
	def is_development(self) -> bool:
		return self.ENVIRONMENT.lower() == "development"
	
	@property
	def is_production(self) -> bool:
		return self.ENVIRONMENT.lower() == "production"
	
	def get_tortoise_config(self) -> Dict[str, Any]:
		"""返回Tortoise ORM配置，避免硬编码"""
		return {
			"apps": {
				"models": {
					"models": ["app.models", "aerich.models"],
					"default_connection": "default"
				}
			},
			"connections": {
				"default": {
					"engine": "tortoise.backends.mysql",
					"credentials": {
						"host": self.SQL_HOST,
						"port": self.SQL_PORT,
						"user": self.SQL_USER,
						"password": self.SQL_PASSWORD.get_secret_value(),
						"database": self.SQL_DBNAME,
						"minsize": 1,
						"maxsize": 5 if self.is_production else 2,
						"charset": "utf8mb4",
						"echo": not self.is_production,
					},
				}
			},
			"use_tz": False,
			'timezone': 'Asia/Shanghai'
		}


@lru_cache
def get_settings() -> Settings:
	"""使用lru_cache确保Settings只被初始化一次"""
	import os
	return Settings(
		JWT_SECRET_KEY=os.environ['JWT_SECRET_KEY'],
		SQL_HOST=os.environ['SQL_HOST'],
		SQL_PORT=os.environ['SQL_PORT'],
		SQL_USER=os.environ['SQL_USER'],
		SQL_PASSWORD=os.environ['SQL_PASSWORD'],
		SQL_DBNAME=os.environ['SQL_DBNAME']
	)


# 导出设置实例
cfg = get_settings()
# 导出ORM配置
TORTOISE_ORM = cfg.get_tortoise_config()
