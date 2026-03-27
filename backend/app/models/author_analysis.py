from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any


@dataclass
class AuthorStats:
    """Author statistics"""
    display_name: str = ""
    paper_count: int = 0
    first_paper_year: Optional[int] = None
    latest_paper_year: Optional[int] = None
    categories: Dict[str, int] = field(default_factory=dict)
    collaborator_count: int = 0


@dataclass
class CollaborationGraph:
    """Collaboration network graph"""
    authors: Dict[str, AuthorStats]
    edges: Dict[Tuple[str, str], int]
    author_papers: Dict[str, Set[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "authors": {
                aid: {
                    "display_name": stats.display_name,
                    "paper_count": stats.paper_count,
                    "first_paper_year": stats.first_paper_year,
                    "latest_paper_year": stats.latest_paper_year,
                    "categories": stats.categories,
                    "collaborator_count": stats.collaborator_count,
                }
                for aid, stats in self.authors.items()
            },
            "edges": [
                {"source": a1, "target": a2, "weight": w}
                for (a1, a2), w in self.edges.items()
            ],
            "total_authors": len(self.authors),
            "total_edges": len(self.edges),
        }


@dataclass
class AuthorRank:
    """Author ranking data"""
    author_id: str
    name: str
    paper_count: int
    pagerank: float
    degree_centrality: float
    betweenness_centrality: float
    clustering_coeff: float
    primary_category: Optional[str]
    first_year: Optional[int]
    latest_year: Optional[int]
    calculated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "author_id": self.author_id,
            "name": self.name,
            "paper_count": self.paper_count,
            "pagerank": self.pagerank,
            "degree_centrality": self.degree_centrality,
            "betweenness_centrality": self.betweenness_centrality,
            "clustering_coeff": self.clustering_coeff,
            "primary_category": self.primary_category,
            "first_year": self.first_year,
            "latest_year": self.latest_year,
            "calculated_at": self.calculated_at,
        }


@dataclass
class AuthorAnalysisResult:
    """Author analysis result"""
    total_papers: int
    total_authors: int
    total_edges: int
    top_authors: List[Dict[str, Any]]
    status: str = "success"
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_papers": self.total_papers,
            "total_authors": self.total_authors,
            "total_edges": self.total_edges,
            "top_authors": self.top_authors,
            "status": self.status,
            "message": self.message,
        }
