import pytest
from unittest.mock import Mock, patch
import pandas as pd
import json

from app.db.lancedb.bookmark_repo import LanceDBBookmarkRepository


class TestLanceDBBookmarkRepositoryAdd:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_add_success(self, repo, sample_bookmark_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(sample_bookmark_data)
            
            assert "id" in result
            assert result["paper_id"] == sample_bookmark_data["paper_id"]
            assert result["title"] == sample_bookmark_data["title"]
            assert result["authors"] == sample_bookmark_data["authors"]
            mock_table.add.assert_called_once()

    def test_add_with_long_title_truncation(self, repo):
        long_title = "A" * 2000
        data = {
            "paper_id": "2301.12345",
            "title": long_title,
            "authors": ["Author"],
        }
        
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(data)
            
            assert len(result["title"]) == 1024

    def test_add_with_long_abstract_truncation(self, repo):
        long_abstract = "A" * 20000
        data = {
            "paper_id": "2301.12345",
            "title": "Test",
            "abstract": long_abstract,
        }
        
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(data)
            
            assert len(result["abstract"]) == 16384

    def test_add_with_none_values(self, repo):
        data = {
            "paper_id": "2301.12345",
            "title": None,
            "authors": None,
            "categories": None,
        }
        
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(data)
            
            assert result["title"] == ""
            assert result["authors"] == []
            assert result["categories"] == []

    def test_add_creates_valid_record(self, repo, sample_bookmark_data):
        mock_table = Mock()
        added_record = None
        
        def capture_add(records):
            nonlocal added_record
            added_record = records[0]
        
        mock_table.add = Mock(side_effect=capture_add)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            repo.add(sample_bookmark_data)
            
            assert "id" in added_record
            assert "created_at" in added_record
            assert "embedding" in added_record
            assert len(added_record["embedding"]) == 1536
            assert isinstance(added_record["authors"], str)
            assert isinstance(added_record["categories"], str)


class TestLanceDBBookmarkRepositoryRemove:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_remove_success(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.remove("2301.12345")
            
            assert result is True
            mock_table.delete.assert_called_once_with("paper_id = '2301.12345'")


class TestLanceDBBookmarkRepositoryGet:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_get_existing_bookmark(self, repo, sample_bookmark_data):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-id-123",
            "paper_id": sample_bookmark_data["paper_id"],
            "arxiv_id": sample_bookmark_data["arxiv_id"],
            "title": sample_bookmark_data["title"],
            "authors": json.dumps(sample_bookmark_data["authors"]),
            "abstract": sample_bookmark_data["abstract"],
            "comment": sample_bookmark_data["comment"],
            "journal_ref": sample_bookmark_data["journal_ref"],
            "doi": sample_bookmark_data["doi"],
            "primary_category": sample_bookmark_data["primary_category"],
            "categories": json.dumps(sample_bookmark_data["categories"]),
            "pdf_url": sample_bookmark_data["pdf_url"],
            "abs_url": sample_bookmark_data["abs_url"],
            "published": sample_bookmark_data["published"],
            "updated": sample_bookmark_data["updated"],
            "created_at": "2024-01-03T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get("test-id-123")
            
            assert result is not None
            assert result["id"] == "test-id-123"
            assert result["title"] == sample_bookmark_data["title"]
            assert isinstance(result["authors"], list)

    def test_get_nonexistent_bookmark(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get("nonexistent-id")
            
            assert result is None


class TestLanceDBBookmarkRepositoryGetAll:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_get_all_with_data(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "title": "Paper 1",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "cs.AI",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "2024-01-03T00:00:00",
            },
            {
                "id": "2",
                "paper_id": "2301.00002",
                "title": "Paper 2",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "cs.AI",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "2024-01-02T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=2)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all(limit=10, offset=0)
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=0)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_get_all_with_pagination(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": str(i),
                "paper_id": f"2301.0000{i}",
                "title": f"Paper {i}",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "cs.AI",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": f"2024-01-0{i}T00:00:00",
            }
            for i in range(1, 6)
        ])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=5)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all(limit=2, offset=1)
            
            assert total == 5
            assert len(results) == 2

    def test_get_all_sorted_by_created_at_desc(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "title": "Old Paper",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "id": "2",
                "paper_id": "2301.00002",
                "title": "New Paper",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "2024-01-03T00:00:00",
            },
            {
                "id": "3",
                "paper_id": "2301.00003",
                "title": "Middle Paper",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "2024-01-02T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, _ = repo.get_all()
            
            assert results[0]["title"] == "New Paper"
            assert results[1]["title"] == "Middle Paper"
            assert results[2]["title"] == "Old Paper"


class TestLanceDBBookmarkRepositoryExists:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_exists_true(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "test-id"}])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.exists("test-id")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.exists("nonexistent")
            
            assert result is False


class TestLanceDBBookmarkRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_get_by_paper_id_found(self, repo, sample_bookmark_data):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-id",
            "paper_id": sample_bookmark_data["paper_id"],
            "arxiv_id": sample_bookmark_data["arxiv_id"],
            "title": sample_bookmark_data["title"],
            "authors": json.dumps(sample_bookmark_data["authors"]),
            "abstract": sample_bookmark_data["abstract"],
            "comment": "",
            "journal_ref": "",
            "doi": "",
            "primary_category": sample_bookmark_data["primary_category"],
            "categories": json.dumps(sample_bookmark_data["categories"]),
            "pdf_url": sample_bookmark_data["pdf_url"],
            "abs_url": sample_bookmark_data["abs_url"],
            "published": sample_bookmark_data["published"],
            "updated": sample_bookmark_data["updated"],
            "created_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_by_paper_id(sample_bookmark_data["paper_id"])
            
            assert result is not None
            assert result["paper_id"] == sample_bookmark_data["paper_id"]

    def test_get_by_paper_id_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_by_paper_id("nonexistent")
            
            assert result is None


class TestLanceDBBookmarkRepositorySearch:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_search_by_title(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "title": "Machine Learning Paper",
                "authors": "[]",
                "abstract": "About other things",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "",
            },
            {
                "id": "2",
                "paper_id": "2301.00002",
                "title": "Other Paper",
                "authors": "[]",
                "abstract": "About machine learning",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results = repo.search("machine learning", limit=10)
            
            assert len(results) == 2

    def test_search_by_paper_id(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.12345",
                "title": "Paper Title",
                "authors": "[]",
                "abstract": "Abstract",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results = repo.search("2301.12345", limit=10)
            
            assert len(results) == 1
            assert results[0]["paper_id"] == "2301.12345"

    def test_search_no_results(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "title": "Paper Title",
                "authors": "[]",
                "abstract": "Abstract",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results = repo.search("nonexistent", limit=10)
            
            assert len(results) == 0

    def test_search_case_insensitive(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "title": "MACHINE LEARNING",
                "authors": "[]",
                "abstract": "",
                "comment": "",
                "journal_ref": "",
                "doi": "",
                "primary_category": "",
                "categories": "[]",
                "pdf_url": "",
                "abs_url": "",
                "published": "",
                "updated": "",
                "created_at": "",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results = repo.search("machine", limit=10)
            
            assert len(results) == 1


class TestLanceDBBookmarkRepositoryIsBookmarked:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_is_bookmarked_true(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "test-id"}])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.is_bookmarked("2301.12345")
            
            assert result is True

    def test_is_bookmarked_false(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.is_bookmarked("nonexistent")
            
            assert result is False


class TestLanceDBBookmarkRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = LanceDBBookmarkRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = LanceDBBookmarkRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = LanceDBBookmarkRepository._safe_str("test string", max_len=4)
        assert result == "test"

    def test_safe_str_with_int(self):
        result = LanceDBBookmarkRepository._safe_str(123)
        assert result == "123"


class TestLanceDBBookmarkRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBBookmarkRepository()

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_no_bookmarks(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "other.paper"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
                "2301.00003": False,
            }

    def test_check_batch_all_bookmarked(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00002"},
            {"paper_id": "2301.00003"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": True,
                "2301.00003": True,
            }

    def test_check_batch_partial_bookmarked(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00003"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": False,
                "2301.00003": True,
                "2301.00004": False,
            }

    def test_check_batch_single_paper_bookmarked(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.12345"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.check_batch(["2301.12345"])
            assert result == {"2301.12345": True}

    def test_check_batch_single_paper_not_bookmarked(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.check_batch(["2301.99999"])
            assert result == {"2301.99999": False}

    def test_check_batch_with_versioned_ids(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.12345v2"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.check_batch(["2301.12345v2"])
            assert result == {"2301.12345v2": True}
            
            result = repo.check_batch(["2301.12345v1", "2301.12345v3"])
            assert result == {"2301.12345v1": False, "2301.12345v3": False}

    def test_check_batch_empty_table(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
            }

    def test_check_batch_large_list(self, repo):
        mock_table = Mock()
        bookmarked_ids = [f"2301.{i:05d}" for i in range(0, 100, 2)]
        df = pd.DataFrame([{"paper_id": pid} for pid in bookmarked_ids])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = [f"2301.{i:05d}" for i in range(100)]
            result = repo.check_batch(paper_ids)
            
            for i, pid in enumerate(paper_ids):
                expected = i % 2 == 0
                assert result[pid] == expected, f"Failed for {pid}"
