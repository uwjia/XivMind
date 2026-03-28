import pytest
from unittest.mock import patch

from app.models.author_analysis import AuthorStats, CollaborationGraph
from app.services.pagerank_calculator import (
    PageRankCalculatorBase,
    NetworkXPageRankCalculator,
    get_pagerank_calculator,
)

IGRAPH_AVAILABLE = False
try:
    import igraph
    IGRAPH_AVAILABLE = True
except ImportError:
    pass

skip_if_no_igraph = pytest.mark.skipif(
    not IGRAPH_AVAILABLE,
    reason="igraph is not installed"
)


class TestPageRankCalculatorBase:
    """Tests for PageRankCalculatorBase abstract class"""

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


class TestNetworkXPageRankCalculator(TestPageRankCalculatorBase):
    """Tests for NetworkXPageRankCalculator"""

    def test_build_networkx_graph(self, sample_graph):
        calculator = NetworkXPageRankCalculator(sample_graph)
        
        assert calculator.nx_graph.number_of_nodes() == 3
        assert calculator.nx_graph.number_of_edges() == 3

    def test_calculate_pagerank(self, sample_graph):
        calculator = NetworkXPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank(alpha=0.85)
        
        assert len(pagerank) == 3
        assert all(0 <= v <= 1 for v in pagerank.values())

    def test_calculate_pagerank_values_sum_to_one(self, sample_graph):
        calculator = NetworkXPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank(alpha=0.85)
        
        total = sum(pagerank.values())
        assert abs(total - 1.0) < 0.0001

    def test_calculate_all_metrics(self, sample_graph):
        calculator = NetworkXPageRankCalculator(sample_graph)
        
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
        calculator = NetworkXPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank()
        
        top_authors = calculator.get_top_authors(pagerank, top_n=2)
        
        assert len(top_authors) == 2
        assert "rank" in top_authors[0]
        assert "author_id" in top_authors[0]
        assert "name" in top_authors[0]
        assert "pagerank" in top_authors[0]

    def test_get_top_authors_sorted_by_pagerank(self, sample_graph):
        calculator = NetworkXPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank()
        
        top_authors = calculator.get_top_authors(pagerank, top_n=3)
        
        for i in range(len(top_authors) - 1):
            assert top_authors[i]["pagerank"] >= top_authors[i + 1]["pagerank"]


class TestIGraphPageRankCalculator(TestPageRankCalculatorBase):
    """Tests for IGraphPageRankCalculator"""

    @skip_if_no_igraph
    def test_build_igraph(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        
        assert calculator.igraph_obj.vcount() == 3
        assert calculator.igraph_obj.ecount() == 3

    @skip_if_no_igraph
    def test_calculate_pagerank(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank(alpha=0.85)
        
        assert len(pagerank) == 3
        assert all(0 <= v <= 1 for v in pagerank.values())

    @skip_if_no_igraph
    def test_calculate_pagerank_values_sum_to_one(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank(alpha=0.85)
        
        total = sum(pagerank.values())
        assert abs(total - 1.0) < 0.0001

    @skip_if_no_igraph
    def test_calculate_all_metrics(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        metrics = calculator.calculate_all_metrics(alpha=0.85)
        
        assert "pagerank" in metrics
        assert "degree" in metrics
        assert "clustering" in metrics
        assert "betweenness" in metrics
        
        assert len(metrics["pagerank"]) == 3
        assert len(metrics["degree"]) == 3
        assert len(metrics["clustering"]) == 3
        assert len(metrics["betweenness"]) == 3

    @skip_if_no_igraph
    def test_get_top_authors(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank()
        
        top_authors = calculator.get_top_authors(pagerank, top_n=2)
        
        assert len(top_authors) == 2
        assert "rank" in top_authors[0]
        assert "author_id" in top_authors[0]
        assert "name" in top_authors[0]
        assert "pagerank" in top_authors[0]

    @skip_if_no_igraph
    def test_get_top_authors_sorted_by_pagerank(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(sample_graph)
        pagerank = calculator.calculate_pagerank()
        
        top_authors = calculator.get_top_authors(pagerank, top_n=3)
        
        for i in range(len(top_authors) - 1):
            assert top_authors[i]["pagerank"] >= top_authors[i + 1]["pagerank"]


class TestAlgorithmConsistency(TestPageRankCalculatorBase):
    """Tests for consistency between NetworkX and IGraph implementations"""

    @skip_if_no_igraph
    def test_pagerank_ranking_consistency(self, sample_graph):
        """Test that both algorithms produce similar rankings"""
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        nx_calculator = NetworkXPageRankCalculator(sample_graph)
        ig_calculator = IGraphPageRankCalculator(sample_graph)
        
        nx_pagerank = nx_calculator.calculate_pagerank(alpha=0.85)
        ig_pagerank = ig_calculator.calculate_pagerank(alpha=0.85)
        
        nx_ranking = sorted(nx_pagerank.items(), key=lambda x: x[1], reverse=True)
        ig_ranking = sorted(ig_pagerank.items(), key=lambda x: x[1], reverse=True)
        
        nx_order = [author_id for author_id, _ in nx_ranking]
        ig_order = [author_id for author_id, _ in ig_ranking]
        
        assert nx_order == ig_order, f"Rankings differ: NX={nx_order}, IG={ig_order}"

    @skip_if_no_igraph
    def test_pagerank_values_similar(self, sample_graph):
        """Test that PageRank values are within acceptable tolerance"""
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        nx_calculator = NetworkXPageRankCalculator(sample_graph)
        ig_calculator = IGraphPageRankCalculator(sample_graph)
        
        nx_pagerank = nx_calculator.calculate_pagerank(alpha=0.85)
        ig_pagerank = ig_calculator.calculate_pagerank(alpha=0.85)
        
        for author_id in nx_pagerank:
            nx_val = nx_pagerank[author_id]
            ig_val = ig_pagerank[author_id]
            
            assert abs(nx_val - ig_val) < 0.01, \
                f"PageRank values differ significantly for {author_id}: NX={nx_val}, IG={ig_val}"

    @skip_if_no_igraph
    def test_degree_centrality_ranking_consistency(self, sample_graph):
        """Test that degree centrality rankings are consistent"""
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        nx_calculator = NetworkXPageRankCalculator(sample_graph)
        ig_calculator = IGraphPageRankCalculator(sample_graph)
        
        nx_metrics = nx_calculator.calculate_all_metrics(alpha=0.85)
        ig_metrics = ig_calculator.calculate_all_metrics(alpha=0.85)
        
        nx_degree = nx_metrics['degree']
        ig_degree = ig_metrics['degree']
        
        nx_ranking = sorted(nx_degree.items(), key=lambda x: x[1], reverse=True)
        ig_ranking = sorted(ig_degree.items(), key=lambda x: x[1], reverse=True)
        
        nx_order = [author_id for author_id, _ in nx_ranking]
        ig_order = [author_id for author_id, _ in ig_ranking]
        
        assert nx_order == ig_order, f"Degree rankings differ: NX={nx_order}, IG={ig_order}"


class TestGetPageRankCalculator(TestPageRankCalculatorBase):
    """Tests for get_pagerank_calculator factory function"""

    def test_factory_returns_networkx(self, sample_graph):
        calculator = get_pagerank_calculator(sample_graph, algorithm="networkx")
        assert isinstance(calculator, NetworkXPageRankCalculator)

    @skip_if_no_igraph
    def test_factory_returns_igraph(self, sample_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = get_pagerank_calculator(sample_graph, algorithm="igraph")
        assert isinstance(calculator, IGraphPageRankCalculator)

    def test_factory_default_is_networkx(self, sample_graph):
        calculator = get_pagerank_calculator(sample_graph)
        assert isinstance(calculator, NetworkXPageRankCalculator)


class TestEdgeCases:
    """Tests for edge cases"""

    @pytest.fixture
    def single_node_graph(self):
        authors = {
            "author_a": AuthorStats(
                display_name="Author A",
                paper_count=5,
                categories={"cs.AI": 5},
            ),
        }
        edges = {}
        author_papers = {"author_a": {"p1", "p2", "p3", "p4", "p5"}}
        return CollaborationGraph(authors=authors, edges=edges, author_papers=author_papers)

    def test_single_node_networkx(self, single_node_graph):
        calculator = NetworkXPageRankCalculator(single_node_graph)
        pagerank = calculator.calculate_pagerank()
        
        assert len(pagerank) == 1
        assert pagerank["author_a"] == 1.0

    @skip_if_no_igraph
    def test_single_node_igraph(self, single_node_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(single_node_graph)
        pagerank = calculator.calculate_pagerank()
        
        assert len(pagerank) == 1
        assert pagerank["author_a"] == 1.0

    @pytest.fixture
    def disconnected_graph(self):
        authors = {
            "author_a": AuthorStats(display_name="Author A", paper_count=5),
            "author_b": AuthorStats(display_name="Author B", paper_count=3),
        }
        edges = {}
        author_papers = {
            "author_a": {"p1", "p2", "p3", "p4", "p5"},
            "author_b": {"p6", "p7", "p8"},
        }
        return CollaborationGraph(authors=authors, edges=edges, author_papers=author_papers)

    def test_disconnected_nodes_networkx(self, disconnected_graph):
        calculator = NetworkXPageRankCalculator(disconnected_graph)
        pagerank = calculator.calculate_pagerank()
        
        assert len(pagerank) == 2
        total = sum(pagerank.values())
        assert abs(total - 1.0) < 0.0001

    @skip_if_no_igraph
    def test_disconnected_nodes_igraph(self, disconnected_graph):
        from app.services.pagerank_calculator import IGraphPageRankCalculator
        calculator = IGraphPageRankCalculator(disconnected_graph)
        pagerank = calculator.calculate_pagerank()
        
        assert len(pagerank) == 2
        total = sum(pagerank.values())
        assert abs(total - 1.0) < 0.0001
