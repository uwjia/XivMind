from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import platform
import sys


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


def get_app_data_dir() -> str:
    print(f"[config.py] get_app_data_dir called")
    print(f"[config.py] platform.system(): {platform.system()}")
    print(f"[config.py] sys.frozen: {getattr(sys, 'frozen', False)}")
    
    print(f"[config.py] All environment variables:")
    for key, value in os.environ.items():
        if key in ['APPDATA', 'LOCALAPPDATA', 'USERPROFILE', 'HOME', 'DOWNLOAD_DIR', 'LANCEDB_PATH']:
            print(f"  {key} = {value}")
    
    if platform.system() == "Windows":
        app_data = os.environ.get("APPDATA")
        print(f"[config.py] APPDATA env: '{app_data}'")
        
        if app_data:
            result = os.path.join(app_data, "XivMind")
            print(f"[config.py] get_app_data_dir returning: {result}")
            return result
        
        user_profile = os.environ.get("USERPROFILE")
        print(f"[config.py] USERPROFILE env: '{user_profile}'")
        if user_profile:
            result = os.path.join(user_profile, "AppData", "Roaming", "XivMind")
            print(f"[config.py] get_app_data_dir from USERPROFILE: {result}")
            return result
    
    fallback = os.path.expanduser("~/.xivmind")
    print(f"[config.py] expanduser('~') = {os.path.expanduser('~')}")
    print(f"[config.py] get_app_data_dir fallback returning: {fallback}")
    return fallback


APP_DATA_DIR = get_app_data_dir()
print(f"[config.py] APP_DATA_DIR computed at module load time: {APP_DATA_DIR}")


class Settings(BaseSettings):
    DATABASE_TYPE: str = "sqlite"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    DATABASE_NAME: str = "xivmind"
    DOWNLOAD_DIR: str = os.path.join(APP_DATA_DIR, "downloads")
    SQLITE_DB_PATH: str = os.path.join(APP_DATA_DIR, "data", "xivmind.db")
    LANCEDB_PATH: str = os.path.join(APP_DATA_DIR, "data", "lancedb")

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = os.path.join(APP_DATA_DIR, "logs")
    LOG_FILE_MAX_SIZE: str = "10 MB"
    LOG_FILE_RETENTION: str = "7 days"
    LOG_CONSOLE_ENABLED: bool = True
    LOG_FILE_ENABLED: bool = True
    LOG_JSON_ENABLED: bool = False

    ARXIV_MAX_RETRIES: int = 3
    ARXIV_RETRY_BASE_DELAY: float = 1.0
    ARXIV_BATCH_SIZE: int = 300
    ARXIV_FETCH_DELAY: float = 5.0

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = ""
    
    LOCAL_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    USE_LOCAL_EMBEDDING: bool = True
    
    EMBEDDING_DEVICE: str = "auto"
    EMBEDDING_BATCH_SIZE: int = 32
    
    HF_ENDPOINT: str = "https://hf-mirror.com"
    
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    
    GLM_API_KEY: str = ""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    MILVUS_QUERY_BATCH_SIZE: int = 3000
    
    SKILLS_DIR: str = os.path.join(APP_DATA_DIR, "skills")
    SKILLS_WATCH_ENABLED: bool = True
    SKILLS_WATCH_DEBOUNCE_MS: int = 250
    SKILLS_RELOAD_ON_START: bool = True
    
    SUBAGENTS_DIR: str = os.path.join(APP_DATA_DIR, "subagents")
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
