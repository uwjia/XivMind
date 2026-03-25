import pytest
from unittest.mock import Mock, patch

from app.services.author_profile_service import AuthorProfileService


class TestAuthorProfileService:
    @pytest.fixture
    def paper_service(self):
        return Mock()

    @pytest.fixture
    def service(self, paper_service):
        return AuthorProfileService(paper_service)

    def test_get_author_profile_empty(self, service, paper_service):
        paper_service.query_papers_by_author.return_value = {"papers": [], "total": 0}
        
        result = service.get_author_profile("John Doe")
        
        assert result["name"] == "John Doe"
        assert result["total_papers"] == 0
        assert result["first_paper_year"] is None
        assert result["latest_paper_year"] is None
        assert result["active_years"] == 0
        assert result["categories"] == []
        assert result["yearly_papers"] == []
        assert result["collaborators"] == []
        assert result["title_keywords"] == []

    def test_get_author_profile_single_paper(self, service, paper_service):
        paper_service.query_papers_by_author.return_value = {
            "papers": [{
                "id": "2301.12345",
                "title": "Test Paper",
                "authors": ["John Doe", "Jane Smith"],
                "abstract": "This is a test paper about machine learning.",
                "primary_category": "cs.AI",
                "categories": ["cs.AI", "cs.LG"],
                "published": "2023-06-15T00:00:00",
            }],
            "total": 1
        }
        
        result = service.get_author_profile("John Doe")
        
        assert result["name"] == "John Doe"
        assert result["total_papers"] == 1
        assert result["first_paper_year"] == 2023
        assert result["latest_paper_year"] == 2023
        assert result["active_years"] == 1
        assert len(result["categories"]) > 0
        assert len(result["collaborators"]) == 1
        assert result["collaborators"][0]["name"] == "Jane Smith"
        assert "title_keywords" in result

    def test_get_author_profile_multiple_papers(self, service, paper_service):
        paper_service.query_papers_by_author.return_value = {
            "papers": [
                {
                    "id": "2301.12345",
                    "title": "Paper 1",
                    "authors": ["John Doe", "Jane Smith"],
                    "abstract": "Abstract 1",
                    "primary_category": "cs.AI",
                    "categories": ["cs.AI"],
                    "published": "2023-06-15T00:00:00",
                },
                {
                    "id": "2301.12346",
                    "title": "Paper 2",
                    "authors": ["John Doe", "Bob Wilson"],
                    "abstract": "Abstract 2",
                    "primary_category": "cs.LG",
                    "categories": ["cs.LG", "cs.AI"],
                    "published": "2022-03-10T00:00:00",
                },
                {
                    "id": "2301.12347",
                    "title": "Paper 3",
                    "authors": ["John Doe"],
                    "abstract": "Abstract 3",
                    "primary_category": "cs.AI",
                    "categories": ["cs.AI"],
                    "published": "2021-01-20T00:00:00",
                },
            ],
            "total": 3
        }
        
        result = service.get_author_profile("John Doe")
        
        assert result["total_papers"] == 3
        assert result["first_paper_year"] == 2021
        assert result["latest_paper_year"] == 2023
        assert result["active_years"] == 3
        assert len(result["yearly_papers"]) == 3
        assert len(result["collaborators"]) == 2

    def test_extract_years(self, service):
        papers = [
            {"published": "2023-06-15T00:00:00"},
            {"published": "2022-03-10T00:00:00"},
            {"published": "2021-01-20T00:00:00"},
            {"published": "invalid"},
            {"published": None},
        ]
        
        years = service._extract_years(papers)
        
        assert sorted(years) == [2021, 2022, 2023]

    def test_analyze_categories(self, service):
        papers = [
            {"primary_category": "cs.AI", "categories": ["cs.AI", "cs.LG"]},
            {"primary_category": "cs.AI", "categories": ["cs.AI"]},
            {"primary_category": "cs.LG", "categories": ["cs.LG", "cs.CV"]},
        ]
        
        result = service._analyze_categories(papers)
        
        assert len(result) > 0
        assert result[0]["category"] == "cs.AI"
        assert result[0]["count"] == 2

    def test_analyze_yearly_papers(self, service):
        papers = [
            {"published": "2023-06-15T00:00:00"},
            {"published": "2023-03-10T00:00:00"},
            {"published": "2022-01-20T00:00:00"},
        ]
        
        result = service._analyze_yearly_papers(papers)
        
        assert len(result) == 2
        assert result[0]["year"] == 2022
        assert result[0]["count"] == 1
        assert result[1]["year"] == 2023
        assert result[1]["count"] == 2

    def test_analyze_collaborators(self, service):
        papers = [
            {"authors": ["John Doe", "Jane Smith", "Bob Wilson"]},
            {"authors": ["John Doe", "Jane Smith"]},
            {"authors": ["John Doe", "Alice Brown"]},
        ]
        
        result = service._analyze_collaborators(papers, "John Doe")
        
        assert len(result) == 3
        assert result[0]["name"] == "Jane Smith"
        assert result[0]["collaboration_count"] == 2

    def test_extract_keywords(self, service):
        papers = [
            {"title": "Deep Learning for NLP", "abstract": "This paper presents neural network approaches for natural language processing."},
            {"title": "Neural Networks in Computer Vision", "abstract": "We propose a deep learning method for image classification."},
        ]
        
        result = service._extract_keywords(papers)
        
        assert len(result) > 0
        keywords = [k["word"] for k in result]
        assert "neural" in keywords or "learning" in keywords

    def test_get_category_names(self, service):
        names = service._get_category_names()
        
        assert names["cs.AI"] == "Artificial Intelligence"
        assert names["cs.LG"] == "Machine Learning"
        assert names["cs.CV"] == "Computer Vision"

    def test_get_stop_words(self, service):
        stop_words = service._get_stop_words()
        
        assert "the" in stop_words
        assert "a" in stop_words
        assert "and" in stop_words
        assert "paper" in stop_words
        assert "method" in stop_words
