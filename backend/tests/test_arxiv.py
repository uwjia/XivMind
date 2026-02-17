import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.arxiv import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_paper_service():
    with patch('app.routers.arxiv._paper_service') as mock:
        yield mock


@pytest.fixture
def sample_paper_data():
    return {
        "id": "2301.12345v1",
        "title": "Test Paper Title",
        "abstract": "This is a test abstract for the paper.",
        "authors": ["Author One", "Author Two", "Author Three"],
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG", "cs.CL"],
        "published": "2024-01-15T10:00:00",
        "updated": "2024-01-16T12:00:00",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "comment": "Test comment",
    }


@pytest.fixture
def sample_paper_response():
    return {
        "id": "2301.12345v1",
        "title": "Test Paper Title",
        "abstract": "This is a test abstract for the paper.",
        "authors": ["Author One", "Author Two", "Author Three"],
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG", "cs.CL"],
        "published": "2024-01-15T10:00:00",
        "updated": "2024-01-16T12:00:00",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "comment": "Test comment",
        "fetched_at": "2024-01-17T00:00:00",
    }


@pytest.fixture
def sample_date_index():
    return {
        "date": "2024-01-15",
        "total_count": 125,
        "fetched_at": "2024-01-17T00:00:00",
    }


@pytest.fixture
def sample_statistics():
    return {
        "total_papers": 1500,
        "total_dates": 30,
        "earliest_date": "2024-01-01",
        "latest_date": "2024-01-30",
    }


class TestQueryPapers:
    def test_query_papers_success(self, client, mock_paper_service, sample_paper_response):
        mock_paper_service.query_papers = AsyncMock(return_value={
            "papers": [sample_paper_response],
            "total": 1,
            "start": 0,
            "max_results": 50,
        })
        
        response = client.get("/arxiv/query?date=2024-01-15")
        
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["papers"]) == 1
        assert response.json()["papers"][0]["id"] == "2301.12345v1"

    def test_query_papers_with_category(self, client, mock_paper_service, sample_paper_response):
        mock_paper_service.query_papers = AsyncMock(return_value={
            "papers": [sample_paper_response],
            "total": 1,
            "start": 0,
            "max_results": 50,
        })
        
        response = client.get("/arxiv/query?date=2024-01-15&category=cs.AI")
        
        assert response.status_code == 200
        mock_paper_service.query_papers.assert_called_once()
        call_kwargs = mock_paper_service.query_papers.call_args[1]
        assert call_kwargs["category"] == "cs.AI"

    def test_query_papers_with_pagination(self, client, mock_paper_service, sample_paper_response):
        mock_paper_service.query_papers = AsyncMock(return_value={
            "papers": [sample_paper_response],
            "total": 100,
            "start": 10,
            "max_results": 10,
        })
        
        response = client.get("/arxiv/query?date=2024-01-15&start=10&max_results=10")
        
        assert response.status_code == 200
        assert response.json()["start"] == 10
        assert response.json()["max_results"] == 10
        call_kwargs = mock_paper_service.query_papers.call_args[1]
        assert call_kwargs["start"] == 10
        assert call_kwargs["max_results"] == 10

    def test_query_papers_invalid_start(self, client, mock_paper_service):
        response = client.get("/arxiv/query?date=2024-01-15&start=-1")
        assert response.status_code == 422

    def test_query_papers_invalid_max_results(self, client, mock_paper_service):
        response = client.get("/arxiv/query?date=2024-01-15&max_results=0")
        assert response.status_code == 422

    def test_query_papers_max_results_exceeds_limit(self, client, mock_paper_service):
        response = client.get("/arxiv/query?date=2024-01-15&max_results=501")
        assert response.status_code == 422

    def test_query_papers_fetch_category(self, client, mock_paper_service, sample_paper_response):
        mock_paper_service.query_papers = AsyncMock(return_value={
            "papers": [sample_paper_response],
            "total": 1,
            "start": 0,
            "max_results": 50,
        })
        
        response = client.get("/arxiv/query?date=2024-01-15&fetch_category=cs.LG")
        
        assert response.status_code == 200
        call_kwargs = mock_paper_service.query_papers.call_args[1]
        assert call_kwargs["fetch_category"] == "cs.LG"

    def test_query_papers_service_error(self, client, mock_paper_service):
        mock_paper_service.query_papers = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.get("/arxiv/query?date=2024-01-15")
        
        assert response.status_code == 200
        assert response.json()["papers"] == []
        assert response.json()["total"] == 0


class TestGetPaper:
    def test_get_paper_success(self, client, mock_paper_service, sample_paper_response):
        mock_paper_service.get_paper_by_id.return_value = sample_paper_response
        
        response = client.get("/arxiv/paper/2301.12345v1")
        
        assert response.status_code == 200
        assert response.json()["id"] == "2301.12345v1"
        assert response.json()["title"] == "Test Paper Title"
        mock_paper_service.get_paper_by_id.assert_called_once_with("2301.12345v1")

    def test_get_paper_not_found(self, client, mock_paper_service):
        mock_paper_service.get_paper_by_id.return_value = None
        
        response = client.get("/arxiv/paper/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_paper_service_error(self, client, mock_paper_service):
        mock_paper_service.get_paper_by_id.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            client.get("/arxiv/paper/2301.12345v1")


class TestFetchPapers:
    def test_fetch_papers_success(self, client, mock_paper_service):
        mock_paper_service.fetch_papers_for_date = AsyncMock(return_value={
            "success": True,
            "date": "2024-01-15",
            "count": 125,
        })
        
        response = client.post("/arxiv/fetch/2024-01-15")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["count"] == 125

    def test_fetch_papers_with_category(self, client, mock_paper_service):
        mock_paper_service.fetch_papers_for_date = AsyncMock(return_value={
            "success": True,
            "date": "2024-01-15",
            "count": 50,
        })
        
        response = client.post("/arxiv/fetch/2024-01-15?category=cs.LG")
        
        assert response.status_code == 200
        mock_paper_service.fetch_papers_for_date.assert_called_once_with("2024-01-15", "cs.LG")

    def test_fetch_papers_invalid_date(self, client, mock_paper_service):
        mock_paper_service.fetch_papers_for_date = AsyncMock(return_value={
            "success": False,
            "date": "invalid-date",
            "count": 0,
            "error": "Invalid date format",
        })
        
        response = client.post("/arxiv/fetch/invalid-date")
        
        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_fetch_papers_future_date(self, client, mock_paper_service):
        mock_paper_service.fetch_papers_for_date = AsyncMock(return_value={
            "success": False,
            "date": "2030-01-01",
            "count": 0,
            "error": "Cannot fetch papers for future dates",
        })
        
        response = client.post("/arxiv/fetch/2030-01-01")
        
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert "future" in response.json()["error"].lower()

    def test_fetch_papers_service_error(self, client, mock_paper_service):
        mock_paper_service.fetch_papers_for_date = AsyncMock(side_effect=Exception("Network error"))
        
        with pytest.raises(Exception):
            client.post("/arxiv/fetch/2024-01-15")


class TestClearCache:
    def test_clear_date_cache_success(self, client, mock_paper_service):
        mock_paper_service.clear_date_index.return_value = None
        
        response = client.delete("/arxiv/cache/date/2024-01-15")
        
        assert response.status_code == 200
        assert "cleared" in response.json()["message"].lower()
        mock_paper_service.clear_date_index.assert_called_once_with("2024-01-15")

    def test_clear_all_cache_success(self, client, mock_paper_service):
        mock_paper_service.clear_all_date_index.return_value = None
        
        response = client.delete("/arxiv/cache/date")
        
        assert response.status_code == 200
        assert "cleared" in response.json()["message"].lower()
        mock_paper_service.clear_all_date_index.assert_called_once()

    def test_clear_cache_service_error(self, client, mock_paper_service):
        mock_paper_service.clear_date_index.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            client.delete("/arxiv/cache/date/2024-01-15")


class TestGetDateIndexes:
    def test_get_date_indexes_success(self, client, mock_paper_service, sample_date_index):
        mock_paper_service.get_all_date_indexes.return_value = [sample_date_index]
        
        response = client.get("/arxiv/date-indexes")
        
        assert response.status_code == 200
        assert "indexes" in response.json()
        assert len(response.json()["indexes"]) == 1
        assert response.json()["indexes"][0]["date"] == "2024-01-15"

    def test_get_date_indexes_empty(self, client, mock_paper_service):
        mock_paper_service.get_all_date_indexes.return_value = []
        
        response = client.get("/arxiv/date-indexes")
        
        assert response.status_code == 200
        assert response.json()["indexes"] == []

    def test_get_date_indexes_service_error(self, client, mock_paper_service):
        mock_paper_service.get_all_date_indexes.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            client.get("/arxiv/date-indexes")


class TestGetStatistics:
    def test_get_statistics_success(self, client, mock_paper_service, sample_statistics):
        mock_paper_service.get_statistics.return_value = sample_statistics
        
        response = client.get("/arxiv/statistics")
        
        assert response.status_code == 200
        assert response.json()["total_papers"] == 1500
        assert response.json()["total_dates"] == 30

    def test_get_statistics_service_error(self, client, mock_paper_service):
        mock_paper_service.get_statistics.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            client.get("/arxiv/statistics")


class TestDateIndexSorting:
    def test_date_indexes_returns_service_order(self, client, mock_paper_service):
        indexes = [
            {"date": "2024-01-17", "total_count": 150, "fetched_at": "2024-01-17T00:00:00"},
            {"date": "2024-01-16", "total_count": 120, "fetched_at": "2024-01-16T00:00:00"},
            {"date": "2024-01-15", "total_count": 100, "fetched_at": "2024-01-15T00:00:00"},
        ]
        mock_paper_service.get_all_date_indexes.return_value = indexes
        
        response = client.get("/arxiv/date-indexes")
        
        assert response.status_code == 200
        result_indexes = response.json()["indexes"]
        assert result_indexes[0]["date"] == "2024-01-17"
        assert result_indexes[1]["date"] == "2024-01-16"
        assert result_indexes[2]["date"] == "2024-01-15"


class TestQueryPapersEmptyResult:
    def test_query_papers_no_papers_for_date(self, client, mock_paper_service):
        mock_paper_service.query_papers = AsyncMock(return_value={
            "papers": [],
            "total": 0,
            "start": 0,
            "max_results": 50,
        })
        
        response = client.get("/arxiv/query?date=2024-01-15")
        
        assert response.status_code == 200
        assert response.json()["papers"] == []
        assert response.json()["total"] == 0
