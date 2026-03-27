import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import json

from app.services.author_analysis_service import (
    CollaborationNetworkBuilder,
    PageRankCalculator,
    AuthorRankService,
    AuthorCluster,
    AuthorDisambiguator,
    AuthorStats,
    CollaborationGraph,
)


class TestAuthorDisambiguator:
    """Tests for AuthorDisambiguator"""

    @pytest.fixture
    def disambiguator(self):
        return AuthorDisambiguator(similarity_threshold=0.1)

    def test_add_paper(self, disambiguator):
        paper = {
            "id": "2301.12345",
            "authors": ["Author One", "Author Two"],
            "primary_category": "cs.AI",
            "published": "2024-01-01",
        }
        
        disambiguator.add_paper(paper)
        
        assert "Author One" in disambiguator.name_to_papers
        assert "Author Two" in disambiguator.name_to_papers
        assert len(disambiguator.name_to_papers["Author One"]) == 1

    def test_disambiguate_single_paper_author(self, disambiguator):
        disambiguator.add_paper({
            "id": "paper1",
            "authors": ["Single Author"],
            "primary_category": "cs.AI",
            "published": "2024-01-01",
        })
        
        mapping = disambiguator.disambiguate_all()
        
        assert len(mapping) == 1
        assert "paper1:Single Author" in mapping

    def test_disambiguate_multiple_papers_same_collaborators(self, disambiguator):
        for i in range(3):
            disambiguator.add_paper({
                "id": f"paper{i}",
                "authors": ["Test Author", "Collaborator A"],
                "primary_category": "cs.AI",
                "published": f"2024-0{i}-01",
            })
        
        mapping = disambiguator.disambiguate_all()
        
        for i in range(3):
            key = f"paper{i}:Test Author"
            assert key in mapping
            assert mapping[key] == "test_author"

    def test_disambiguate_different_collaborators(self, disambiguator):
        disambiguator.add_paper({
            "id": "paper1",
            "authors": ["Test Author", "Collaborator A"],
            "primary_category": "cs.AI",
            "published": "2024-01-01",
        })
        disambiguator.add_paper({
            "id": "paper2",
            "authors": ["Test Author", "Collaborator B"],
            "primary_category": "cs.LG",
            "published": "2020-01-01",
        })
        
        mapping = disambiguator.disambiguate_all()
        
        key1 = "paper1:Test Author"
        key2 = "paper2:Test Author"
        assert key1 in mapping
        assert key2 in mapping

    def test_get_disambiguation_stats(self, disambiguator):
        disambiguator.add_paper({
            "id": "paper1",
            "authors": ["Author A"],
            "primary_category": "cs.AI",
            "published": "2024-01-01",
        })
        
        disambiguator.disambiguate_all()
        stats = disambiguator.get_disambiguation_stats()
        
        assert "total_names" in stats
        assert "total_clusters" in stats
        assert stats["total_names"] == 1


class TestCollaborationNetworkBuilder:
    """Tests for CollaborationNetworkBuilder"""

    @pytest.fixture
    def builder(self):
        return CollaborationNetworkBuilder(use_disambiguation=False)

    @pytest.fixture
    def builder_with_disambiguation(self):
        return CollaborationNetworkBuilder(use_disambiguation=True, similarity_threshold=0.1)

    def test_process_paper(self, builder):
        paper = {
            "id": "paper1",
            "authors": ["Author One", "Author Two"],
            "primary_category": "cs.AI",
            "published": "2024-01-15",
        }
        
        builder._process_paper(paper)
        
        assert len(builder.authors) == 2
        assert "author_one" in builder.authors
        assert "author_two" in builder.authors
        assert builder.authors["author_one"].paper_count == 1
        assert builder.authors["author_two"].paper_count == 1

    def test_process_paper_creates_edge(self, builder):
        paper = {
            "id": "paper1",
            "authors": ["Author One", "Author Two"],
            "primary_category": "cs.AI",
            "published": "2024-01-15",
        }
        
        builder._process_paper(paper)
        
        edge_key = tuple(sorted(["author_one", "author_two"]))
        assert edge_key in builder.edges
        assert builder.edges[edge_key] == 1

    def test_process_paper_multiple_collaborations(self, builder):
        paper = {
            "id": "paper1",
            "authors": ["A", "B", "C"],
            "primary_category": "cs.AI",
            "published": "2024-01-15",
        }
        
        builder._process_paper(paper)
        
        assert len(builder.edges) == 3

    def test_extract_year(self, builder):
        assert builder._extract_year("2024-01-15T00:00:00") == 2024
        assert builder._extract_year("2023-12-31") == 2023
        assert builder._extract_year(None) is None
        assert builder._extract_year("") is None
        assert builder._extract_year("invalid") is None

    def test_filter_low_activity(self, builder):
        builder.authors = {
            "author_a": AuthorStats(display_name="Author A", paper_count=5),
            "author_b": AuthorStats(display_name="Author B", paper_count=1),
            "author_c": AuthorStats(display_name="Author C", paper_count=10),
        }
        builder.edges = {
            ("author_a", "author_b"): 1,
            ("author_a", "author_c"): 2,
        }
        builder.author_papers = {
            "author_a": {"p1", "p2", "p3", "p4", "p5"},
            "author_b": {"p1"},
            "author_c": {"p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10"},
        }
        
        builder._filter_low_activity(min_papers=3)
        
        assert "author_a" in builder.authors
        assert "author_b" not in builder.authors
        assert "author_c" in builder.authors
        assert ("author_a", "author_b") not in builder.edges

    def test_calculate_collaborator_counts(self, builder):
        builder.authors = {
            "author_a": AuthorStats(display_name="Author A"),
            "author_b": AuthorStats(display_name="Author B"),
            "author_c": AuthorStats(display_name="Author C"),
        }
        builder.edges = {
            ("author_a", "author_b"): 2,
            ("author_a", "author_c"): 1,
        }
        
        builder._calculate_collaborator_counts()
        
        assert builder.authors["author_a"].collaborator_count == 2
        assert builder.authors["author_b"].collaborator_count == 1
        assert builder.authors["author_c"].collaborator_count == 1

    def test_build_from_paper_reader(self, builder):
        mock_reader = Mock()
        mock_reader.get_total_count = Mock(return_value=2)
        mock_reader.iter_papers_batch = Mock(return_value=[[
            {
                "id": "paper1",
                "authors": ["Author One", "Author Two"],
                "primary_category": "cs.AI",
                "published": "2024-01-15",
            },
            {
                "id": "paper2",
                "authors": ["Author One", "Author Three"],
                "primary_category": "cs.LG",
                "published": "2024-02-15",
            },
        ]])
        
        graph = builder.build_from_paper_reader(mock_reader, min_papers=1)
        
        assert len(graph.authors) == 3
        assert len(graph.edges) == 2


class TestPageRankCalculator:
    """Tests for PageRankCalculator"""

    @pytest.fixture
    def sample_graph(self):
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 5, "cs.LG": 5},
            ),
            "author_b": AuthorStats(
                display_name="Author B",
                paper_count=8,
                categories={"cs.AI": 8},
            ),
            "author_c": AuthorStats(
                display_name="Author C",
                paper_count=5,
                categories={"cs.LG": 5},
            ),
        }
        edges = {
            ("author_a", "author_b"): 3,
            ("author_a", "author_c"): 2,
            ("author_b", "author_c"): 1,
        }
        author_papers = {
            "author_a": {"p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10"},
            "author_b": {"p1", "p2", "p3", "p11", "p12", "p13", "p14", "p15"},
            "author_c": {"p4", "p5", "p16", "p17", "p18"},
        }
        return CollaborationGraph(authors=authors, edges=edges, author_papers=author_papers)

    def test_build_networkx_graph(self, sample_graph):
        calculator = PageRankCalculator(sample_graph)
        
        assert calculator.nx_graph.number_of_nodes() == 3
        assert calculator.nx_graph.number_of_edges() == 3

    def test_calculate_pagerank(self, sample_graph):
        calculator = PageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank(alpha=0.85)
        
        assert len(pagerank) == 3
        assert all(0 <= v <= 1 for v in pagerank.values())

    def test_calculate_all_metrics(self, sample_graph):
        calculator = PageRankCalculator(sample_graph)
        
        with patch('networkx.betweenness_centrality') as mock_betweenness:
            mock_betweenness.return_value = {
                "author_a": 0.5,
                "author_b": 0.3,
                "author_c": 0.2,
            }
            metrics = calculator.calculate_all_metrics(alpha=0.85)
        
        assert "pagerank" in metrics
        assert "degree" in metrics
        assert "clustering" in metrics
        assert "betweenness" in metrics
        
        assert len(metrics["pagerank"]) == 3
        assert len(metrics["degree"]) == 3

    def test_get_top_authors(self, sample_graph):
        calculator = PageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank()
        
        top_authors = calculator.get_top_authors(pagerank, top_n=2)
        
        assert len(top_authors) == 2
        assert "rank" in top_authors[0]
        assert "author_id" in top_authors[0]
        assert "name" in top_authors[0]
        assert "pagerank" in top_authors[0]


class TestAuthorRankService:
    """Tests for AuthorRankService"""

    @pytest.fixture
    def service(self):
        return AuthorRankService()

    @pytest.fixture
    def mock_repo(self):
        repo = Mock()
        repo.get_top_authors = Mock(return_value=[
            {
                "author_id": "author_a",
                "name": "Author A",
                "paper_count": 10,
                "pagerank": 0.5,
                "degree_centrality": 0.3,
                "betweenness_centrality": 0.2,
                "clustering_coeff": 0.8,
                "primary_category": "cs.AI",
            }
        ])
        repo.count_authors = Mock(return_value=100)
        repo.get_author_by_id = Mock(return_value={
            "author_id": "author_a",
            "name": "Author A",
            "paper_count": 10,
        })
        repo.clear_all = Mock()
        repo.get_disambiguation_stats = Mock(return_value={"total_names": 50})
        return repo

    def test_get_top_authors(self, service, mock_repo):
        with patch.object(service, '_get_repo', return_value=mock_repo):
            result = service.get_top_authors(
                metric="pagerank",
                category="cs.AI",
                name_search="Author",
                limit=10,
                offset=0,
            )
        
        assert "authors" in result
        assert "total" in result
        assert result["total"] == 100
        assert len(result["authors"]) == 1
        mock_repo.get_top_authors.assert_called_once_with(
            metric="pagerank",
            limit=10,
            offset=0,
            category="cs.AI",
            name_search="Author",
        )

    def test_get_author_by_id(self, service, mock_repo):
        with patch.object(service, '_get_repo', return_value=mock_repo):
            result = service.get_author_by_id("author_a")
        
        assert result is not None
        assert result["author_id"] == "author_a"
        mock_repo.get_author_by_id.assert_called_once_with("author_a")

    def test_get_statistics(self, service, mock_repo):
        mock_reader = Mock()
        mock_reader.get_total_count = Mock(return_value=1000)
        
        with patch.object(service, '_get_repo', return_value=mock_repo):
            with patch('app.services.author_analysis_service.get_paper_reader', return_value=mock_reader):
                result = service.get_statistics()
        
        assert "total_papers" in result
        assert "total_analyzed_authors" in result
        assert result["total_papers"] == 1000
        assert result["total_analyzed_authors"] == 100

    def test_clear_all(self, service, mock_repo):
        with patch.object(service, '_get_repo', return_value=mock_repo):
            service.clear_all()
        
        mock_repo.clear_all.assert_called_once()

    def test_get_disambiguation_stats(self, service, mock_repo):
        with patch.object(service, '_get_repo', return_value=mock_repo):
            result = service.get_disambiguation_stats()
        
        assert "total_names" in result
        mock_repo.get_disambiguation_stats.assert_called_once()


class TestAuthorCluster:
    """Tests for AuthorCluster dataclass"""

    def test_unique_id_cluster_zero(self):
        cluster = AuthorCluster(
            original_name="Test Author",
            cluster_id=0,
        )
        
        assert cluster.unique_id == "test_author"

    def test_unique_id_cluster_nonzero(self):
        cluster = AuthorCluster(
            original_name="Test Author",
            cluster_id=2,
        )
        
        assert cluster.unique_id == "test_author#2"

    def test_unique_id_with_spaces(self):
        cluster = AuthorCluster(
            original_name="Test Author Name",
            cluster_id=1,
        )
        
        assert cluster.unique_id == "test_author_name#1"


class TestAuthorStats:
    """Tests for AuthorStats dataclass"""

    def test_default_values(self):
        stats = AuthorStats(display_name="Test Author")
        
        assert stats.display_name == "Test Author"
        assert stats.paper_count == 0
        assert stats.first_paper_year is None
        assert stats.latest_paper_year is None
        assert stats.categories == {}
        assert stats.collaborator_count == 0

    def test_custom_values(self):
        stats = AuthorStats(
            display_name="Test Author",
            paper_count=10,
            first_paper_year=2020,
            latest_paper_year=2024,
            categories={"cs.AI": 5, "cs.LG": 5},
            collaborator_count=15,
        )
        
        assert stats.paper_count == 10
        assert stats.first_paper_year == 2020
        assert stats.latest_paper_year == 2024
        assert stats.categories["cs.AI"] == 5
        assert stats.collaborator_count == 15


class TestCollaborationGraph:
    """Tests for CollaborationGraph dataclass"""

    def test_to_dict(self):
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=10,
                categories={"cs.AI": 10},
            ),
        }
        edges = {("author_a", "author_b"): 3}
        author_papers = {"author_a": {"p1", "p2"}}
        
        graph = CollaborationGraph(
            authors=authors,
            edges=edges,
            author_papers=author_papers,
        )
        
        result = graph.to_dict()
        
        assert "authors" in result
        assert "edges" in result
        assert "total_authors" in result
        assert "total_edges" in result
        assert result["total_authors"] == 1
        assert result["total_edges"] == 1
