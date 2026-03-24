import pytest
import tempfile
import os
import json

from app.db.sqlite.pdf_annotation_repo import SQLitePdfAnnotationRepository


class TestSQLitePdfAnnotationRepositoryAnnotationOperations:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_annotations.db")
            repo = SQLitePdfAnnotationRepository(db_path)
            yield repo

    @pytest.fixture
    def sample_annotation_data(self):
        return {
            "paper_id": "2301.12345",
            "type": "highlight",
            "page_number": 1,
            "position": {"x": 100, "y": 200, "width": 300, "height": 20},
            "content": "This is highlighted text",
            "color": "rgba(255, 235, 59, 0.4)",
        }

    @pytest.fixture
    def sample_drawing_annotation_data(self):
        return {
            "paper_id": "2301.12345",
            "type": "drawing",
            "page_number": 1,
            "position": {"x": 100, "y": 200, "width": 300, "height": 100},
            "content": json.dumps([
                {"x": 100, "y": 200},
                {"x": 150, "y": 220},
                {"x": 200, "y": 210}
            ]),
            "color": "#FF0000",
        }

    @pytest.fixture
    def sample_comment_annotation_data(self):
        return {
            "paper_id": "2301.12345",
            "type": "comment",
            "page_number": 1,
            "position": {"x": 0, "y": 300, "width": 24, "height": 24},
            "content": "This is an important comment",
            "color": "#FFC107",
        }

    def test_create_annotation(self, repo, sample_annotation_data):
        result = repo.create_annotation(sample_annotation_data)
        
        assert result is not None
        assert result["paper_id"] == sample_annotation_data["paper_id"]
        assert result["type"] == sample_annotation_data["type"]
        assert result["page_number"] == sample_annotation_data["page_number"]
        assert result["color"] == sample_annotation_data["color"]
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_create_drawing_annotation(self, repo, sample_drawing_annotation_data):
        result = repo.create_annotation(sample_drawing_annotation_data)
        
        assert result is not None
        assert result["type"] == "drawing"
        assert result["content"] == sample_drawing_annotation_data["content"]

    def test_create_comment_annotation(self, repo, sample_comment_annotation_data):
        result = repo.create_annotation(sample_comment_annotation_data)
        
        assert result is not None
        assert result["type"] == "comment"
        assert result["content"] == sample_comment_annotation_data["content"]

    def test_get_annotation_found(self, repo, sample_annotation_data):
        created = repo.create_annotation(sample_annotation_data)
        
        result = repo.get_annotation(created["id"])
        
        assert result is not None
        assert result["id"] == created["id"]
        assert result["paper_id"] == sample_annotation_data["paper_id"]

    def test_get_annotation_not_found(self, repo):
        result = repo.get_annotation("nonexistent-id")
        
        assert result is None

    def test_get_annotations_by_paper_id(self, repo, sample_annotation_data):
        repo.create_annotation(sample_annotation_data)
        repo.create_annotation({
            **sample_annotation_data,
            "type": "comment",
            "content": "Another annotation",
        })
        
        result = repo.get_annotations(sample_annotation_data["paper_id"])
        
        assert len(result) == 2
        assert all(a["paper_id"] == sample_annotation_data["paper_id"] for a in result)

    def test_get_annotations_empty(self, repo):
        result = repo.get_annotations("nonexistent-paper")
        
        assert result == []

    def test_get_annotations_sorted_by_page_and_time(self, repo):
        repo.create_annotation({
            "paper_id": "test-paper",
            "type": "highlight",
            "page_number": 2,
            "position": {},
            "color": "yellow",
        })
        repo.create_annotation({
            "paper_id": "test-paper",
            "type": "highlight",
            "page_number": 1,
            "position": {},
            "color": "blue",
        })
        repo.create_annotation({
            "paper_id": "test-paper",
            "type": "highlight",
            "page_number": 1,
            "position": {},
            "color": "green",
        })
        
        result = repo.get_annotations("test-paper")
        
        assert len(result) == 3
        assert result[0]["page_number"] == 1
        assert result[1]["page_number"] == 1
        assert result[2]["page_number"] == 2

    def test_update_annotation(self, repo, sample_annotation_data):
        created = repo.create_annotation(sample_annotation_data)
        
        update_data = {
            "content": "Updated content",
            "color": "rgba(33, 150, 243, 0.4)",
        }
        result = repo.update_annotation(created["id"], update_data)
        
        assert result is not None
        assert result["content"] == "Updated content"
        assert result["color"] == "rgba(33, 150, 243, 0.4)"

    def test_update_annotation_position(self, repo, sample_annotation_data):
        created = repo.create_annotation(sample_annotation_data)
        
        new_position = {"x": 200, "y": 300, "width": 400, "height": 30}
        update_data = {"position": new_position}
        result = repo.update_annotation(created["id"], update_data)
        
        assert result is not None
        assert result["position"] == new_position

    def test_update_annotation_not_found(self, repo):
        result = repo.update_annotation("nonexistent-id", {"content": "test"})
        
        assert result is None

    def test_delete_annotation(self, repo, sample_annotation_data):
        created = repo.create_annotation(sample_annotation_data)
        
        result = repo.delete_annotation(created["id"])
        
        assert result is True
        assert repo.get_annotation(created["id"]) is None

    def test_delete_annotation_not_found(self, repo):
        result = repo.delete_annotation("nonexistent-id")
        
        assert result is False

    def test_row_to_annotation(self, repo, sample_annotation_data):
        created = repo.create_annotation(sample_annotation_data)
        result = repo.get_annotation(created["id"])
        
        assert result["position"] == sample_annotation_data["position"]
        assert isinstance(result["position"], dict)


class TestSQLitePdfAnnotationRepositoryReadingProgress:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_progress.db")
            repo = SQLitePdfAnnotationRepository(db_path)
            yield repo

    @pytest.fixture
    def sample_reading_progress_data(self):
        return {
            "paper_id": "2301.12345",
            "current_page": 5,
            "total_pages": 20,
            "zoom_level": 1.5,
            "view_mode": "continuous",
        }

    def test_save_reading_progress_new(self, repo, sample_reading_progress_data):
        result = repo.save_reading_progress(
            paper_id=sample_reading_progress_data["paper_id"],
            current_page=sample_reading_progress_data["current_page"],
            total_pages=sample_reading_progress_data["total_pages"],
            zoom_level=sample_reading_progress_data["zoom_level"],
            view_mode=sample_reading_progress_data["view_mode"],
        )
        
        assert result is not None
        assert result["paper_id"] == sample_reading_progress_data["paper_id"]
        assert result["current_page"] == sample_reading_progress_data["current_page"]
        assert result["total_pages"] == sample_reading_progress_data["total_pages"]
        assert result["zoom_level"] == sample_reading_progress_data["zoom_level"]
        assert result["view_mode"] == sample_reading_progress_data["view_mode"]
        assert "last_read_at" in result

    def test_save_reading_progress_update(self, repo, sample_reading_progress_data):
        repo.save_reading_progress(
            paper_id=sample_reading_progress_data["paper_id"],
            current_page=sample_reading_progress_data["current_page"],
            total_pages=sample_reading_progress_data["total_pages"],
            zoom_level=sample_reading_progress_data["zoom_level"],
            view_mode=sample_reading_progress_data["view_mode"],
        )
        
        result = repo.save_reading_progress(
            paper_id=sample_reading_progress_data["paper_id"],
            current_page=10,
            total_pages=20,
            zoom_level=2.0,
            view_mode="single",
        )
        
        assert result is not None
        assert result["current_page"] == 10
        assert result["zoom_level"] == 2.0
        assert result["view_mode"] == "single"

    def test_get_reading_progress_found(self, repo, sample_reading_progress_data):
        repo.save_reading_progress(
            paper_id=sample_reading_progress_data["paper_id"],
            current_page=sample_reading_progress_data["current_page"],
            total_pages=sample_reading_progress_data["total_pages"],
            zoom_level=sample_reading_progress_data["zoom_level"],
            view_mode=sample_reading_progress_data["view_mode"],
        )
        
        result = repo.get_reading_progress(sample_reading_progress_data["paper_id"])
        
        assert result is not None
        assert result["paper_id"] == sample_reading_progress_data["paper_id"]
        assert result["current_page"] == sample_reading_progress_data["current_page"]

    def test_get_reading_progress_not_found(self, repo):
        result = repo.get_reading_progress("nonexistent-paper")
        
        assert result is None

    def test_reading_progress_persists(self, repo):
        repo.save_reading_progress(
            paper_id="test-paper",
            current_page=5,
            total_pages=10,
            zoom_level=1.5,
            view_mode="continuous",
        )
        
        progress = repo.get_reading_progress("test-paper")
        
        assert progress["current_page"] == 5
        assert progress["total_pages"] == 10
        assert progress["zoom_level"] == 1.5
        assert progress["view_mode"] == "continuous"
