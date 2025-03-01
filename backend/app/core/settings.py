from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	APP_NAME: str = "Watermark System"
	API_V1: str = "/api/v1"
	VERSION: str = "1.0.0"
	CORS_ORIGINS: List[AnyHttpUrl] = []
	
	# model 配置
	MODEL_PATH: str = "gpt2"  # 所用模型
	MODEL_CACHE_DIR: str = ".cache/models"  # 缓存目录
	
	# JWT配置
	SECRET_KEY: str = "your-secret-key-here"  # 在生产环境中应该使用环境变量
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	
	# 数据库配置
	SQLALCHEMY_DATABASE_URI: str = "postgresql://user:password@localhost:5432/watermark"
	
	class Config:
		case_sensitive = True
		env_file = ".env"
	
	@field_validator("CORS_ORIGINS", mode='before')
	def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
		if isinstance(v, str) and not v.startswith("["):
			return [i.strip() for i in v.split(",")]
		elif isinstance(v, (list, str)):
			return v
		raise ValueError(v)


settings = Settings()
