import pytest
from unittest.mock import Mock, patch
import json

from app.db.milvus.bookmark_repo import MilvusBookmarkRepository


class TestMilvusBookmarkRepositoryAdd:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_add_success(self, repo, sample_bookmark_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(sample_bookmark_data)
            
            assert "id" in result
            assert result["paper_id"] == sample_bookmark_data["paper_id"]
            assert result["title"] == sample_bookmark_data["title"]
            assert result["authors"] == sample_bookmark_data["authors"]
            mock_collection.insert.assert_called_once()

    def test_add_with_long_title_truncation(self, repo):
        long_title = "A" * 2000
        data = {
            "paper_id": "2301.12345",
            "title": long_title,
            "authors": ["Author"],
        }
        
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(data)
            
            assert len(result["title"]) == 1024

    def test_add_with_long_abstract_truncation(self, repo):
        long_abstract = "A" * 20000
        data = {
            "paper_id": "2301.12345",
            "title": "Test",
            "abstract": long_abstract,
        }
        
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(data)
            
            assert len(result["abstract"]) == 16384

    def test_add_with_none_values(self, repo):
        data = {
            "paper_id": "2301.12345",
            "title": None,
            "authors": None,
            "categories": None,
        }
        
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(data)
            
            assert result["title"] == ""
            assert result["authors"] == []
            assert result["categories"] == []

    def test_add_creates_valid_insert_data(self, repo, sample_bookmark_data):
        mock_collection = Mock()
        inserted_data = None
        
        def capture_insert(data):
            nonlocal inserted_data
            inserted_data = data
        
        mock_collection.insert = Mock(side_effect=capture_insert)
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            repo.add(sample_bookmark_data)
            
            assert inserted_data is not None
            assert len(inserted_data) == 17
            assert inserted_data[1][0] == sample_bookmark_data["paper_id"]


class TestMilvusBookmarkRepositoryRemove:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_remove_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.remove("2301.12345")
            
            assert result is True
            mock_collection.delete.assert_called_once()


class TestMilvusBookmarkRepositoryGet:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_get_existing_bookmark(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_bookmark_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get("test-bookmark-id")
            
            assert result is not None
            assert result["id"] == "test-bookmark-id"
            assert result["title"] == "Test Paper Title"
            assert isinstance(result["authors"], list)

    def test_get_nonexistent_bookmark(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get("nonexistent-id")
            
            assert result is None


class TestMilvusBookmarkRepositoryGetAll:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_get_all_with_data(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {**sample_bookmark_entity, "id": "1", "created_at": "2024-01-03T00:00:00"},
            {**sample_bookmark_entity, "id": "2", "created_at": "2024-01-02T00:00:00"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all(limit=10, offset=0)
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 0
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_get_all_with_pagination(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 5
        mock_collection.query = Mock(return_value=[
            {**sample_bookmark_entity, "id": str(i), "created_at": f"2024-01-0{i}T00:00:00"}
            for i in range(1, 6)
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all(limit=2, offset=1)
            
            assert total == 5
            assert len(results) == 2

    def test_get_all_sorted_by_created_at_desc(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 3
        mock_collection.query = Mock(return_value=[
            {**sample_bookmark_entity, "id": "1", "created_at": "2024-01-01T00:00:00"},
            {**sample_bookmark_entity, "id": "2", "created_at": "2024-01-03T00:00:00"},
            {**sample_bookmark_entity, "id": "3", "created_at": "2024-01-02T00:00:00"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, _ = repo.get_all()
            
            assert results[0]["created_at"] == "2024-01-03T00:00:00"
            assert results[1]["created_at"] == "2024-01-02T00:00:00"
            assert results[2]["created_at"] == "2024-01-01T00:00:00"


class TestMilvusBookmarkRepositoryExists:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_exists_true(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_bookmark_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.exists("test-id")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.exists("nonexistent")
            
            assert result is False


class TestMilvusBookmarkRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_get_by_paper_id_found(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_bookmark_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_by_paper_id("2301.12345v1")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345v1"

    def test_get_by_paper_id_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_by_paper_id("nonexistent")
            
            assert result is None


class TestMilvusBookmarkRepositorySearch:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_search_by_query(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_bookmark_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results = repo.search("machine learning", limit=10)
            
            assert len(results) == 1

    def test_search_no_results(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results = repo.search("nonexistent", limit=10)
            
            assert results == []


class TestMilvusBookmarkRepositoryIsBookmarked:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_is_bookmarked_true(self, repo, sample_bookmark_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_bookmark_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.is_bookmarked("2301.12345")
            
            assert result is True

    def test_is_bookmarked_false(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.is_bookmarked("nonexistent")
            
            assert result is False


class TestMilvusBookmarkRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = MilvusBookmarkRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = MilvusBookmarkRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = MilvusBookmarkRepository._safe_str("test string", max_len=4)
        assert result == "test"

    def test_safe_str_with_int(self):
        result = MilvusBookmarkRepository._safe_str(123)
        assert result == "123"


class TestMilvusBookmarkRepositoryEntityToResponse:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_entity_to_response(self, repo, sample_bookmark_entity):
        result = repo._entity_to_response(sample_bookmark_entity)
        
        assert result["id"] == sample_bookmark_entity["id"]
        assert result["paper_id"] == sample_bookmark_entity["paper_id"]
        assert isinstance(result["authors"], list)
        assert isinstance(result["categories"], list)

    def test_entity_to_response_with_missing_fields(self, repo):
        entity = {"id": "test-id"}
        result = repo._entity_to_response(entity)
        
        assert result["id"] == "test-id"
        assert result["title"] == ""
        assert result["authors"] == []


class TestMilvusBookmarkRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        return MilvusBookmarkRepository()

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_no_bookmarks(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
                "2301.00003": False,
            }

    def test_check_batch_all_bookmarked(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00002"},
            {"paper_id": "2301.00003"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": True,
                "2301.00003": True,
            }

    def test_check_batch_partial_bookmarked(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00003"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": False,
                "2301.00003": True,
                "2301.00004": False,
            }

    def test_check_batch_single_paper_bookmarked(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.12345"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.check_batch(["2301.12345"])
            assert result == {"2301.12345": True}

    def test_check_batch_single_paper_not_bookmarked(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.check_batch(["2301.99999"])
            assert result == {"2301.99999": False}

    def test_check_batch_with_versioned_ids(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        def mock_query(expr=None, output_fields=None):
            if '2301.12345v2' in expr:
                return [{"paper_id": "2301.12345v2"}]
            return []
        
        mock_collection.query = Mock(side_effect=mock_query)
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.check_batch(["2301.12345v2"])
            assert result == {"2301.12345v2": True}
            
            result = repo.check_batch(["2301.12345v1", "2301.12345v3"])
            assert result == {"2301.12345v1": False, "2301.12345v3": False}

    def test_check_batch_handles_exception(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(side_effect=Exception("Query failed"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
            }

    def test_check_batch_large_list(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        bookmarked_results = [
            {"paper_id": f"2301.{i:05d}"}
            for i in range(0, 100, 2)
        ]
        mock_collection.query = Mock(return_value=bookmarked_results)
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = [f"2301.{i:05d}" for i in range(100)]
            result = repo.check_batch(paper_ids)
            
            for i, pid in enumerate(paper_ids):
                expected = i % 2 == 0
                assert result[pid] == expected, f"Failed for {pid}"

    def test_check_batch_query_expression_format(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002"]
            repo.check_batch(paper_ids)
            
            call_args = mock_collection.query.call_args
            expr = call_args[1]['expr']
            
            assert 'paper_id in [' in expr
            assert '"2301.00001"' in expr
            assert '"2301.00002"' in expr
