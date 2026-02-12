from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    DATABASE_NAME: str = "xivmind"
    DOWNLOAD_DIR: str = "./downloads"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
