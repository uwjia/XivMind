import pytest
from unittest.mock import Mock, patch, MagicMock
import json


@pytest.fixture
def mock_milvus_collection():
    def create_collection(data=None):
        collection = Mock()
        collection.load = Mock()
        collection.insert = Mock()
        collection.delete = Mock()
        collection.upsert = Mock()
        collection.flush = Mock()
        collection.create_index = Mock()
        collection.num_entities = len(data) if data else 0
        
        query_results = data if data else []
        
        def mock_query(expr=None, output_fields=None, limit=None):
            return query_results
        
        collection.query = Mock(side_effect=mock_query)
        
        collection._set_query_results = lambda results: (query_results.clear(), query_results.extend(results))
        
        return collection
    
    return create_collection


@pytest.fixture
def mock_milvus_client(mock_milvus_collection):
    with patch('app.db.milvus.client.connections') as mock_connections:
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.db') as mock_db:
                with patch('app.db.milvus.client.Collection') as mock_collection_class:
                    with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                        mock_settings = Mock()
                        mock_settings.MILVUS_HOST = "localhost"
                        mock_settings.MILVUS_PORT = 19530
                        mock_settings.DATABASE_NAME = "test"
                        mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                        mock_get_settings.return_value = mock_settings
                        
                        mock_connections.connect = Mock()
                        mock_db.list_database = Mock(return_value=["test"])
                        mock_db.create_database = Mock()
                        mock_db.using_database = Mock()
                        mock_utility.has_collection = Mock(return_value=False)
                        mock_utility.drop_collection = Mock()
                        
                        mock_collection_class.return_value = mock_milvus_collection()
                        
                        from app.db.milvus.client import MilvusClient
                        MilvusClient._instance = None
                        MilvusClient._initialized = False
                        
                        yield {
                            'connections': mock_connections,
                            'utility': mock_utility,
                            'db': mock_db,
                            'Collection': mock_collection_class,
                            'settings': mock_settings,
                        }


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
def sample_bookmark_entity():
    return {
        "id": "test-bookmark-id",
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "authors": json.dumps(["Author One", "Author Two"]),
        "abstract": "This is a test abstract.",
        "comment": "Test comment",
        "journal_ref": "Test Journal",
        "doi": "10.1234/test",
        "primary_category": "cs.AI",
        "categories": json.dumps(["cs.AI", "cs.LG"]),
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "published": "2024-01-01T00:00:00",
        "updated": "2024-01-02T00:00:00",
        "created_at": "2024-01-03T00:00:00",
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
def sample_download_entity():
    return {
        "id": "test-task-id",
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "status": "completed",
        "progress": 100,
        "file_path": "/path/to/file.pdf",
        "file_size": 1234567,
        "error_message": "",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
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
def sample_paper_entity():
    return {
        "id": "2301.12345",
        "title": "Test Paper Title",
        "abstract": "This is a test abstract for the paper.",
        "authors": json.dumps(["Author One", "Author Two"]),
        "primary_category": "cs.AI",
        "categories": json.dumps(["cs.AI", "cs.LG"]),
        "published": "2024-01-15T10:00:00",
        "updated": "2024-01-16T10:00:00",
        "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "comment": "Test comment",
        "journal_ref": "Test Journal",
        "doi": "10.1234/test",
        "fetched_at": "2024-01-15T00:00:00",
    }


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
def sample_conversation_entity():
    return {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "title": "Test Conversation",
        "mode": "search",
        "starred": False,
        "pinned": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-02T00:00:00",
        "message_count": 5,
    }


@pytest.fixture
def sample_date_index_entity():
    return {
        "date": "2024-01-15",
        "total_count": 100,
        "fetched_at": "2024-01-15T00:00:00",
    }


@pytest.fixture
def sample_embedding_index_entity():
    return {
        "date": "2024-01-15",
        "total_count": 50,
        "generated_at": "2024-01-15T00:00:00",
        "model_name": "text-embedding-ada-002",
    }
