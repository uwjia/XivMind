import pytest
import sys
from unittest.mock import MagicMock

sys.modules["pymilvus"] = MagicMock()
sys.modules["pymilvus.connections"] = MagicMock()
sys.modules["pymilvus.Collection"] = MagicMock()
sys.modules["pymilvus.utility"] = MagicMock()
sys.modules["pymilvus.DataType"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()


@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.DATABASE_TYPE = "sqlite"
    mock.SQLITE_DB_PATH = "./data/test.db"
    mock.MILVUS_HOST = "localhost"
    mock.MILVUS_PORT = 19530
    mock.DATABASE_NAME = "test"
    mock.DOWNLOAD_DIR = "./downloads"
    mock.LLM_PROVIDER = "openai"
    mock.LLM_MODEL = "gpt-4o-mini"
    mock.OPENAI_API_KEY = "test-key"
    mock.OLLAMA_BASE_URL = "http://localhost:11434"
    mock.OLLAMA_MODEL = "llama3"
    mock.MILVUS_QUERY_BATCH_SIZE = 1000
    mock.USE_LOCAL_EMBEDDING = True
    mock.LOCAL_EMBEDDING_MODEL = "BAAI/bge-m3"
    mock.EMBEDDING_DEVICE = "auto"
    mock.EMBEDDING_BATCH_SIZE = 32
    mock.HF_ENDPOINT = "https://hf-mirror.com"
    return mock


@pytest.fixture
def mock_paper():
    return {
        "id": "2301.12345",
        "title": "Test Paper Title",
        "abstract": "This is a test abstract for the paper.",
        "authors": ["Author One", "Author Two"],
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG"],
        "published": "2024-01-15T10:00:00",
        "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
    }
