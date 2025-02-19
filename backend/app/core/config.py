from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Watermark System"
    API_V1_STR: str = "/api"
    VERSION: str = "1.0.0"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"  # 在生产环境中应该使用环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: str = "postgresql://user:password@localhost:5432/watermark"
    
    # 模型配置
    DEFAULT_MODEL_PATH: str = "gpt2"  # 默认使用的模型
    MODEL_CACHE_DIR: str = ".cache/models"  # 模型缓存目录

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()