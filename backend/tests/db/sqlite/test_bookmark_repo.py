import pytest
import tempfile
import os

from app.db.sqlite.bookmark_repo import SQLiteBookmarkRepository


class TestSQLiteBookmarkRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_bookmarks.db")
            repo = SQLiteBookmarkRepository(db_path)
            yield repo

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_no_bookmarks(self, repo):
        paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": False,
            "2301.00002": False,
            "2301.00003": False,
        }

    def test_check_batch_all_bookmarked(self, repo):
        for i in range(1, 4):
            repo.add({
                "paper_id": f"2301.0000{i}",
                "title": f"Test Paper {i}",
            })
        
        paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": True,
            "2301.00002": True,
            "2301.00003": True,
        }

    def test_check_batch_partial_bookmarked(self, repo):
        repo.add({
            "paper_id": "2301.00001",
            "title": "Bookmarked Paper",
        })
        repo.add({
            "paper_id": "2301.00003",
            "title": "Another Bookmarked Paper",
        })
        
        paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": True,
            "2301.00002": False,
            "2301.00003": True,
            "2301.00004": False,
        }

    def test_check_batch_single_paper(self, repo):
        repo.add({
            "paper_id": "2301.12345",
            "title": "Single Paper",
        })
        
        result = repo.check_batch(["2301.12345"])
        assert result == {"2301.12345": True}
        
        result = repo.check_batch(["2301.99999"])
        assert result == {"2301.99999": False}

    def test_check_batch_with_versioned_ids(self, repo):
        repo.add({
            "paper_id": "2301.12345v2",
            "title": "Versioned Paper",
        })
        
        result = repo.check_batch(["2301.12345v2"])
        assert result == {"2301.12345v2": True}
        
        result = repo.check_batch(["2301.12345v1", "2301.12345v3"])
        assert result == {"2301.12345v1": False, "2301.12345v3": False}

    def test_check_batch_large_list(self, repo):
        for i in range(100):
            repo.add({
                "paper_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
            })
        
        paper_ids = [f"2301.{i:05d}" for i in range(0, 200, 2)]
        result = repo.check_batch(paper_ids)
        
        for i, pid in enumerate(paper_ids):
            expected = (i * 2) < 100
            assert result[pid] == expected, f"Failed for {pid}"

    def test_check_batch_after_remove(self, repo):
        repo.add({
            "paper_id": "2301.00001",
            "title": "To Be Removed",
        })
        repo.add({
            "paper_id": "2301.00002",
            "title": "To Stay",
        })
        
        result = repo.check_batch(["2301.00001", "2301.00002"])
        assert result["2301.00001"] is True
        assert result["2301.00002"] is True
        
        repo.remove("2301.00001")
        
        result = repo.check_batch(["2301.00001", "2301.00002"])
        assert result["2301.00001"] is False
        assert result["2301.00002"] is True
