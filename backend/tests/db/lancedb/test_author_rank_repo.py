import pytest
from unittest.mock import Mock, patch
import pandas as pd

from app.db.lancedb.author_rank_repo import LanceDBAuthorRankRepository


class TestLanceDBAuthorRankRepository:
    """Tests for LanceDBAuthorRankRepository"""

    @pytest.fixture
    def repo(self):
        return LanceDBAuthorRankRepository()

    @pytest.fixture
    def mock_table(self):
        table = Mock()
        table.count_rows = Mock(return_value=100)
        return table

    @pytest.fixture
    def mock_lance_ds(self):
        ds = Mock()
        return ds

    def test_count_authors_no_filter(self, repo, mock_table):
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.count_authors()
            assert result == 100
            mock_table.count_rows.assert_called_once()

    def test_count_authors_with_category(self, repo, mock_table, mock_lance_ds):
        mock_scanner = Mock()
        mock_table_result = Mock()
        mock_table_result.num_rows = 50
        mock_scanner.to_table = Mock(return_value=mock_table_result)
        mock_lance_ds.scanner = Mock(return_value=mock_scanner)
        mock_table.to_lance = Mock(return_value=mock_lance_ds)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.count_authors(category="cs.AI")
            assert result == 50

    def test_count_authors_with_name_search(self, repo, mock_table, mock_lance_ds):
        mock_scanner = Mock()
        mock_table_result = Mock()
        mock_table_result.num_rows = 10
        mock_scanner.to_table = Mock(return_value=mock_table_result)
        mock_lance_ds.scanner = Mock(return_value=mock_scanner)
        mock_table.to_lance = Mock(return_value=mock_lance_ds)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.count_authors(name_search="LeCun")
            assert result == 10

    def test_get_top_authors_basic(self, repo, mock_table, mock_lance_ds):
        mock_df = pd.DataFrame([{
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
        
        mock_table_result = Mock()
        mock_table_result.to_pandas = Mock(return_value=mock_df)
        mock_scanner = Mock()
        mock_scanner.to_table = Mock(return_value=mock_table_result)
        mock_lance_ds.scanner = Mock(return_value=mock_scanner)
        mock_table.to_lance = Mock(return_value=mock_lance_ds)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_top_authors(metric="pagerank", limit=10, offset=0)
            assert len(result) == 1
            assert result[0]["author_id"] == "author_a"

    def test_get_top_authors_with_filters(self, repo, mock_table, mock_lance_ds):
        mock_df = pd.DataFrame([{
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
        
        mock_table_result = Mock()
        mock_table_result.to_pandas = Mock(return_value=mock_df)
        mock_scanner = Mock()
        mock_scanner.to_table = Mock(return_value=mock_table_result)
        mock_lance_ds.scanner = Mock(return_value=mock_scanner)
        mock_table.to_lance = Mock(return_value=mock_lance_ds)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_top_authors(
                metric="pagerank",
                limit=10,
                offset=0,
                category="cs.AI",
                name_search="Author"
            )
            assert len(result) == 1

    def test_get_author_by_id_found(self, repo, mock_table):
        mock_df = pd.DataFrame([{
            "author_id": "author_a",
            "name": "Author A",
            "paper_count": 10,
            "pagerank": 0.5,
        }])
        
        mock_table.search = Mock(return_value=Mock(
            where=Mock(return_value=Mock(
                limit=Mock(return_value=Mock(to_pandas=Mock(return_value=mock_df))
            )))
        ))
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_author_by_id("author_a")
            assert result is not None
            assert result["author_id"] == "author_a"

    def test_get_author_by_id_not_found(self, repo, mock_table):
        mock_df = pd.DataFrame()
        
        mock_table.search = Mock(return_value=Mock(
            where=Mock(return_value=Mock(
                limit=Mock(return_value=Mock(to_pandas=Mock(return_value=mock_df))
            )))
        ))
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_author_by_id("nonexistent")
            assert result is None

    def test_escape_filter_string(self, repo):
        assert repo._escape_filter_string("test") == "test"
        assert repo._escape_filter_string("test's") == "test\\'s"
        assert repo._escape_filter_string('test"s') == 'test\\"s'
        assert repo._escape_filter_string("test\\path") == "test\\\\path"

    def test_save_rankings(self, repo, mock_table):
        mock_table.merge_insert = Mock(return_value=Mock(
            when_matched_update_all=Mock(return_value=Mock(
                when_not_matched_insert_all=Mock(return_value=Mock(
                    execute=Mock(return_value=None)
                ))
            ))
        ))
        
        with patch.object(repo, '_get_table', return_value=mock_table):
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
            
            result = repo.save_rankings(authors, metrics)
            assert result == 1

    def test_clear_all(self, repo, mock_table):
        mock_df = pd.DataFrame([{"author_id": "author_a"}])
        mock_table.to_pandas = Mock(return_value=mock_df)
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            repo.clear_all()
