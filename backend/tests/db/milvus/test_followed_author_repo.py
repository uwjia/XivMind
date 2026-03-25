import pytest
from unittest.mock import MagicMock, patch

from app.db.milvus.followed_author_repo import MilvusFollowedAuthorRepository


class TestMilvusFollowedAuthorRepository:
    """Tests for Milvus implementation."""
    
    @pytest.fixture
    def mock_collection(self):
        collection = MagicMock()
        collection.num_entities = 0
        return collection
    
    @pytest.fixture
    def repo(self, mock_collection):
        with patch('app.db.milvus.followed_author_repo.milvus_client') as mock_client:
            mock_client.get_collection.return_value = mock_collection
            
            repo = MilvusFollowedAuthorRepository()
            repo._collection = mock_collection
            yield repo
    
    def test_add(self, repo, mock_collection):
        data = {
            "author_name": "John Doe",
            "paper_count": 10,
            "latest_published": "2024-01-15",
            "notes": "Test notes"
        }
        
        result = repo.add(data)
        
        assert result["author_name"] == "John Doe"
        assert result["paper_count"] == 10
        assert result["latest_published"] == "2024-01-15"
        assert result["notes"] == "Test notes"
        assert result["id"] is not None
        mock_collection.insert.assert_called_once()
    
    def test_remove(self, repo, mock_collection):
        result = repo.remove("test-id")
        
        assert result is True
        mock_collection.delete.assert_called()
    
    def test_get_not_found(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        result = repo.get("non-existent-id")
        
        assert result is None
    
    def test_is_followed(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        assert repo.is_followed("John Doe") is False
    
    def test_get_all_empty(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        results, total = repo.get_all()
        
        assert results == []
        assert total == 0
    
    def test_update_notes_not_found(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        result = repo.update_notes("Non Existent", "New notes")
        
        assert result is False
    
    def test_update_paper_info_not_found(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        result = repo.update_paper_info("Non Existent", 10, "2024-06-15")
        
        assert result is False
