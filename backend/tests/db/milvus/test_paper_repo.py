import pytest
from unittest.mock import Mock, patch
import json

from app.db.milvus.paper_repo import MilvusPaperRepository


class TestMilvusPaperRepositoryPaperOperations:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_add_paper(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{
            **sample_paper_data,
            "authors": json.dumps(sample_paper_data["authors"]),
            "categories": json.dumps(sample_paper_data["categories"]),
            "fetched_at": "2024-01-15T00:00:00",
        }])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.add(sample_paper_data)
            
            assert result is not None
            assert result["id"] == sample_paper_data["id"]

    def test_remove_paper(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.remove("2301.12345")
            
            assert result is True
            mock_collection.delete.assert_called_once()

    def test_get_paper_by_id_found(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_paper_entity])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.get("2301.12345")
            
            assert result is not None
            assert result["id"] == "2301.12345"

    def test_get_paper_by_id_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.get("nonexistent")
            
            assert result is None

    def test_get_all_papers(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {**sample_paper_entity, "published": "2024-01-02T00:00:00"},
            {**sample_paper_entity, "id": "2301.12346", "published": "2024-01-01T00:00:00"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            results, total = repo.get_all()
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_papers_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 0
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_exists_true(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_paper_entity])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.exists("2301.12345")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.exists("nonexistent")
            
            assert result is False

    def test_insert_paper(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            repo.insert_paper(sample_paper_data)
            
            mock_collection.insert.assert_called_once()

    def test_insert_papers_batch(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        papers = [
            {**sample_paper_data, "id": "2301.12345"},
            {**sample_paper_data, "id": "2301.12346"},
        ]
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.insert_papers_batch(papers)
                
                assert result == 2

    def test_insert_papers_batch_skip_existing(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{"id": "2301.12345"}])
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        papers = [
            {**sample_paper_data, "id": "2301.12345"},
            {**sample_paper_data, "id": "2301.12346"},
        ]
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.insert_papers_batch(papers)
                
                assert result == 1

    def test_insert_papers_batch_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.insert_papers_batch([])
            
            assert result == 0

    def test_get_total_paper_count(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 100
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.get_total_paper_count()
            
            assert result == 100

    def test_get_all_paper_ids(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {"id": "2301.12345"},
            {"id": "2301.12346"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.get_all_paper_ids()
            
            assert len(result) == 2
            assert "2301.12345" in result

    def test_get_papers_by_ids(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_paper_entity])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_papers_by_ids(["2301.12345"])
                
                assert len(result) == 1
                assert result[0]["id"] == "2301.12345"

    def test_get_papers_by_ids_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.get_papers_by_ids([])
            
            assert result == []


class TestMilvusPaperRepositoryDateQuery:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_query_papers_by_date(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_paper_entity, "published": "2024-01-15T10:00:00"},
            {**sample_paper_entity, "id": "2301.12346", "published": "2024-01-15T12:00:00"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            results, total = repo.query_papers_by_date("2024-01-15")
            
            assert total == 2
            assert len(results) == 2

    def test_query_papers_by_date_with_category(self, repo, sample_paper_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_paper_entity, "categories": '["cs.AI", "cs.LG"]'},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            results, total = repo.query_papers_by_date("2024-01-15", category="cs.AI")
            
            assert total == 1

    def test_query_papers_by_date_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            results, total = repo.query_papers_by_date("2024-01-15")
            
            assert total == 0
            assert results == []

    def test_get_paper_ids_by_date_range(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"id": "2301.12345", "published": "2024-01-15T00:00:00"},
            {"id": "2301.12346", "published": "2024-01-16T00:00:00"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_paper_ids_by_date_range(
                    date_from="2024-01-15", date_to="2024-01-16"
                )
                
                assert len(result) == 2

    def test_get_paper_ids_by_date_range_single_date(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"id": "2301.12345", "published": "2024-01-15T10:00:00"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_paper_ids_by_date_range(date="2024-01-15")
                
                assert len(result) == 1

    def test_get_paper_ids_by_filters(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"id": "2301.12345"},
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_paper_ids_by_filters(category="cs.AI")
                
                assert len(result) == 1


class TestMilvusPaperRepositoryDateIndex:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_get_date_index_found(self, repo, sample_date_index_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_date_index_entity])
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            result = repo.get_date_index("2024-01-15")
            
            assert result is not None
            assert result["date"] == "2024-01-15"
            assert result["total_count"] == 100

    def test_get_date_index_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            result = repo.get_date_index("2024-01-15")
            
            assert result is None

    def test_insert_date_index(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            repo.insert_date_index("2024-01-15", 100)
            
            mock_collection.insert.assert_called_once()

    def test_insert_date_index_updates_existing(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{"date": "2024-01-15"}])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            repo.insert_date_index("2024-01-15", 100)
            
            mock_collection.delete.assert_called_once()
            mock_collection.insert.assert_called_once()

    def test_delete_date_index(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            repo.delete_date_index("2024-01-15")
            
            mock_collection.delete.assert_called_once()

    def test_delete_all_date_index(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            repo.delete_all_date_index()
            
            mock_collection.delete.assert_called_once()

    def test_get_all_date_indexes(self, repo, sample_date_index_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {**sample_date_index_entity, "date": "2024-01-16"},
            {**sample_date_index_entity, "date": "2024-01-15"},
        ])
        
        with patch.object(repo, '_get_date_index_collection', return_value=mock_collection):
            result = repo.get_all_date_indexes()
            
            assert len(result) == 2
            assert result[0]["date"] == "2024-01-16"


class TestMilvusPaperRepositoryEmbeddingIndex:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_get_embedding_index_found(self, repo, sample_embedding_index_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_embedding_index_entity])
        
        with patch.object(repo, '_get_embedding_index_collection', return_value=mock_collection):
            result = repo.get_embedding_index("2024-01-15")
            
            assert result is not None
            assert result["date"] == "2024-01-15"
            assert result["model_name"] == "text-embedding-ada-002"

    def test_get_embedding_index_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_embedding_index_collection', return_value=mock_collection):
            result = repo.get_embedding_index("2024-01-15")
            
            assert result is None

    def test_insert_embedding_index(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_embedding_index_collection', return_value=mock_collection):
            repo.insert_embedding_index("2024-01-15", 100, "test-model")
            
            mock_collection.insert.assert_called_once()

    def test_get_all_embedding_indexes(self, repo, sample_embedding_index_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {**sample_embedding_index_entity, "date": "2024-01-16"},
            {**sample_embedding_index_entity, "date": "2024-01-15"},
        ])
        
        with patch.object(repo, '_get_embedding_index_collection', return_value=mock_collection):
            result = repo.get_all_embedding_indexes()
            
            assert len(result) == 2

    def test_delete_embedding_index(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_embedding_index_collection', return_value=mock_collection):
            repo.delete_embedding_index("2024-01-15")
            
            mock_collection.delete.assert_called_once()


class TestMilvusPaperRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = MilvusPaperRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = MilvusPaperRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = MilvusPaperRepository._safe_str("test string", max_len=4)
        assert result == "test"


class TestMilvusPaperRepositoryGetNextDate:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

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


class TestMilvusPaperRepositoryUpsertPapersBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_upsert_papers_batch_insert_new(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        papers = [
            {**sample_paper_data, "id": "2301.00001"},
            {**sample_paper_data, "id": "2301.00002"},
        ]
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.upsert_papers_batch(papers)
            
            assert result == 2
            mock_collection.insert.assert_called_once()
            mock_collection.flush.assert_called_once()

    def test_upsert_papers_batch_empty_list(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.upsert_papers_batch([])
            
            assert result == 0

    def test_upsert_papers_batch_single_paper(self, repo, sample_paper_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        papers = [{**sample_paper_data, "id": "2301.00001"}]
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            result = repo.upsert_papers_batch(papers)
            
            assert result == 1


class TestMilvusPaperRepositoryGetPapersByAuthor:
    @pytest.fixture
    def repo(self):
        return MilvusPaperRepository()

    def test_get_papers_by_author_single_author(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{
            "id": "2301.00001",
            "title": "Paper 1",
            "abstract": "Abstract 1",
            "authors": json.dumps(["John Smith"]),
            "primary_category": "cs.AI",
            "categories": json.dumps(["cs.AI"]),
            "published": "2024-01-01T00:00:00",
            "updated": "2024-01-01T00:00:00",
            "pdf_url": "url1",
            "abs_url": "url1",
            "comment": "",
            "journal_ref": "",
            "doi": "",
            "fetched_at": "2024-01-01T00:00:00",
        }])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("John Smith")
                
                assert total == 1
                assert len(papers) == 1
                assert papers[0]["id"] == "2301.00001"
                assert "John Smith" in papers[0]["authors"]

    def test_get_papers_by_author_multiple_papers(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "id": "2301.00001",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": json.dumps(["John Smith", "Jane Doe"]),
                "primary_category": "cs.AI",
                "categories": json.dumps(["cs.AI"]),
                "published": "2024-01-01T00:00:00",
                "updated": "2024-01-01T00:00:00",
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
                "authors": json.dumps(["John Smith"]),
                "primary_category": "cs.LG",
                "categories": json.dumps(["cs.LG"]),
                "published": "2024-01-02T00:00:00",
                "updated": "2024-01-02T00:00:00",
                "pdf_url": "url2",
                "abs_url": "url2",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-02T00:00:00",
            },
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("John Smith")
                
                assert total == 2
                assert len(papers) == 2
                paper_ids = [p["id"] for p in papers]
                assert "2301.00001" in paper_ids
                assert "2301.00002" in paper_ids

    def test_get_papers_by_author_sorted_by_date(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "id": "2301.00001",
                "title": "Older Paper",
                "abstract": "Abstract 1",
                "authors": json.dumps(["John Smith"]),
                "primary_category": "cs.AI",
                "categories": json.dumps(["cs.AI"]),
                "published": "2024-01-01T00:00:00",
                "updated": "2024-01-01T00:00:00",
                "pdf_url": "url1",
                "abs_url": "url1",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "Newer Paper",
                "abstract": "Abstract 2",
                "authors": json.dumps(["John Smith"]),
                "primary_category": "cs.LG",
                "categories": json.dumps(["cs.LG"]),
                "published": "2024-06-01T00:00:00",
                "updated": "2024-06-01T00:00:00",
                "pdf_url": "url2",
                "abs_url": "url2",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-06-01T00:00:00",
            },
            {
                "id": "2301.00003",
                "title": "Middle Paper",
                "abstract": "Abstract 3",
                "authors": json.dumps(["John Smith"]),
                "primary_category": "cs.CV",
                "categories": json.dumps(["cs.CV"]),
                "published": "2024-03-01T00:00:00",
                "updated": "2024-03-01T00:00:00",
                "pdf_url": "url3",
                "abs_url": "url3",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-03-01T00:00:00",
            },
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("John Smith")
                
                assert total == 3
                assert papers[0]["id"] == "2301.00002"
                assert papers[1]["id"] == "2301.00003"
                assert papers[2]["id"] == "2301.00001"

    def test_get_papers_by_author_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("Unknown Author")
                
                assert total == 0
                assert len(papers) == 0

    def test_get_papers_by_author_pagination(self, repo):
        papers_data = []
        for i in range(10):
            papers_data.append({
                "id": f"2301.0000{i}",
                "title": f"Paper {i}",
                "abstract": f"Abstract {i}",
                "authors": json.dumps(["John Smith"]),
                "primary_category": "cs.AI",
                "categories": json.dumps(["cs.AI"]),
                "published": f"2024-01-{i+1:02d}T00:00:00",
                "updated": f"2024-01-{i+1:02d}T00:00:00",
                "pdf_url": f"url{i}",
                "abs_url": f"url{i}",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": f"2024-01-{i+1:02d}T00:00:00",
            })
        
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=papers_data)
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("John Smith", start=0, max_results=5)
                
                assert total == 10
                assert len(papers) == 5
                
                papers2, total2 = repo.get_papers_by_author("John Smith", start=5, max_results=5)
                
                assert total2 == 10
                assert len(papers2) == 5

    def test_get_papers_by_author_coauthor(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "id": "2301.00001",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": json.dumps(["John Smith", "Jane Doe", "Bob Wilson"]),
                "primary_category": "cs.AI",
                "categories": json.dumps(["cs.AI"]),
                "published": "2024-01-01T00:00:00",
                "updated": "2024-01-01T00:00:00",
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
                "authors": json.dumps(["Jane Doe", "Alice Brown"]),
                "primary_category": "cs.LG",
                "categories": json.dumps(["cs.LG"]),
                "published": "2024-01-02T00:00:00",
                "updated": "2024-01-02T00:00:00",
                "pdf_url": "url2",
                "abs_url": "url2",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "fetched_at": "2024-01-02T00:00:00",
            },
        ])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("Jane Doe")
                
                assert total == 2
                assert len(papers) == 2

    def test_get_papers_by_author_empty_database(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_papers_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                papers, total = repo.get_papers_by_author("John Smith")
                
                assert total == 0
                assert len(papers) == 0
