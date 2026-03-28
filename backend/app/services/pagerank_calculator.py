import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import networkx as nx

from app.models.author_analysis import CollaborationGraph
from app.config import get_settings

logger = logging.getLogger(__name__)


class PageRankCalculatorBase(ABC):
    """Abstract base class for PageRank calculators"""
    
    def __init__(self, graph: CollaborationGraph):
        self.graph = graph
        self._author_list: List[str] = []
        self._node_data: Dict[str, Dict[str, Any]] = {}
    
    def _prepare_graph_data(self):
        """Prepare common graph data structures"""
        self._author_list = list(self.graph.authors.keys())
        self._node_data = {}
        
        for author_id, stats in self.graph.authors.items():
            primary_cat = None
            if stats.categories:
                primary_cat = max(stats.categories.items(), key=lambda x: x[1])[0]
            
            self._node_data[author_id] = {
                'name': stats.display_name,
                'paper_count': stats.paper_count,
                'primary_category': primary_cat,
                'first_year': stats.first_paper_year,
                'latest_year': stats.latest_paper_year,
                'collaborator_count': stats.collaborator_count,
            }
    
    @abstractmethod
    def calculate_pagerank(
        self,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, float]:
        """Calculate PageRank values"""
        pass
    
    @abstractmethod
    def calculate_all_metrics(self, alpha: float = 0.85) -> Dict[str, Dict[str, float]]:
        """Calculate all network metrics"""
        pass
    
    def get_top_authors(
        self,
        pagerank: Dict[str, float],
        top_n: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get authors with highest PageRank"""
        sorted_authors = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        result = []
        for rank, (author_id, score) in enumerate(sorted_authors, 1):
            node_data = self._node_data.get(author_id, {})
            result.append({
                'rank': rank,
                'author_id': author_id,
                'name': node_data.get('name', author_id),
                'pagerank': score,
                'paper_count': node_data.get('paper_count', 0),
                'primary_category': node_data.get('primary_category'),
                'collaborator_count': node_data.get('collaborator_count', 0),
            })
        
        return result


class NetworkXPageRankCalculator(PageRankCalculatorBase):
    """PageRank calculator using NetworkX"""
    
    def __init__(self, graph: CollaborationGraph):
        super().__init__(graph)
        self.nx_graph = self._build_networkx_graph()
    
    def _build_networkx_graph(self) -> nx.Graph:
        """Build NetworkX graph"""
        self._prepare_graph_data()
        
        G = nx.Graph()
        
        for author_id in self._author_list:
            G.add_node(author_id, **self._node_data[author_id])
        
        for (a1, a2), weight in self.graph.edges.items():
            G.add_edge(a1, a2, weight=weight)
        
        return G
    
    def calculate_pagerank(
        self,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, float]:
        """Calculate PageRank values using NetworkX"""
        logger.info(f"Calculating PageRank with NetworkX (alpha={alpha}, max_iter={max_iter})...")
        
        pagerank = nx.pagerank(
            self.nx_graph,
            alpha=alpha,
            max_iter=max_iter,
            tol=tol,
            weight='weight',
        )
        
        logger.info(f"PageRank calculation complete, {len(pagerank)} nodes")
        return pagerank
    
    def calculate_all_metrics(self, alpha: float = 0.85) -> Dict[str, Dict[str, float]]:
        """Calculate all network metrics using NetworkX"""
        logger.info("Calculating network metrics with NetworkX...")
        
        metrics: Dict[str, Dict[str, float]] = {
            'pagerank': self.calculate_pagerank(alpha=alpha),
            'degree': dict(nx.degree_centrality(self.nx_graph)),
            'clustering': dict(nx.clustering(self.nx_graph)),
        }
        
        n_nodes = self.nx_graph.number_of_nodes()
        threshold = get_settings().PAGERANK_BETWEENNESS_THRESHOLD
        if n_nodes > threshold:
            logger.warning(
                f"Graph has {n_nodes} nodes (threshold: {threshold}). Skipping betweenness centrality calculation "
                "(too slow for large graphs). Using 0.0 for all nodes."
            )
            metrics['betweenness'] = {node: 0.0 for node in self.nx_graph.nodes()}
        else:
            logger.info("Calculating betweenness centrality...")
            k = min(1000, n_nodes)
            metrics['betweenness'] = dict(nx.betweenness_centrality(self.nx_graph, k=k if k < n_nodes else None))
        
        logger.info("Network metrics calculation complete (NetworkX)")
        return metrics


class IGraphPageRankCalculator(PageRankCalculatorBase):
    """PageRank calculator using igraph"""
    
    def __init__(self, graph: CollaborationGraph):
        super().__init__(graph)
        self.igraph_obj = self._build_igraph()
    
    def _build_igraph(self):
        """Build igraph from CollaborationGraph"""
        try:
            import igraph as ig
        except ImportError:
            raise ImportError("igraph is not installed. Install it with: pip install igraph")
        
        self._prepare_graph_data()
        
        n_nodes = len(self._author_list)
        author_id_to_idx = {aid: idx for idx, aid in enumerate(self._author_list)}
        
        edges = []
        weights = []
        for (a1, a2), weight in self.graph.edges.items():
            if a1 in author_id_to_idx and a2 in author_id_to_idx:
                edges.append((author_id_to_idx[a1], author_id_to_idx[a2]))
                weights.append(weight)
        
        g = ig.Graph(n=n_nodes, edges=edges, directed=False)
        g.es['weight'] = weights
        
        for idx, author_id in enumerate(self._author_list):
            node_data = self._node_data[author_id]
            g.vs[idx]['name'] = author_id
            g.vs[idx]['display_name'] = node_data['name']
            g.vs[idx]['paper_count'] = node_data['paper_count']
            g.vs[idx]['primary_category'] = node_data['primary_category']
            g.vs[idx]['collaborator_count'] = node_data['collaborator_count']
        
        self._author_id_to_idx = author_id_to_idx
        
        return g
    
    def calculate_pagerank(
        self,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, float]:
        """Calculate PageRank values using igraph"""
        logger.info(f"Calculating PageRank with igraph (alpha={alpha}, max_iter={max_iter})...")
        
        pagerank_values = self.igraph_obj.pagerank(
            weights='weight',
            damping=alpha,
        )
        
        pagerank = {}
        for idx, author_id in enumerate(self._author_list):
            pagerank[author_id] = pagerank_values[idx]
        
        logger.info(f"PageRank calculation complete, {len(pagerank)} nodes")
        return pagerank
    
    def calculate_all_metrics(self, alpha: float = 0.85) -> Dict[str, Dict[str, float]]:
        """Calculate all network metrics using igraph"""
        logger.info("Calculating network metrics with igraph...")
        
        pagerank = self.calculate_pagerank(alpha=alpha)
        
        n = len(self._author_list)
        
        logger.info(f"Calculating degree centrality for {n} nodes...")
        degree_values = self.igraph_obj.degree()
        max_possible_degree = n - 1 if n > 1 else 1
        degree_centrality = dict(zip(
            self._author_list,
            (d / max_possible_degree for d in degree_values)
        ))
        logger.info(f"Degree centrality calculated for {len(degree_centrality)} nodes")
        
        logger.info("Calculating clustering coefficient (this may take a while for large graphs)...")
        clustering = {}
        try:
            clustering_values = self.igraph_obj.transitivity_local_undirected(mode="zero")
            clustering = dict(zip(
                self._author_list,
                (float(v) if v is not None else 0.0 for v in clustering_values)
            ))
            logger.info("Clustering coefficient calculation complete")
        except Exception as e:
            logger.warning(f"Clustering coefficient calculation failed: {e}, using default values")
            clustering = {author_id: 0.0 for author_id in self._author_list}
        
        n_nodes = self.igraph_obj.vcount()
        threshold = get_settings().PAGERANK_BETWEENNESS_THRESHOLD
        if n_nodes > threshold:
            logger.warning(
                f"Graph has {n_nodes} nodes (threshold: {threshold}). Skipping betweenness centrality calculation "
                "(too slow for large graphs). Using 0.0 for all nodes."
            )
            betweenness = {author_id: 0.0 for author_id in self._author_list}
        else:
            logger.info(f"Calculating betweenness centrality for {n_nodes} nodes...")
            betweenness = {}
            try:
                betweenness_values = self.igraph_obj.betweenness(weights='weight', normalized=True)
                betweenness = dict(zip(
                    self._author_list,
                    (float(v) for v in betweenness_values)
                ))
                logger.info("Betweenness centrality calculation complete")
            except Exception as e:
                logger.warning(f"Betweenness centrality calculation failed: {e}, using default values")
                betweenness = {author_id: 0.0 for author_id in self._author_list}
        
        metrics: Dict[str, Dict[str, float]] = {
            'pagerank': pagerank,
            'degree': degree_centrality,
            'clustering': clustering,
            'betweenness': betweenness,
        }
        
        logger.info("Network metrics calculation complete (IGraph)")
        return metrics


def get_pagerank_calculator(
    graph: CollaborationGraph,
    algorithm: str = "networkx",
) -> PageRankCalculatorBase:
    """Factory function to get the appropriate PageRank calculator"""
    if algorithm == "igraph":
        logger.info("Using igraph PageRank calculator")
        return IGraphPageRankCalculator(graph)
    else:
        logger.info("Using NetworkX PageRank calculator")
        return NetworkXPageRankCalculator(graph)
