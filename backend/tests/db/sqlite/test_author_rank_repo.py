import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from app.db.sqlite.author_rank_repo import SQLiteAuthorRankRepository


class TestSQLiteAuthorRankRepository:
    """Tests for SQLiteAuthorRankRepository"""

    @pytest.fixture
    def repo(self, tmp_path):
        with patch('app.db.sqlite.author_rank_repo.get_settings') as mock_settings:
            mock_settings.return_value = Mock(DATA_DIR=str(tmp_path))
            return SQLiteAuthorRankRepository()

    def test_count_authors_no_filter(self, repo):
        result = repo.count_authors()
        assert result == 0

    def test_save_and_get_rankings(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                first_paper_year=2020,
                latest_paper_year=2024,
                categories={"cs.AI": 10},
                collaborator_count=5,
            )
        }
        metrics = {
            "pagerank": {"author_a": 0.5},
            "degree": {"author_a": 0.3},
            "betweenness": {"author_a": 0.2},
            "clustering": {"author_a": 0.8},
        }
        
        count = repo.save_rankings(authors, metrics)
        assert count == 1
        
        result = repo.count_authors()
        assert result == 1

    def test_get_top_authors(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
            "author_b": AuthorStats(
                display_name="Author B",
                paper_count=5,
                categories={"cs.LG": 5},
            ),
        }
        metrics = {
            "pagerank": {"author_a": 0.5, "author_b": 0.3},
            "degree": {"author_a": 0.3, "author_b": 0.2},
            "betweenness": {"author_a": 0.2, "author_b": 0.1},
            "clustering": {"author_a": 0.8, "author_b": 0.6},
        }
        
        repo.save_rankings(authors, metrics)
        
        result = repo.get_top_authors(metric="pagerank", limit=10, offset=0)
        assert len(result) == 2
        assert result[0]["author_id"] == "author_a"

    def test_get_top_authors_with_category_filter(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
            "author_b": AuthorStats(
                display_name="Author B",
                paper_count=5,
                categories={"cs.LG": 5},
            ),
        }
        metrics = {
            "pagerank": {"author_a": 0.5, "author_b": 0.3},
            "degree": {"author_a": 0.3, "author_b": 0.2},
            "betweenness": {"author_a": 0.2, "author_b": 0.1},
            "clustering": {"author_a": 0.8, "author_b": 0.6},
        }
        
        repo.save_rankings(authors, metrics)
        
        result = repo.get_top_authors(metric="pagerank", limit=10, offset=0, category="cs.AI")
        assert len(result) == 1
        assert result[0]["author_id"] == "author_a"

    def test_get_top_authors_with_name_search(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
            "author_b": AuthorStats(
                display_name="Different Name",
                paper_count=5,
                categories={"cs.LG": 5},
            ),
        }
        metrics = {
            "pagerank": {"author_a": 0.5, "author_b": 0.3},
            "degree": {"author_a": 0.3, "author_b": 0.2},
            "betweenness": {"author_a": 0.2, "author_b": 0.1},
            "clustering": {"author_a": 0.8, "author_b": 0.6},
        }
        
        repo.save_rankings(authors, metrics)
        
        result = repo.get_top_authors(metric="pagerank", limit=10, offset=0, name_search="Author")
        assert len(result) == 1
        assert result[0]["author_id"] == "author_a"

    def test_get_author_by_id(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
        }
        metrics = {
            "pagerank": {"author_a": 0.5},
            "degree": {"author_a": 0.3},
            "betweenness": {"author_a": 0.2},
            "clustering": {"author_a": 0.8},
        }
        
        repo.save_rankings(authors, metrics)
        
        result = repo.get_author_by_id("author_a")
        assert result is not None
        assert result["name"] == "Author A"
        
        result = repo.get_author_by_id("nonexistent")
        assert result is None

    def test_clear_all(self, repo):
        from app.services.author_analysis_service import AuthorStats
        
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
        }
        metrics = {
            "pagerank": {"author_a": 0.5},
            "degree": {"author_a": 0.3},
            "betweenness": {"author_a": 0.2},
            "clustering": {"author_a": 0.8},
        }
        
        repo.save_rankings(authors, metrics)
        assert repo.count_authors() == 1
        
        repo.clear_all()
        assert repo.count_authors() == 0

    def test_disambiguation_stats(self, repo):
        stats = {"total_names": 100, "names_disambiguated": 10}
        repo.save_disambiguation_stats(stats)
        
        result = repo.get_disambiguation_stats()
        assert result["total_names"] == 100
