import pytest
import tempfile
import os

from app.db.sqlite.paper_repo import SQLitePaperRepository


class TestSQLitePaperRepositoryUpsertPapersBatch:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_papers.db")
            repo = SQLitePaperRepository(db_path)
            yield repo

    def test_upsert_papers_batch_insert_new(self, repo):
        papers = [
            {
                "id": "2301.00001",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": ["Author 1"],
                "primary_category": "cs.AI",
                "categories": ["cs.AI"],
                "published": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "Paper 2",
                "abstract": "Abstract 2",
                "authors": ["Author 2"],
                "primary_category": "cs.LG",
                "categories": ["cs.LG"],
                "published": "2024-01-01T00:00:00",
            },
        ]
        
        count = repo.upsert_papers_batch(papers)
        
        assert count == 2
        assert repo.exists("2301.00001")
        assert repo.exists("2301.00002")

    def test_upsert_papers_batch_update_existing(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Original Title",
            "abstract": "Original Abstract",
            "authors": ["Original Author"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        
        papers = [
            {
                "id": "2301.00001",
                "title": "Updated Title",
                "abstract": "Updated Abstract",
                "authors": ["Updated Author"],
                "primary_category": "cs.LG",
                "categories": ["cs.LG"],
                "published": "2024-01-02T00:00:00",
            },
        ]
        
        count = repo.upsert_papers_batch(papers)
        
        assert count == 1
        paper = repo.get("2301.00001")
        assert paper["title"] == "Updated Title"
        assert paper["abstract"] == "Updated Abstract"
        assert paper["primary_category"] == "cs.LG"

    def test_upsert_papers_batch_mixed_insert_and_update(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Existing Paper",
            "abstract": "Original Abstract",
            "authors": ["Author"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        
        papers = [
            {
                "id": "2301.00001",
                "title": "Updated Paper",
                "abstract": "Updated Abstract",
                "authors": ["Updated Author"],
                "primary_category": "cs.LG",
                "categories": ["cs.LG"],
                "published": "2024-01-02T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "New Paper",
                "abstract": "New Abstract",
                "authors": ["New Author"],
                "primary_category": "cs.CV",
                "categories": ["cs.CV"],
                "published": "2024-01-03T00:00:00",
            },
        ]
        
        count = repo.upsert_papers_batch(papers)
        
        assert count == 2
        paper1 = repo.get("2301.00001")
        assert paper1["title"] == "Updated Paper"
        paper2 = repo.get("2301.00002")
        assert paper2["title"] == "New Paper"

    def test_upsert_papers_batch_empty_list(self, repo):
        count = repo.upsert_papers_batch([])
        
        assert count == 0

    def test_upsert_papers_batch_multiple_updates(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Paper 1 Original",
            "abstract": "Abstract 1",
            "authors": [],
            "primary_category": "cs.AI",
            "categories": [],
            "published": "2024-01-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00002",
            "title": "Paper 2 Original",
            "abstract": "Abstract 2",
            "authors": [],
            "primary_category": "cs.LG",
            "categories": [],
            "published": "2024-01-01T00:00:00",
        })
        
        papers = [
            {
                "id": "2301.00001",
                "title": "Paper 1 Updated",
                "abstract": "Updated Abstract 1",
                "authors": [],
                "primary_category": "cs.AI",
                "categories": [],
                "published": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "Paper 2 Updated",
                "abstract": "Updated Abstract 2",
                "authors": [],
                "primary_category": "cs.LG",
                "categories": [],
                "published": "2024-01-01T00:00:00",
            },
        ]
        
        count = repo.upsert_papers_batch(papers)
        
        assert count == 2
        assert repo.get("2301.00001")["title"] == "Paper 1 Updated"
        assert repo.get("2301.00002")["title"] == "Paper 2 Updated"


class TestSQLitePaperRepositoryInsertPapersBatch:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_papers.db")
            repo = SQLitePaperRepository(db_path)
            yield repo

    def test_insert_papers_batch_insert_new(self, repo):
        papers = [
            {
                "id": "2301.00001",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "authors": ["Author 1"],
                "primary_category": "cs.AI",
                "categories": ["cs.AI"],
                "published": "2024-01-01T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "Paper 2",
                "abstract": "Abstract 2",
                "authors": ["Author 2"],
                "primary_category": "cs.LG",
                "categories": ["cs.LG"],
                "published": "2024-01-01T00:00:00",
            },
        ]
        
        count = repo.insert_papers_batch(papers)
        
        assert count == 2

    def test_insert_papers_batch_skip_existing(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Existing Paper",
            "abstract": "Original Abstract",
            "authors": ["Author"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        
        papers = [
            {
                "id": "2301.00001",
                "title": "Should Not Update",
                "abstract": "Should Not Update",
                "authors": [],
                "primary_category": "cs.LG",
                "categories": [],
                "published": "2024-01-02T00:00:00",
            },
            {
                "id": "2301.00002",
                "title": "New Paper",
                "abstract": "New Abstract",
                "authors": [],
                "primary_category": "cs.CV",
                "categories": [],
                "published": "2024-01-03T00:00:00",
            },
        ]
        
        count = repo.insert_papers_batch(papers)
        
        assert count == 1
        paper = repo.get("2301.00001")
        assert paper["title"] == "Existing Paper"

    def test_insert_papers_batch_empty_list(self, repo):
        count = repo.insert_papers_batch([])
        
        assert count == 0


class TestSQLitePaperRepositoryGetPapersByAuthor:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_papers.db")
            repo = SQLitePaperRepository(db_path)
            yield repo

    def test_get_papers_by_author_single_author(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Paper 1",
            "abstract": "Abstract 1",
            "authors": ["John Smith"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00002",
            "title": "Paper 2",
            "abstract": "Abstract 2",
            "authors": ["Jane Doe"],
            "primary_category": "cs.LG",
            "categories": ["cs.LG"],
            "published": "2024-01-02T00:00:00",
        })
        
        papers, total = repo.get_papers_by_author("John Smith")
        
        assert total == 1
        assert len(papers) == 1
        assert papers[0]["id"] == "2301.00001"
        assert "John Smith" in papers[0]["authors"]

    def test_get_papers_by_author_multiple_papers(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Paper 1",
            "abstract": "Abstract 1",
            "authors": ["John Smith", "Jane Doe"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00002",
            "title": "Paper 2",
            "abstract": "Abstract 2",
            "authors": ["John Smith"],
            "primary_category": "cs.LG",
            "categories": ["cs.LG"],
            "published": "2024-01-02T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00003",
            "title": "Paper 3",
            "abstract": "Abstract 3",
            "authors": ["Jane Doe"],
            "primary_category": "cs.CV",
            "categories": ["cs.CV"],
            "published": "2024-01-03T00:00:00",
        })
        
        papers, total = repo.get_papers_by_author("John Smith")
        
        assert total == 2
        assert len(papers) == 2
        paper_ids = [p["id"] for p in papers]
        assert "2301.00001" in paper_ids
        assert "2301.00002" in paper_ids

    def test_get_papers_by_author_sorted_by_date(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Older Paper",
            "abstract": "Abstract 1",
            "authors": ["John Smith"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00002",
            "title": "Newer Paper",
            "abstract": "Abstract 2",
            "authors": ["John Smith"],
            "primary_category": "cs.LG",
            "categories": ["cs.LG"],
            "published": "2024-06-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00003",
            "title": "Middle Paper",
            "abstract": "Abstract 3",
            "authors": ["John Smith"],
            "primary_category": "cs.CV",
            "categories": ["cs.CV"],
            "published": "2024-03-01T00:00:00",
        })
        
        papers, total = repo.get_papers_by_author("John Smith")
        
        assert total == 3
        assert papers[0]["id"] == "2301.00002"
        assert papers[1]["id"] == "2301.00003"
        assert papers[2]["id"] == "2301.00001"

    def test_get_papers_by_author_not_found(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Paper 1",
            "abstract": "Abstract 1",
            "authors": ["John Smith"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        
        papers, total = repo.get_papers_by_author("Unknown Author")
        
        assert total == 0
        assert len(papers) == 0

    def test_get_papers_by_author_pagination(self, repo):
        for i in range(10):
            repo.insert_paper({
                "id": f"2301.0000{i}",
                "title": f"Paper {i}",
                "abstract": f"Abstract {i}",
                "authors": ["John Smith"],
                "primary_category": "cs.AI",
                "categories": ["cs.AI"],
                "published": f"2024-01-{i+1:02d}T00:00:00",
            })
        
        papers, total = repo.get_papers_by_author("John Smith", start=0, max_results=5)
        
        assert total == 10
        assert len(papers) == 5
        
        papers2, total2 = repo.get_papers_by_author("John Smith", start=5, max_results=5)
        
        assert total2 == 10
        assert len(papers2) == 5
        
        all_ids = [p["id"] for p in papers] + [p["id"] for p in papers2]
        assert len(set(all_ids)) == 10

    def test_get_papers_by_author_coauthor(self, repo):
        repo.insert_paper({
            "id": "2301.00001",
            "title": "Paper 1",
            "abstract": "Abstract 1",
            "authors": ["John Smith", "Jane Doe", "Bob Wilson"],
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "published": "2024-01-01T00:00:00",
        })
        repo.insert_paper({
            "id": "2301.00002",
            "title": "Paper 2",
            "abstract": "Abstract 2",
            "authors": ["Jane Doe", "Alice Brown"],
            "primary_category": "cs.LG",
            "categories": ["cs.LG"],
            "published": "2024-01-02T00:00:00",
        })
        
        papers, total = repo.get_papers_by_author("Jane Doe")
        
        assert total == 2
        assert len(papers) == 2

    def test_get_papers_by_author_empty_database(self, repo):
        papers, total = repo.get_papers_by_author("John Smith")
        
        assert total == 0
        assert len(papers) == 0
