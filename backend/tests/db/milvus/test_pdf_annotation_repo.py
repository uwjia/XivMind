import pytest
from unittest.mock import Mock, patch
import json

from app.db.milvus.pdf_annotation_repo import MilvusPdfAnnotationRepository


@pytest.fixture
def repo():
    return MilvusPdfAnnotationRepository()


@pytest.fixture
def sample_annotation_data():
    return {
        "paper_id": "2301.12345",
        "type": "highlight",
        "page_number": 1,
        "position": {"x": 100, "y": 200, "width": 300, "height": 20},
        "content": "This is highlighted text",
        "color": "rgba(255, 235, 59, 0.4)",
    }


@pytest.fixture
def sample_drawing_annotation_data():
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
def sample_comment_annotation_data():
    return {
        "paper_id": "2301.12345",
        "type": "comment",
        "page_number": 1,
        "position": {"x": 0, "y": 300, "width": 24, "height": 24},
        "content": "This is an important comment",
        "color": "#FFC107",
    }


@pytest.fixture
def sample_annotation_entity():
    return {
        "id": "test-annotation-id",
        "paper_id": "2301.12345",
        "type": "highlight",
        "page_number": 1,
        "position": json.dumps({"x": 100, "y": 200, "width": 300, "height": 20}),
        "content": "This is highlighted text",
        "color": "rgba(255, 235, 59, 0.4)",
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00",
    }


@pytest.fixture
def sample_reading_progress_data():
    return {
        "paper_id": "2301.12345",
        "current_page": 5,
        "total_pages": 20,
        "zoom_level": 1.5,
        "view_mode": "continuous",
    }


@pytest.fixture
def sample_reading_progress_entity():
    return {
        "paper_id": "2301.12345",
        "current_page": 5,
        "total_pages": 20,
        "zoom_level": 1.5,
        "view_mode": "continuous",
        "last_read_at": "2024-01-15T10:00:00",
    }


class TestMilvusPdfAnnotationRepositoryAnnotationOperations:
    def test_create_annotation(self, repo, sample_annotation_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.create_annotation(sample_annotation_data)
            
            assert result is not None
            assert result["paper_id"] == sample_annotation_data["paper_id"]
            assert result["type"] == sample_annotation_data["type"]
            assert result["page_number"] == sample_annotation_data["page_number"]
            assert result["color"] == sample_annotation_data["color"]
            assert "id" in result
            assert "created_at" in result
            assert "updated_at" in result
            mock_collection.insert.assert_called_once()
            mock_collection.flush.assert_called_once()

    def test_create_drawing_annotation(self, repo, sample_drawing_annotation_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.create_annotation(sample_drawing_annotation_data)
            
            assert result is not None
            assert result["type"] == "drawing"
            assert result["content"] == sample_drawing_annotation_data["content"]

    def test_create_comment_annotation(self, repo, sample_comment_annotation_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.create_annotation(sample_comment_annotation_data)
            
            assert result is not None
            assert result["type"] == "comment"
            assert result["content"] == sample_comment_annotation_data["content"]

    def test_get_annotation_found(self, repo, sample_annotation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_annotation_entity])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.get_annotation("test-annotation-id")
            
            assert result is not None
            assert result["id"] == "test-annotation-id"
            assert result["paper_id"] == sample_annotation_entity["paper_id"]

    def test_get_annotation_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.get_annotation("nonexistent-id")
            
            assert result is None

    def test_get_annotations_by_paper_id(self, repo, sample_annotation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            sample_annotation_entity,
            {**sample_annotation_entity, "id": "annotation-2", "type": "comment"},
        ])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.get_annotations(sample_annotation_entity["paper_id"])
            
            assert len(result) == 2
            assert all(a["paper_id"] == sample_annotation_entity["paper_id"] for a in result)

    def test_get_annotations_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.get_annotations("nonexistent-paper")
            
            assert result == []

    def test_get_annotations_sorted_by_page_and_time(self, repo):
        entities = [
            {
                "id": "annotation-1",
                "paper_id": "test-paper",
                "type": "highlight",
                "page_number": 2,
                "position": "{}",
                "content": "",
                "color": "yellow",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00",
            },
            {
                "id": "annotation-2",
                "paper_id": "test-paper",
                "type": "highlight",
                "page_number": 1,
                "position": "{}",
                "content": "",
                "color": "blue",
                "created_at": "2024-01-15T09:00:00",
                "updated_at": "2024-01-15T09:00:00",
            },
            {
                "id": "annotation-3",
                "paper_id": "test-paper",
                "type": "highlight",
                "page_number": 1,
                "position": "{}",
                "content": "",
                "color": "green",
                "created_at": "2024-01-15T11:00:00",
                "updated_at": "2024-01-15T11:00:00",
            },
        ]
        
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=entities)
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.get_annotations("test-paper")
            
            assert len(result) == 3
            assert result[0]["page_number"] == 1
            assert result[1]["page_number"] == 1
            assert result[2]["page_number"] == 2

    def test_update_annotation(self, repo, sample_annotation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_annotation_entity])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            update_data = {
                "content": "Updated content",
                "color": "rgba(33, 150, 243, 0.4)",
            }
            result = repo.update_annotation("test-annotation-id", update_data)
            
            assert result is not None
            assert result["content"] == "Updated content"
            assert result["color"] == "rgba(33, 150, 243, 0.4)"
            mock_collection.delete.assert_called_once()
            mock_collection.insert.assert_called_once()

    def test_update_annotation_position(self, repo, sample_annotation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_annotation_entity])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            new_position = {"x": 200, "y": 300, "width": 400, "height": 30}
            update_data = {"position": new_position}
            result = repo.update_annotation("test-annotation-id", update_data)
            
            assert result is not None
            assert result["position"] == new_position

    def test_update_annotation_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.update_annotation("nonexistent-id", {"content": "test"})
            
            assert result is None

    def test_delete_annotation(self, repo, sample_annotation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_annotation_entity])
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.delete_annotation("test-annotation-id")
            
            assert result is True
            mock_collection.delete.assert_called_once()

    def test_delete_annotation_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_annotations_collection', return_value=mock_collection):
            result = repo.delete_annotation("nonexistent-id")
            
            assert result is False


class TestMilvusPdfAnnotationRepositoryReadingProgress:
    def test_save_reading_progress_new(self, repo, sample_reading_progress_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_progress_collection', return_value=mock_collection):
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
            mock_collection.delete.assert_called_once()
            mock_collection.insert.assert_called_once()

    def test_save_reading_progress_update(self, repo, sample_reading_progress_data):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_progress_collection', return_value=mock_collection):
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

    def test_get_reading_progress_found(self, repo, sample_reading_progress_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_reading_progress_entity])
        
        with patch.object(repo, '_get_progress_collection', return_value=mock_collection):
            result = repo.get_reading_progress(sample_reading_progress_entity["paper_id"])
            
            assert result is not None
            assert result["paper_id"] == sample_reading_progress_entity["paper_id"]
            assert result["current_page"] == sample_reading_progress_entity["current_page"]

    def test_get_reading_progress_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_progress_collection', return_value=mock_collection):
            result = repo.get_reading_progress("nonexistent-paper")
            
            assert result is None


class TestMilvusPdfAnnotationRepositoryEntityConversion:
    def test_entity_to_annotation(self, repo):
        entity = {
            "id": "test-id",
            "paper_id": "2301.12345",
            "type": "highlight",
            "page_number": 1,
            "position": json.dumps({"x": 100, "y": 200, "width": 300, "height": 20}),
            "content": "Test content",
            "color": "rgba(255, 235, 59, 0.4)",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        
        result = repo._entity_to_annotation(entity)
        
        assert result["id"] == "test-id"
        assert result["paper_id"] == "2301.12345"
        assert result["type"] == "highlight"
        assert result["position"] == {"x": 100, "y": 200, "width": 300, "height": 20}
        assert result["content"] == "Test content"

    def test_entity_to_annotation_empty_position(self, repo):
        entity = {
            "id": "test-id",
            "paper_id": "2301.12345",
            "type": "comment",
            "page_number": 1,
            "position": None,
            "content": "Test content",
            "color": "#FFC107",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        
        result = repo._entity_to_annotation(entity)
        
        assert result["position"] == {}
