from pydantic_settings import BaseSettings
from functools import lru_cache
import os


EMBEDDING_DIMENSIONS = {
    "all-MiniLM-L6-v2": 384,
    "paraphrase-multilingual-MiniLM-L12-v2": 384,
    "BAAI/bge-m3": 1024,
    "BAAI/bge-large-zh": 1024,
    "BAAI/bge-large-en": 1024,
    "BAAI/bge-base-en": 768,
    "BAAI/bge-base-zh": 768,
    "text-embedding-ada-002": 1536,
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


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

    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    LOCAL_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    USE_LOCAL_EMBEDDING: bool = False
    
    EMBEDDING_DEVICE: str = "auto"
    EMBEDDING_BATCH_SIZE: int = 32
    
    HF_ENDPOINT: str = "https://hf-mirror.com"
    
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    
    GLM_API_KEY: str = ""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    MILVUS_QUERY_BATCH_SIZE: int = 3000
    
    SKILLS_DIR: str = "./skills"
    SKILLS_WATCH_ENABLED: bool = True
    SKILLS_WATCH_DEBOUNCE_MS: int = 250
    SKILLS_RELOAD_ON_START: bool = True
    
    SUBAGENTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "subagents")
    SUBAGENTS_WATCH_ENABLED: bool = True
    SUBAGENTS_WATCH_DEBOUNCE_MS: int = 250
    SUBAGENTS_RELOAD_ON_START: bool = True
    SUBAGENTS_MAX_TURNS: int = 10
    SUBAGENTS_DEFAULT_MODEL: str = "glm-4"

    class Config:
        env_file = ".env"
    
    @property
    def EMBEDDING_DIM(self) -> int:
        if self.USE_LOCAL_EMBEDDING:
            return EMBEDDING_DIMENSIONS.get(self.LOCAL_EMBEDDING_MODEL, 384)
        else:
            return EMBEDDING_DIMENSIONS.get(self.OPENAI_EMBEDDING_MODEL, 1536)
    
    @property
    def LOCAL_EMBEDDING_DIM(self) -> int:
        return EMBEDDING_DIMENSIONS.get(self.LOCAL_EMBEDDING_MODEL, 384)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
