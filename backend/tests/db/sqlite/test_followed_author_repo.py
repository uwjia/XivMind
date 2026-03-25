import os
import tempfile
import pytest

from app.db.sqlite.followed_author_repo import SQLiteFollowedAuthorRepository


class TestSQLiteFollowedAuthorRepository:
    """Tests for SQLite implementation."""
    
    @pytest.fixture
    def repo(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        repo = SQLiteFollowedAuthorRepository(db_path)
        yield repo
        os.unlink(db_path)
    
    def test_add(self, repo):
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
        assert result["followed_at"] is not None
    
    def test_add_duplicate_author(self, repo):
        data = {"author_name": "John Doe"}
        repo.add(data)
        
        with pytest.raises(Exception):
            repo.add(data)
    
    def test_get(self, repo):
        data = {"author_name": "John Doe", "paper_count": 5}
        added = repo.add(data)
        
        result = repo.get(added["id"])
        
        assert result is not None
        assert result["author_name"] == "John Doe"
        assert result["paper_count"] == 5
    
    def test_get_not_found(self, repo):
        result = repo.get("non-existent-id")
        assert result is None
    
    def test_remove(self, repo):
        data = {"author_name": "John Doe"}
        added = repo.add(data)
        
        result = repo.remove(added["id"])
        assert result is True
        
        assert repo.get(added["id"]) is None
    
    def test_remove_not_found(self, repo):
        result = repo.remove("non-existent-id")
        assert result is False
    
    def test_get_all(self, repo):
        repo.add({"author_name": "Author A"})
        repo.add({"author_name": "Author B"})
        repo.add({"author_name": "Author C"})
        
        results, total = repo.get_all(limit=2, offset=0)
        
        assert total == 3
        assert len(results) == 2
    
    def test_get_all_empty(self, repo):
        results, total = repo.get_all()
        
        assert results == []
        assert total == 0
    
    def test_exists(self, repo):
        data = {"author_name": "John Doe"}
        added = repo.add(data)
        
        assert repo.exists(added["id"]) is True
        assert repo.exists("non-existent-id") is False
    
    def test_get_by_author_name(self, repo):
        data = {"author_name": "John Doe", "paper_count": 15}
        repo.add(data)
        
        result = repo.get_by_author_name("John Doe")
        
        assert result is not None
        assert result["author_name"] == "John Doe"
        assert result["paper_count"] == 15
    
    def test_get_by_author_name_not_found(self, repo):
        result = repo.get_by_author_name("Non Existent")
        assert result is None
    
    def test_is_followed(self, repo):
        repo.add({"author_name": "John Doe"})
        
        assert repo.is_followed("John Doe") is True
        assert repo.is_followed("Jane Doe") is False
    
    def test_update_notes(self, repo):
        repo.add({"author_name": "John Doe", "notes": "Old notes"})
        
        result = repo.update_notes("John Doe", "New notes")
        assert result is True
        
        author = repo.get_by_author_name("John Doe")
        assert author["notes"] == "New notes"
    
    def test_update_notes_not_found(self, repo):
        result = repo.update_notes("Non Existent", "New notes")
        assert result is False
    
    def test_update_paper_info(self, repo):
        repo.add({"author_name": "John Doe", "paper_count": 5, "latest_published": "2023-01-01"})
        
        result = repo.update_paper_info("John Doe", 10, "2024-06-15")
        assert result is True
        
        author = repo.get_by_author_name("John Doe")
        assert author["paper_count"] == 10
        assert author["latest_published"] == "2024-06-15"
    
    def test_update_paper_info_not_found(self, repo):
        result = repo.update_paper_info("Non Existent", 10, "2024-06-15")
        assert result is False
