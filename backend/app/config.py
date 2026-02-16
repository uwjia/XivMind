from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_TYPE: str = "sqlite"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    DATABASE_NAME: str = "xivmind"
    DOWNLOAD_DIR: str = "./downloads"
    SQLITE_DB_PATH: str = "./data/xivmind.db"

    ARXIV_MAX_RETRIES: int = 3
    ARXIV_RETRY_BASE_DELAY: float = 1.0
    ARXIV_BATCH_SIZE: int = 50

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
