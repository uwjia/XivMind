import pytest
from unittest.mock import Mock, patch
import pandas as pd
import json

from app.db.lancedb.paper_repo import LanceDBPaperRepository


class TestLanceDBPaperRepositoryPaperOperations:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperRepository()

    def test_add_paper(self, repo, sample_paper_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=pd.DataFrame([{
            "id": sample_paper_data["id"],
            "title": sample_paper_data["title"],
            "abstract": sample_paper_data["abstract"],
            "authors": json.dumps(sample_paper_data["authors"]),
            "primary_category": sample_paper_data["primary_category"],
            "categories": json.dumps(sample_paper_data["categories"]),
            "published": sample_paper_data["published"],
            "updated": sample_paper_data["updated"],
            "pdf_url": sample_paper_data["pdf_url"],
            "abs_url": sample_paper_data["abs_url"],
            "comment": sample_paper_data["comment"],
            "journal_ref": sample_paper_data["journal_ref"],
            "doi": sample_paper_data["doi"],
            "fetched_at": "2024-01-01T00:00:00",
        }]))
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.add(sample_paper_data)
            
            assert result is not None
            assert result["id"] == sample_paper_data["id"]

    def test_remove_paper(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.remove("2301.12345")
            
            assert result is True
            mock_table.delete.assert_called_once()

    def test_get_paper_by_id_found(self, repo, sample_paper_data):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": sample_paper_data["id"],
            "title": sample_paper_data["title"],
            "abstract": sample_paper_data["abstract"],
            "authors": json.dumps(sample_paper_data["authors"]),
            "primary_category": sample_paper_data["primary_category"],
            "categories": json.dumps(sample_paper_data["categories"]),
            "published": sample_paper_data["published"],
            "updated": sample_paper_data["updated"],
            "pdf_url": sample_paper_data["pdf_url"],
            "abs_url": sample_paper_data["abs_url"],
            "comment": sample_paper_data["comment"],
            "journal_ref": sample_paper_data["journal_ref"],
            "doi": sample_paper_data["doi"],
            "fetched_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get("2301.12345")
            
            assert result is not None
            assert result["id"] == "2301.12345"

    def test_get_paper_by_id_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get("nonexistent")
            
            assert result is None

    def test_get_all_papers(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "2301.00001",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": "[]",
                "primary_category": "cs.AI",
                "categories": "[]",
                "published": "2024-01-02T00:00:00",
                "updated": "2024-01-02T00:00:00",
                "pdf_url": "url1",
                "abs_url": "url1",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "Paper 2",
                "abstract": "Abstract 2",
                "authors": "[]",
                "primary_category": "cs.LG",
                "categories": "[]",
                "published": "2024-01-01T00:00:00",
                "updated": "2024-01-01T00:00:00",
                "pdf_url": "url2",
                "abs_url": "url2",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-01T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            results, total = repo.get_all()
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_papers_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_exists_true(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "2301.12345"}])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.exists("2301.12345")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.exists("nonexistent")
            
            assert result is False

    def test_insert_paper(self, repo, sample_paper_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            repo.insert_paper(sample_paper_data)
            
            mock_table.add.assert_called_once()

    def test_insert_papers_batch(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.add = Mock()
        
        papers = [
            {
                "id": "2301.12345",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": ["Author 1"],
                "primary_category": "cs.AI",
                "categories": ["cs.AI"],
                "published": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.12346",
                "title": "Paper 2",
                "abstract": "Abstract 2",
                "authors": ["Author 2"],
                "primary_category": "cs.LG",
                "categories": ["cs.LG"],
                "published": "2024-01-01T00:00:00",
            },
        ]
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.insert_papers_batch(papers)
            
            assert result == 2

    def test_insert_papers_batch_skip_existing(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "2301.12345"}])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.add = Mock()
        
        papers = [
            {"id": "2301.12345", "title": "Existing Paper"},
            {"id": "2301.12346", "title": "New Paper"},
        ]
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.insert_papers_batch(papers)
            
            assert result == 1

    def test_insert_papers_batch_empty(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.insert_papers_batch([])
            
            assert result == 0

    def test_get_total_paper_count(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": str(i)} for i in range(5)])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_total_paper_count()
            
            assert result == 5

    def test_get_all_paper_ids(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"id": "2301.12345"},
            {"id": "2301.12346"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_all_paper_ids()
            
            assert len(result) == 2
            assert "2301.12345" in result

    def test_get_papers_by_ids(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "2301.12345",
                "title": "Paper 1",
                "abstract": "Abstract",
                "authors": "[]",
                "primary_category": "cs.AI",
                "categories": "[]",
                "published": "2024-01-01T00:00:00",
                "updated": "2024-01-01T00:00:00",
                "pdf_url": "url",
                "abs_url": "url",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-01T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_papers_by_ids(["2301.12345"])
            
            assert len(result) == 1
            assert result[0]["id"] == "2301.12345"

    def test_get_papers_by_ids_empty(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_papers_by_ids([])
            
            assert result == []


class TestLanceDBPaperRepositoryDateQuery:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperRepository()

    def test_query_papers_by_date(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "2301.12345",
                "title": "Paper 1",
                "abstract": "Abstract",
                "authors": "[]",
                "primary_category": "cs.AI",
                "categories": '["cs.AI"]',
                "published": "2024-01-15T10:00:00",
                "updated": "2024-01-15T10:00:00",
                "pdf_url": "url",
                "abs_url": "url",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-15T00:00:00",
            },
            {
                "id": "2301.12346",
                "title": "Paper 2",
                "abstract": "Abstract",
                "authors": "[]",
                "primary_category": "cs.LG",
                "categories": '["cs.LG"]',
                "published": "2024-01-15T12:00:00",
                "updated": "2024-01-15T12:00:00",
                "pdf_url": "url",
                "abs_url": "url",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-15T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            results, total = repo.query_papers_by_date("2024-01-15")
            
            assert total == 2
            assert len(results) == 2

    def test_query_papers_by_date_with_category(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "2301.12345",
                "title": "Paper 1",
                "abstract": "Abstract",
                "authors": "[]",
                "primary_category": "cs.AI",
                "categories": '["cs.AI", "cs.LG"]',
                "published": "2024-01-15T10:00:00",
                "updated": "2024-01-15T10:00:00",
                "pdf_url": "url",
                "abs_url": "url",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-15T00:00:00",
            },
            {
                "id": "2301.12346",
                "title": "Paper 2",
                "abstract": "Abstract",
                "authors": "[]",
                "primary_category": "cs.LG",
                "categories": '["cs.LG"]',
                "published": "2024-01-15T12:00:00",
                "updated": "2024-01-15T12:00:00",
                "pdf_url": "url",
                "abs_url": "url",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-15T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            results, total = repo.query_papers_by_date("2024-01-15", category="cs.AI")
            
            assert total == 1

    def test_query_papers_by_date_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame(columns=["id", "title", "abstract", "authors", "primary_category", 
                                   "categories", "published", "updated", "pdf_url", "abs_url",
                                   "comment", "journal_ref", "doi", "fetched_at"])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            results, total = repo.query_papers_by_date("2024-01-15")
            
            assert total == 0
            assert results == []

    def test_get_paper_ids_by_date_range(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"id": "2301.12345", "published": "2024-01-15T00:00:00"},
            {"id": "2301.12346", "published": "2024-01-15T12:00:00"},
            {"id": "2301.12347", "published": "2024-01-17T00:00:00"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_paper_ids_by_date_range(
                date_from="2024-01-15", date_to="2024-01-16"
            )
            
            assert len(result) == 2

    def test_get_paper_ids_by_date_range_single_date(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"id": "2301.12345", "published": "2024-01-15T10:00:00"},
            {"id": "2301.12346", "published": "2024-01-16T00:00:00"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_paper_ids_by_date_range(date="2024-01-15")
            
            assert len(result) == 1

    def test_get_paper_ids_by_filters(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "2301.12345",
                "categories": '["cs.AI", "cs.LG"]',
                "published": "2024-01-15T00:00:00",
            },
            {
                "id": "2301.12346",
                "categories": '["cs.LG"]',
                "published": "2024-01-16T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_papers_table', return_value=mock_table):
            result = repo.get_paper_ids_by_filters(category="cs.AI")
            
            assert len(result) == 1


class TestLanceDBPaperRepositoryDateIndex:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperRepository()

    def test_get_date_index_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "date": "2024-01-15",
            "total_count": 100,
            "fetched_at": "2024-01-15T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            result = repo.get_date_index("2024-01-15")
            
            assert result is not None
            assert result["date"] == "2024-01-15"
            assert result["total_count"] == 100

    def test_get_date_index_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            result = repo.get_date_index("2024-01-15")
            
            assert result is None

    def test_insert_date_index(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            repo.insert_date_index("2024-01-15", 100)
            
            mock_table.delete.assert_called_once()
            mock_table.add.assert_called_once()

    def test_delete_date_index(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            repo.delete_date_index("2024-01-15")
            
            mock_table.delete.assert_called_once()

    def test_delete_all_date_index(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"date": "2024-01-15"},
            {"date": "2024-01-16"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            repo.delete_all_date_index()
            
            assert mock_table.delete.call_count == 2

    def test_get_all_date_indexes(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"date": "2024-01-16", "total_count": 100, "fetched_at": "2024-01-16T00:00:00"},
            {"date": "2024-01-15", "total_count": 50, "fetched_at": "2024-01-15T00:00:00"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_date_index_table', return_value=mock_table):
            result = repo.get_all_date_indexes()
            
            assert len(result) == 2
            assert result[0]["date"] == "2024-01-16"


class TestLanceDBPaperRepositoryEmbeddingIndex:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperRepository()

    def test_get_embedding_index_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "date": "2024-01-15",
            "total_count": 100,
            "generated_at": "2024-01-15T00:00:00",
            "model_name": "text-embedding-ada-002",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_embedding_index_table', return_value=mock_table):
            result = repo.get_embedding_index("2024-01-15")
            
            assert result is not None
            assert result["date"] == "2024-01-15"
            assert result["model_name"] == "text-embedding-ada-002"

    def test_get_embedding_index_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_embedding_index_table', return_value=mock_table):
            result = repo.get_embedding_index("2024-01-15")
            
            assert result is None

    def test_insert_embedding_index(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_embedding_index_table', return_value=mock_table):
            repo.insert_embedding_index("2024-01-15", 100, "test-model")
            
            mock_table.delete.assert_called_once()
            mock_table.add.assert_called_once()

    def test_get_all_embedding_indexes(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "date": "2024-01-16",
                "total_count": 100,
                "generated_at": "2024-01-16T00:00:00",
                "model_name": "test-model",
            },
            {
                "date": "2024-01-15",
                "total_count": 50,
                "generated_at": "2024-01-15T00:00:00",
                "model_name": "test-model",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_embedding_index_table', return_value=mock_table):
            result = repo.get_all_embedding_indexes()
            
            assert len(result) == 2
            assert result[0]["date"] == "2024-01-16"

    def test_delete_embedding_index(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_embedding_index_table', return_value=mock_table):
            repo.delete_embedding_index("2024-01-15")
            
            mock_table.delete.assert_called_once()


class TestLanceDBPaperRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = LanceDBPaperRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = LanceDBPaperRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = LanceDBPaperRepository._safe_str("test string", max_len=4)
        assert result == "test"


class TestLanceDBPaperRepositoryGetNextDate:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperRepository()

    def test_get_next_date(self, repo):
        result = repo._get_next_date("2024-01-15")
        assert result == "2024-01-16"

    def test_get_next_date_month_end(self, repo):
        result = repo._get_next_date("2024-01-31")
        assert result == "2024-02-01"

    def test_get_next_date_year_end(self, repo):
        result = repo._get_next_date("2024-12-31")
        assert result == "2025-01-01"

    def test_get_next_date_invalid_format(self, repo):
        result = repo._get_next_date("invalid-date")
        assert result == "invalid-date"
