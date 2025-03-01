from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	APP_NAME: str = "Watermark System"
	API_V1: str = "/api/v1"
	VERSION: str = "1.0.0"
	CORS_ORIGINS: List[AnyHttpUrl] = []


settings = Settings()
