import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def mock_milvus():
    with pytest.MonkeyPatch.context() as m:
        m.setenv("MILVUS_HOST", "localhost")
        m.setenv("MILVUS_PORT", "19530")
        m.setenv("DATABASE_NAME", "test_xivmind")
        yield
