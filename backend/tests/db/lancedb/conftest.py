import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import pandas as pd


@pytest.fixture
def temp_lancedb_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lancedb")
        os.makedirs(db_path, exist_ok=True)
        yield db_path


@pytest.fixture
def mock_lancedb_table():
    def create_table(data=None):
        table = Mock()
        if data is None:
            data = []
        df = pd.DataFrame(data) if data else pd.DataFrame()
        
        table.to_pandas = Mock(return_value=df)
        table.add = Mock()
        table.delete = Mock()
        table.search = Mock()
        
        def mock_search_results(results):
            mock_search = Mock()
            mock_search.where = Mock(return_value=mock_search)
            mock_search.limit = Mock(return_value=mock_search)
            mock_search.to_pandas = Mock(return_value=pd.DataFrame(results))
            table.search = Mock(return_value=mock_search)
            return mock_search
        
        table._set_search_results = mock_search_results
        return table
    
    return create_table


@pytest.fixture
def mock_lancedb_client(mock_lancedb_table, temp_lancedb_path):
    with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
        mock_db = Mock()
        mock_db.table_names = Mock(return_value=[])
        mock_db.create_table = Mock(side_effect=mock_lancedb_table)
        mock_db.open_table = Mock(side_effect=mock_lancedb_table)
        mock_db.drop_table = Mock()
        mock_lancedb.connect = Mock(return_value=mock_db)
        
        from app.db.lancedb.client import LanceDBClient
        LanceDBClient._instance = None
        LanceDBClient._initialized = False
        
        yield mock_db


@pytest.fixture
def sample_bookmark_data():
    return {
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a test abstract.",
        "comment": "Test comment",
        "journal_ref": "Test Journal",
        "doi": "10.1234/test",
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "published": "2024-01-01T00:00:00",
        "updated": "2024-01-02T00:00:00",
    }


@pytest.fixture
def sample_download_data():
    return {
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
    }


@pytest.fixture
def sample_paper_data():
    return {
        "id": "2301.12345",
        "title": "Test Paper Title",
        "abstract": "This is a test abstract for the paper.",
        "authors": ["Author One", "Author Two"],
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG"],
        "published": "2024-01-15T10:00:00",
        "updated": "2024-01-16T10:00:00",
        "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "comment": "Test comment",
        "journal_ref": "Test Journal",
        "doi": "10.1234/test",
    }


@pytest.fixture
def sample_embedding():
    return [0.1] * 1536


@pytest.fixture
def sample_conversation_data():
    from datetime import datetime
    return {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "title": "Test Conversation",
        "mode": "search",
        "starred": False,
        "pinned": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "message_count": 5,
    }


@pytest.fixture
def sample_core_memory_data():
    return {
        "user_id": "test-user",
        "research_interests": ["machine learning", "NLP"],
        "preferred_domains": ["cs.AI", "cs.LG"],
        "frequently_used_skills": ["summarize", "translate"],
        "language_preference": "en-US",
        "summary_style": "detailed",
        "custom_instructions": "Focus on methodology",
    }


@pytest.fixture
def sample_recall_memory_data():
    from datetime import datetime
    return {
        "memory_id": "test-memory-123",
        "user_id": "test-user",
        "session_id": "test-session-123",
        "content": "User is interested in transformer architectures",
        "embedding": [0.1] * 1536,
        "importance_score": 0.8,
        "access_count": 3,
        "timestamp": datetime.utcnow(),
        "category": "context",
        "auto_created": False,
        "ttl_days": 30,
        "metadata": {"source": "conversation"},
    }


@pytest.fixture
def sample_archival_memory_data():
    from datetime import datetime
    return {
        "memory_id": "test-archival-123",
        "user_id": "test-user",
        "content_type": "note",
        "title": "Important Research Note",
        "content": "Key findings about attention mechanisms",
        "embedding": [0.1] * 1536,
        "source_papers": ["2301.12345"],
        "tags": ["attention", "transformers"],
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
    }


@pytest.fixture
def sample_annotation_data():
    return {
        "paper_id": "2301.12345",
        "type": "highlight",
        "page_number": 1,
        "position": {"x": 100, "y": 200, "width": 300, "height": 20},
        "content": "This is highlighted text",
        "color": "rgba(255, 235, 59, 0.4)",
        "stroke_width": 2,
    }


@pytest.fixture
def sample_reading_progress_data():
    return {
        "paper_id": "2301.12345",
        "current_page": 5,
        "total_pages": 20,
        "zoom_level": 1.5,
        "view_mode": "continuous",
    }
