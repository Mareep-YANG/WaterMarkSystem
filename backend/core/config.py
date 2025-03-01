from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	APP_NAME: str = "Watermark System"
	API_V1: str = "/api/v1"
	VERSION: str = "1.0.0"
	CORS_ORIGINS: List[AnyHttpUrl] = []
	MODEL_PATH: str = "gpt2"  # 默认模型
	MODEL_CACHE_DIR: str = ".cache/models"  # 模型缓存目录


settings = Settings()
