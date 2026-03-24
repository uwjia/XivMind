import pytest
from unittest.mock import Mock, patch
import pandas as pd
import json

from app.db.lancedb.pdf_annotation_repo import LanceDBPdfAnnotationRepository


@pytest.fixture
def repo():
    return LanceDBPdfAnnotationRepository()


@pytest.fixture
def sample_annotation_data():
    return {
        "paper_id": "2301.12345",
        "type": "highlight",
        "page_number": 1,
        "position": {"x": 100, "y": 200, "width": 300, "height": 20},
        "content": "This is highlighted text",
        "color": "rgba(255, 235, 59, 0.4)",
        "stroke_width": 2,
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
        "stroke_width": 3,
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
def sample_reading_progress_data():
    return {
        "paper_id": "2301.12345",
        "current_page": 5,
        "total_pages": 20,
        "zoom_level": 1.5,
        "view_mode": "continuous",
    }


class TestLanceDBPdfAnnotationRepositoryAnnotationOperations:
    def test_create_annotation(self, repo, sample_annotation_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.create_annotation(sample_annotation_data)
            
            assert result is not None
            assert result["paper_id"] == sample_annotation_data["paper_id"]
            assert result["type"] == sample_annotation_data["type"]
            assert result["page_number"] == sample_annotation_data["page_number"]
            assert result["color"] == sample_annotation_data["color"]
            assert "id" in result
            assert "created_at" in result
            assert "updated_at" in result
            mock_table.add.assert_called_once()

    def test_create_drawing_annotation(self, repo, sample_drawing_annotation_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.create_annotation(sample_drawing_annotation_data)
            
            assert result is not None
            assert result["type"] == "drawing"
            assert result["stroke_width"] == 3
            mock_table.add.assert_called_once()

    def test_get_annotation_found(self, repo, sample_annotation_data):
        mock_table = Mock()
        annotation_id = "test-annotation-id"
        
        df = pd.DataFrame([{
            "id": annotation_id,
            "paper_id": sample_annotation_data["paper_id"],
            "type": sample_annotation_data["type"],
            "page_number": sample_annotation_data["page_number"],
            "position": json.dumps(sample_annotation_data["position"]),
            "content": sample_annotation_data["content"],
            "color": sample_annotation_data["color"],
            "stroke_width": sample_annotation_data.get("stroke_width"),
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.get_annotation(annotation_id)
            
            assert result is not None
            assert result["id"] == annotation_id
            assert result["paper_id"] == sample_annotation_data["paper_id"]

    def test_get_annotation_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.get_annotation("nonexistent-id")
            
            assert result is None

    def test_get_annotations_by_paper_id(self, repo, sample_annotation_data):
        mock_table = Mock()
        
        df = pd.DataFrame([
            {
                "id": "annotation-1",
                "paper_id": sample_annotation_data["paper_id"],
                "type": "highlight",
                "page_number": 1,
                "position": json.dumps({"x": 100, "y": 200, "width": 300, "height": 20}),
                "content": "Text 1",
                "color": "rgba(255, 235, 59, 0.4)",
                "stroke_width": None,
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00",
            },
            {
                "id": "annotation-2",
                "paper_id": sample_annotation_data["paper_id"],
                "type": "comment",
                "page_number": 1,
                "position": json.dumps({"x": 0, "y": 300, "width": 24, "height": 24}),
                "content": "Comment text",
                "color": "#FFC107",
                "stroke_width": None,
                "created_at": "2024-01-15T10:05:00",
                "updated_at": "2024-01-15T10:05:00",
            },
        ])
        
        mock_lance_ds = Mock()
        mock_result_table = Mock()
        mock_result_table.to_pandas = Mock(return_value=df)
        mock_result_table.num_rows = 2
        mock_scanner = Mock()
        mock_scanner.to_table = Mock(return_value=mock_result_table)
        mock_lance_ds.scanner = Mock(return_value=mock_scanner)
        mock_table.to_lance = Mock(return_value=mock_lance_ds)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.get_annotations(sample_annotation_data["paper_id"])
            
            assert len(result) == 2
            assert result[0]["paper_id"] == sample_annotation_data["paper_id"]

    def test_get_annotations_empty(self, repo):
        mock_table = Mock()
        mock_table.count_rows = Mock(return_value=0)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.get_annotations("nonexistent-paper")
            
            assert result == []

    def test_update_annotation(self, repo, sample_annotation_data):
        mock_table = Mock()
        annotation_id = "test-annotation-id"
        
        existing_df = pd.DataFrame([{
            "id": annotation_id,
            "paper_id": sample_annotation_data["paper_id"],
            "type": "highlight",
            "page_number": 1,
            "position": json.dumps({"x": 100, "y": 200, "width": 300, "height": 20}),
            "content": "Original content",
            "color": "rgba(255, 235, 59, 0.4)",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=existing_df)
        mock_table.search = Mock(return_value=mock_search)
        
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            update_data = {
                "content": "Updated content",
                "color": "rgba(33, 150, 243, 0.4)",
            }
            result = repo.update_annotation(annotation_id, update_data)
            
            assert result is not None
            assert result["content"] == "Updated content"
            assert result["color"] == "rgba(33, 150, 243, 0.4)"
            mock_table.merge_insert.assert_called_once_with("id")

    def test_update_annotation_with_stroke_width(self, repo, sample_annotation_data):
        mock_table = Mock()
        annotation_id = "test-annotation-id"
        
        existing_df = pd.DataFrame([{
            "id": annotation_id,
            "paper_id": sample_annotation_data["paper_id"],
            "type": "drawing",
            "page_number": 1,
            "position": json.dumps({"x": 100, "y": 200, "width": 300, "height": 100}),
            "content": "[]",
            "color": "#FF0000",
            "stroke_width": 2,
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=existing_df)
        mock_table.search = Mock(return_value=mock_search)
        
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            update_data = {
                "stroke_width": 5,
            }
            result = repo.update_annotation(annotation_id, update_data)
            
            assert result is not None
            assert result["stroke_width"] == 5

    def test_update_annotation_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.update_annotation("nonexistent-id", {"content": "test"})
            
            assert result is None

    def test_delete_annotation(self, repo):
        mock_table = Mock()
        annotation_id = "test-annotation-id"
        
        existing_df = pd.DataFrame([{
            "id": annotation_id,
            "paper_id": "2301.12345",
            "type": "highlight",
            "page_number": 1,
            "position": "{}",
            "content": "Test",
            "color": "yellow",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=existing_df)
        mock_table.search = Mock(return_value=mock_search)
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.delete_annotation(annotation_id)
            
            assert result is True
            mock_table.delete.assert_called_once()

    def test_delete_annotation_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_annotations_table', return_value=mock_table):
            result = repo.delete_annotation("nonexistent-id")
            
            assert result is False


class TestLanceDBPdfAnnotationRepositoryReadingProgress:
    def test_save_reading_progress_new(self, repo, sample_reading_progress_data):
        mock_table = Mock()
        
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_progress_table', return_value=mock_table):
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
            mock_table.merge_insert.assert_called_once_with("paper_id")

    def test_save_reading_progress_update(self, repo, sample_reading_progress_data):
        mock_table = Mock()
        
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_progress_table', return_value=mock_table):
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
        mock_table = Mock()
        
        df = pd.DataFrame([{
            "paper_id": sample_reading_progress_data["paper_id"],
            "current_page": sample_reading_progress_data["current_page"],
            "total_pages": sample_reading_progress_data["total_pages"],
            "zoom_level": sample_reading_progress_data["zoom_level"],
            "view_mode": sample_reading_progress_data["view_mode"],
            "last_read_at": "2024-01-15T10:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_progress_table', return_value=mock_table):
            result = repo.get_reading_progress(sample_reading_progress_data["paper_id"])
            
            assert result is not None
            assert result["paper_id"] == sample_reading_progress_data["paper_id"]
            assert result["current_page"] == sample_reading_progress_data["current_page"]

    def test_get_reading_progress_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_progress_table', return_value=mock_table):
            result = repo.get_reading_progress("nonexistent-paper")
            
            assert result is None


class TestLanceDBPdfAnnotationRepositoryEntityConversion:
    def test_entity_to_annotation(self, repo):
        row = {
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
        
        result = repo._entity_to_annotation(row)
        
        assert result["id"] == "test-id"
        assert result["paper_id"] == "2301.12345"
        assert result["type"] == "highlight"
        assert result["position"] == {"x": 100, "y": 200, "width": 300, "height": 20}
        assert result["content"] == "Test content"

    def test_entity_to_annotation_empty_position(self, repo):
        row = {
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
        
        result = repo._entity_to_annotation(row)
        
        assert result["position"] == {}
