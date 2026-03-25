import pytest
from unittest.mock import Mock, patch, MagicMock

from app.db.lancedb.followed_author_repo import LanceDBFollowedAuthorRepository


class TestLanceDBFollowedAuthorRepository:
    """Tests for LanceDB implementation."""
    
    @pytest.fixture
    def mock_table(self):
        table = MagicMock()
        table.count_rows.return_value = 0
        return table
    
    @pytest.fixture
    def repo(self, mock_table):
        with patch('app.db.lancedb.followed_author_repo.lancedb_client') as mock_client:
            mock_client.init_tables.return_value = None
            mock_client.get_table.return_value = mock_table
            
            repo = LanceDBFollowedAuthorRepository()
            repo._table = mock_table
            yield repo
    
    def test_add(self, repo, mock_table):
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
        mock_table.add.assert_called_once()
    
    def test_remove(self, repo, mock_table):
        result = repo.remove("test-id")
        
        assert result is True
        mock_table.delete.assert_called_once_with("id = 'test-id'")
    
    def test_get_not_found(self, repo, mock_table):
        mock_df = MagicMock()
        mock_df.__len__ = Mock(return_value=0)
        mock_table.search.return_value.where.return_value.limit.return_value.to_pandas.return_value = mock_df
        
        result = repo.get("non-existent-id")
        
        assert result is None
    
    def test_is_followed(self, repo, mock_table):
        mock_df = MagicMock()
        mock_df.__len__ = Mock(return_value=0)
        mock_table.search.return_value.where.return_value.limit.return_value.to_pandas.return_value = mock_df
        
        assert repo.is_followed("John Doe") is False
    
    def test_update_notes_not_found(self, repo, mock_table):
        mock_df = MagicMock()
        mock_df.__len__ = Mock(return_value=0)
        mock_table.search.return_value.where.return_value.limit.return_value.to_pandas.return_value = mock_df
        
        result = repo.update_notes("Non Existent", "New notes")
        
        assert result is False
    
    def test_update_paper_info_not_found(self, repo, mock_table):
        mock_df = MagicMock()
        mock_df.__len__ = Mock(return_value=0)
        mock_table.search.return_value.where.return_value.limit.return_value.to_pandas.return_value = mock_df
        
        result = repo.update_paper_info("Non Existent", 10, "2024-06-15")
        
        assert result is False
