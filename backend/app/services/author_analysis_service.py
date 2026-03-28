import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple

import networkx as nx

from app.db.factory import get_author_rank_repository, get_paper_reader
from app.db.base import PaperReader
from app.models.author_analysis import (
    AuthorAnalysisResult,
    AuthorRank,
    AuthorStats,
    CollaborationGraph,
)
from app.services.pagerank_calculator import get_pagerank_calculator

logger = logging.getLogger(__name__)


@dataclass
class AuthorCluster:
    """Author cluster for disambiguation"""
    original_name: str
    cluster_id: int
    papers: Set[str] = field(default_factory=set)
    collaborators: Set[str] = field(default_factory=set)
    categories: Dict[str, int] = field(default_factory=dict)
    years: List[int] = field(default_factory=list)
    
    @property
    def unique_id(self) -> str:
        if self.cluster_id == 0:
            return self.original_name.lower().replace(" ", "_")
        return f"{self.original_name.lower().replace(' ', '_')}#{self.cluster_id}"


class AuthorDisambiguator:
    """
    Author disambiguation based on collaboration network.
    
    Algorithm:
    1. For each author name, collect all papers
    2. Build a paper graph where edges connect papers sharing collaborators
    3. Use connected components to identify distinct author clusters
    4. Each cluster represents a unique author entity
    
    Key insight: Two papers by the same author name with completely 
    different collaborators are likely different people.
    """
    
    def __init__(self, similarity_threshold: float = 0.1):
        self.similarity_threshold = similarity_threshold
        self.name_to_papers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.disambiguated_authors: Dict[str, AuthorCluster] = {}
        self.stats = {
            "total_names": 0,
            "names_disambiguated": 0,
            "total_clusters": 0,
            "papers_processed": 0,
        }
    
    def add_paper(self, paper: Dict[str, Any]):
        """Add a paper to the disambiguation process"""
        authors = paper.get("authors", [])
        paper_id = paper.get("id", "")
        category = paper.get("primary_category", "")
        year = self._extract_year(paper.get("published"))
        
        for author_name in authors:
            if not author_name:
                continue
            
            self.name_to_papers[author_name].append({
                "paper_id": paper_id,
                "coauthors": [a for a in authors if a != author_name],
                "category": category,
                "year": year,
            })
            self.stats["papers_processed"] += 1
    
    def disambiguate_all(self) -> Dict[str, str]:
        """
        Run disambiguation for all author names.
        
        Returns:
            Dict mapping paper_id + author_name to unique author_id
        """
        logger.info(f"Starting disambiguation for {len(self.name_to_papers)} unique names...")
        
        paper_author_to_cluster: Dict[str, str] = {}
        
        for author_name, papers in self.name_to_papers.items():
            self.stats["total_names"] += 1
            
            if len(papers) == 1:
                cluster = AuthorCluster(
                    original_name=author_name,
                    cluster_id=0,
                    papers={papers[0]["paper_id"]},
                )
                key = f"{papers[0]['paper_id']}:{author_name}"
                paper_author_to_cluster[key] = cluster.unique_id
                self.disambiguated_authors[cluster.unique_id] = cluster
                self.stats["total_clusters"] += 1
                continue
            
            clusters = self._cluster_papers(author_name, papers)
            
            if len(clusters) > 1:
                self.stats["names_disambiguated"] += 1
            
            for cluster in clusters:
                self.disambiguated_authors[cluster.unique_id] = cluster
                self.stats["total_clusters"] += 1
                
                for paper_id in cluster.papers:
                    key = f"{paper_id}:{author_name}"
                    paper_author_to_cluster[key] = cluster.unique_id
        
        logger.info(f"Disambiguation complete: {self.stats['names_disambiguated']} names split into multiple clusters")
        logger.info(f"Total clusters created: {self.stats['total_clusters']}")
        
        return paper_author_to_cluster
    
    def _cluster_papers(self, author_name: str, papers: List[Dict[str, Any]]) -> List[AuthorCluster]:
        """
        Cluster papers for a single author name using collaboration similarity.
        """
        n = len(papers)
        if n == 0:
            return []
        
        if n == 1:
            return [AuthorCluster(
                original_name=author_name,
                cluster_id=0,
                papers={papers[0]["paper_id"]},
            )]
        
        similarity_matrix = self._build_similarity_matrix(papers)
        
        G = nx.Graph()
        for i in range(n):
            G.add_node(i)
        
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    G.add_edge(i, j)
        
        components = list(nx.connected_components(G))
        
        clusters = []
        for cluster_id, component in enumerate(components):
            cluster = AuthorCluster(
                original_name=author_name,
                cluster_id=cluster_id,
            )
            
            for idx in component:
                paper = papers[idx]
                cluster.papers.add(paper["paper_id"])
                cluster.collaborators.update(paper["coauthors"])
                if paper["category"]:
                    cluster.categories[paper["category"]] = cluster.categories.get(paper["category"], 0) + 1
                if paper["year"]:
                    cluster.years.append(paper["year"])
            
            clusters.append(cluster)
        
        return clusters
    
    def _build_similarity_matrix(self, papers: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Build similarity matrix between papers based on shared collaborators.
        
        Similarity = Jaccard index of collaborator sets
        """
        n = len(papers)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            matrix[i][i] = 1.0
            coauthors_i = set(papers[i]["coauthors"])
            
            for j in range(i + 1, n):
                coauthors_j = set(papers[j]["coauthors"])
                
                if not coauthors_i and not coauthors_j:
                    sim = self._compute_temporal_similarity(papers[i], papers[j])
                elif not coauthors_i or not coauthors_j:
                    sim = 0.0
                else:
                    intersection = len(coauthors_i & coauthors_j)
                    union = len(coauthors_i | coauthors_j)
                    sim = intersection / union if union > 0 else 0.0
                
                matrix[i][j] = sim
                matrix[j][i] = sim
        
        return matrix
    
    def _compute_temporal_similarity(self, paper1: Dict[str, Any], paper2: Dict[str, Any]) -> float:
        """
        Compute similarity based on temporal proximity and category overlap.
        Used when papers have no collaborators.
        """
        year1, year2 = paper1.get("year"), paper2.get("year")
        cat1, cat2 = paper1.get("category"), paper2.get("category")
        
        score = 0.0
        
        if year1 and year2:
            year_diff = abs(year1 - year2)
            if year_diff <= 2:
                score += 0.5
            elif year_diff <= 5:
                score += 0.3
            elif year_diff <= 10:
                score += 0.1
        
        if cat1 and cat2 and cat1 == cat2:
            score += 0.3
        
        return min(score, 1.0)
    
    def _extract_year(self, date_str: Optional[str]) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        try:
            return int(date_str[:4])
        except (ValueError, TypeError):
            return None
    
    def get_disambiguation_stats(self) -> Dict[str, Any]:
        """Get statistics about the disambiguation process"""
        return {
            **self.stats,
            "unique_names": len(self.name_to_papers),
            "unique_clusters": len(self.disambiguated_authors),
            "avg_papers_per_cluster": (
                self.stats["papers_processed"] / self.stats["total_clusters"]
                if self.stats["total_clusters"] > 0 else 0
            ),
        }
    
    def get_cluster_for_paper_author(self, paper_id: str, author_name: str) -> Optional[AuthorCluster]:
        """Get the author cluster for a specific paper-author combination"""
        for cluster in self.disambiguated_authors.values():
            if paper_id in cluster.papers and cluster.original_name == author_name:
                return cluster
        return None


class CollaborationNetworkBuilder:
    """Author collaboration network builder with optional disambiguation"""
    
    def __init__(self, use_disambiguation: bool = True, similarity_threshold: float = 0.1):
        self.authors: Dict[str, AuthorStats] = {}
        self.edges: Dict[Tuple[str, str], int] = defaultdict(int)
        self.author_papers: Dict[str, Set[str]] = defaultdict(set)
        self.use_disambiguation = use_disambiguation
        self.disambiguator = AuthorDisambiguator(similarity_threshold=similarity_threshold) if use_disambiguation else None
        self.disambiguation_mapping: Dict[str, str] = {}
        self.disambiguation_stats: Dict[str, Any] = {}
    
    def build_from_paper_reader(
        self,
        paper_reader: PaperReader,
        min_papers: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> CollaborationGraph:
        """Build author collaboration network from PaperReader"""
        total_papers = paper_reader.get_total_count()
        processed = 0
        
        logger.info(f"Building collaboration network, total {total_papers} papers...")
        logger.info(f"Disambiguation: {'enabled' if self.use_disambiguation else 'disabled'}")
        
        all_papers = []
        for batch in paper_reader.iter_papers_batch(batch_size=10000):
            all_papers.extend(batch)
            processed += len(batch)
            
            if progress_callback:
                progress_callback(processed, total_papers)
        
        logger.info(f"Collected {len(all_papers)} papers")
        
        if self.use_disambiguation and self.disambiguator:
            logger.info("Running author disambiguation...")
            for paper in all_papers:
                self.disambiguator.add_paper(paper)
            
            self.disambiguation_mapping = self.disambiguator.disambiguate_all()
            self.disambiguation_stats = self.disambiguator.get_disambiguation_stats()
            logger.info(f"Disambiguation stats: {self.disambiguation_stats}")
        
        for paper in all_papers:
            self._process_paper(paper)
        
        logger.info(f"Paper processing complete, {len(self.authors)} authors, {len(self.edges)} collaborations")
        
        if min_papers > 1:
            self._filter_low_activity(min_papers)
        
        self._calculate_collaborator_counts()
        
        return CollaborationGraph(
            authors=self.authors,
            edges=dict(self.edges),
            author_papers=dict(self.author_papers),
        )
    
    def _process_paper(self, paper: Dict[str, Any]):
        """Process a single paper"""
        authors = paper.get("authors", [])
        if not authors:
            return
        
        paper_id = paper.get("id", "")
        year = self._extract_year(paper.get("published"))
        category = paper.get("primary_category")
        
        author_ids = []
        for author_name in authors:
            if self.use_disambiguation and self.disambiguation_mapping:
                key = f"{paper_id}:{author_name}"
                author_id = self.disambiguation_mapping.get(key, author_name.lower().replace(" ", "_"))
            else:
                author_id = author_name.lower().replace(" ", "_")
            
            author_ids.append(author_id)
            
            if author_id not in self.authors:
                self.authors[author_id] = AuthorStats(display_name=author_name)
            
            stats = self.authors[author_id]
            stats.paper_count += 1
            self.author_papers[author_id].add(paper_id)
            
            if year:
                if stats.first_paper_year is None or year < stats.first_paper_year:
                    stats.first_paper_year = year
                if stats.latest_paper_year is None or year > stats.latest_paper_year:
                    stats.latest_paper_year = year
            
            if category:
                stats.categories[category] = stats.categories.get(category, 0) + 1
        
        author_ids = list(dict.fromkeys(author_ids))
        
        for i in range(len(author_ids)):
            for j in range(i + 1, len(author_ids)):
                a1, a2 = author_ids[i], author_ids[j]
                key = tuple(sorted([a1, a2]))
                self.edges[key] += 1
    
    def _extract_year(self, date_str: Optional[str]) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        try:
            return int(date_str[:4])
        except (ValueError, TypeError):
            return None
    
    def _filter_low_activity(self, min_papers: int):
        """Filter low-activity authors"""
        keep_authors = {
            aid for aid, stats in self.authors.items()
            if stats.paper_count >= min_papers
        }
        
        self.authors = {
            aid: stats for aid, stats in self.authors.items()
            if aid in keep_authors
        }
        
        self.edges = {
            (a1, a2): count for (a1, a2), count in self.edges.items()
            if a1 in keep_authors and a2 in keep_authors
        }
        
        self.author_papers = {
            aid: papers for aid, papers in self.author_papers.items()
            if aid in keep_authors
        }
        
        logger.info(f"After filtering: {len(self.authors)} authors, {len(self.edges)} collaborations")
    
    def _calculate_collaborator_counts(self):
        """Calculate collaborator count for each author"""
        for (a1, a2), _ in self.edges.items():
            if a1 in self.authors:
                self.authors[a1].collaborator_count += 1
            if a2 in self.authors:
                self.authors[a2].collaborator_count += 1


def run_pagerank_analysis(
    min_papers: int = 3,
    alpha: float = 0.85,
    use_disambiguation: bool = True,
    similarity_threshold: float = 0.1,
    algorithm: str = "networkx",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> AuthorAnalysisResult:
    """Run complete PageRank analysis with optional author disambiguation
    
    Args:
        min_papers: Minimum paper count threshold
        alpha: PageRank damping factor
        use_disambiguation: Enable author name disambiguation
        similarity_threshold: Jaccard similarity threshold for clustering
        algorithm: PageRank algorithm to use ("networkx" or "igraph")
        progress_callback: Callback function for progress updates
    """
    
    logger.info("=" * 60)
    logger.info("Step 1: Initialize paper reader")
    logger.info("=" * 60)
    paper_reader = get_paper_reader()
    total_papers = paper_reader.get_total_count()
    logger.info(f"Total papers: {total_papers}")
    
    if total_papers == 0:
        return AuthorAnalysisResult(
            total_papers=0,
            total_authors=0,
            total_edges=0,
            top_authors=[],
            status="error",
            message="No paper data found",
        )
    
    logger.info("\n" + "=" * 60)
    logger.info("Step 2: Build collaboration network (with disambiguation)")
    logger.info("=" * 60)
    builder = CollaborationNetworkBuilder(
        use_disambiguation=use_disambiguation,
        similarity_threshold=similarity_threshold,
    )
    graph = builder.build_from_paper_reader(
        paper_reader,
        min_papers=min_papers,
        progress_callback=progress_callback,
    )
    logger.info(f"Authors: {len(graph.authors)}")
    logger.info(f"Collaborations: {len(graph.edges)}")
    
    if builder.disambiguation_stats:
        logger.info(f"Disambiguation: {builder.disambiguation_stats.get('names_disambiguated', 0)} names split into multiple authors")
    
    if len(graph.authors) == 0:
        return AuthorAnalysisResult(
            total_papers=total_papers,
            total_authors=0,
            total_edges=0,
            top_authors=[],
            status="error",
            message="No matching authors found",
        )
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Step 3: Calculate PageRank and network metrics (algorithm: {algorithm})")
    logger.info("=" * 60)
    calculator = get_pagerank_calculator(graph, algorithm=algorithm)
    metrics = calculator.calculate_all_metrics(alpha=alpha)
    
    logger.info("\n" + "=" * 60)
    logger.info("Step 4: Generate rankings")
    logger.info("=" * 60)
    top_authors = calculator.get_top_authors(metrics['pagerank'], top_n=100)
    
    print("\n" + "=" * 60)
    print("Top 10 Most Influential Authors (PageRank)")
    print("=" * 60)
    for author in top_authors[:10]:
        print(f"{author['rank']:2d}. {author['name']:30s} | "
              f"PageRank: {author['pagerank']:.6f} | "
              f"Papers: {author['paper_count']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Step 5: Save results to database")
    logger.info("=" * 60)
    rank_repo = get_author_rank_repository()
    rank_repo.save_rankings(graph.authors, metrics)
    
    if builder.disambiguation_stats:
        rank_repo.save_disambiguation_stats(builder.disambiguation_stats)
    
    return AuthorAnalysisResult(
        total_papers=total_papers,
        total_authors=len(graph.authors),
        total_edges=len(graph.edges),
        top_authors=top_authors,
        status="success",
        message="Analysis complete",
    )


class AuthorRankService:
    """Service for author ranking operations"""
    
    def __init__(self):
        self._repo = None
    
    def _get_repo(self):
        if self._repo is None:
            self._repo = get_author_rank_repository()
        return self._repo
    
    def get_top_authors(
        self,
        metric: str = "pagerank",
        category: Optional[str] = None,
        name_search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get top-ranked authors with pagination and optional name search"""
        repo = self._get_repo()
        authors = repo.get_top_authors(
            metric=metric,
            limit=limit,
            offset=offset,
            category=category,
            name_search=name_search,
        )
        total = repo.count_authors(category=category, name_search=name_search)
        
        return {
            "authors": authors,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    
    def get_author_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author by ID"""
        repo = self._get_repo()
        return repo.get_author_by_id(author_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        paper_reader = get_paper_reader()
        repo = self._get_repo()
        
        return {
            "total_papers": paper_reader.get_total_count(),
            "total_analyzed_authors": repo.count_authors(),
        }
    
    def clear_all(self) -> None:
        """Clear all analysis data"""
        repo = self._get_repo()
        repo.clear_all()
    
    def get_disambiguation_stats(self) -> Dict[str, Any]:
        """Get disambiguation statistics"""
        repo = self._get_repo()
        return repo.get_disambiguation_stats()


_author_rank_service = None


def get_author_rank_service() -> AuthorRankService:
    """Get author rank service singleton"""
    global _author_rank_service
    if _author_rank_service is None:
        _author_rank_service = AuthorRankService()
    return _author_rank_service
