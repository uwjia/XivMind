import pytest
from unittest.mock import Mock, patch

from app.db.milvus.author_rank_repo import MilvusAuthorRankRepository


class TestMilvusAuthorRankRepository:
    """Tests for MilvusAuthorRankRepository"""

    @pytest.fixture
    def repo(self):
        return MilvusAuthorRankRepository()

    @pytest.fixture
    def mock_collection(self):
        collection = Mock()
        collection.num_entities = 100
        collection.load = Mock()
        collection.query = Mock(return_value=[])
        return collection

    def test_count_authors_no_filter(self, repo, mock_collection):
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.count_authors()
            assert result == 100

    def test_count_authors_with_category(self, repo, mock_collection):
        mock_collection.query = Mock(return_value=[{"author_id": f"author_{i}"} for i in range(50)])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.count_authors(category="cs.AI")
            assert result == 50

    def test_get_top_authors_basic(self, repo, mock_collection):
        mock_collection.query = Mock(return_value=[{
            "author_id": "author_a",
            "name": "Author A",
            "paper_count": 10,
            "pagerank": 0.5,
            "degree_centrality": 0.3,
            "betweenness_centrality": 0.2,
            "clustering_coeff": 0.8,
            "primary_category": "cs.AI",
            "first_year": 2020,
            "latest_year": 2024,
            "collaborator_count": 5,
            "calculated_at": "2024-01-01",
        }])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_top_authors(metric="pagerank", limit=10, offset=0)
            assert len(result) == 1

    def test_get_author_by_id_found(self, repo, mock_collection):
        mock_collection.query = Mock(return_value=[{
            "author_id": "author_a",
            "name": "Author A",
        }])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_author_by_id("author_a")
            assert result is not None

    def test_get_author_by_id_not_found(self, repo, mock_collection):
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_author_by_id("nonexistent")
            assert result is None
