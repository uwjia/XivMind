import pytest
import tempfile
import os

from app.db.sqlite.download_repo import SQLiteDownloadRepository


class TestSQLiteDownloadRepositoryCountCompleted:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_downloads.db")
            repo = SQLiteDownloadRepository(db_path)
            yield repo

    def test_count_completed_with_completed_tasks(self, repo):
        for i in range(3):
            task = repo.add({
                "paper_id": f"2301.0000{i}",
                "title": f"Test Paper {i}",
            })
            repo.update_status(task["id"], status="completed", progress=100)
        
        count = repo.count_completed()
        
        assert count == 3

    def test_count_completed_with_no_completed_tasks(self, repo):
        for i in range(3):
            repo.add({
                "paper_id": f"2301.0000{i}",
                "title": f"Test Paper {i}",
            })
        
        count = repo.count_completed()
        
        assert count == 0

    def test_count_completed_with_mixed_statuses(self, repo):
        task1 = repo.add({
            "paper_id": "2301.00001",
            "title": "Completed Paper 1",
        })
        repo.update_status(task1["id"], status="completed", progress=100)
        
        task2 = repo.add({
            "paper_id": "2301.00002",
            "title": "Pending Paper",
        })
        
        task3 = repo.add({
            "paper_id": "2301.00003",
            "title": "Completed Paper 2",
        })
        repo.update_status(task3["id"], status="completed", progress=100)
        
        task4 = repo.add({
            "paper_id": "2301.00004",
            "title": "Failed Paper",
        })
        repo.update_status(task4["id"], status="failed", error_message="Error")
        
        task5 = repo.add({
            "paper_id": "2301.00005",
            "title": "Completed Paper 3",
        })
        repo.update_status(task5["id"], status="completed", progress=100)
        
        count = repo.count_completed()
        
        assert count == 3

    def test_count_completed_empty_database(self, repo):
        count = repo.count_completed()
        
        assert count == 0

    def test_count_completed_after_deletion(self, repo):
        task1 = repo.add({
            "paper_id": "2301.00001",
            "title": "Completed Paper 1",
        })
        repo.update_status(task1["id"], status="completed", progress=100)
        
        task2 = repo.add({
            "paper_id": "2301.00002",
            "title": "Completed Paper 2",
        })
        repo.update_status(task2["id"], status="completed", progress=100)
        
        assert repo.count_completed() == 2
        
        repo.remove(task1["id"])
        
        count = repo.count_completed()
        
        assert count == 1

    def test_count_completed_after_status_change(self, repo):
        task = repo.add({
            "paper_id": "2301.00001",
            "title": "Test Paper",
        })
        
        assert repo.count_completed() == 0
        
        repo.update_status(task["id"], status="downloading", progress=50)
        
        assert repo.count_completed() == 0
        
        repo.update_status(task["id"], status="completed", progress=100)
        
        assert repo.count_completed() == 1
        
        repo.update_status(task["id"], status="failed", error_message="Error")
        
        count = repo.count_completed()
        
        assert count == 0
