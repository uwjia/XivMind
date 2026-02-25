import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from app.db.factory import get_paper_repository, get_paper_embedding_repository
from app.services.embedding_service import embedding_service
from app.models import (
    GraphNode, GraphEdge, GraphStatistics, KnowledgeGraphData,
    CategoryCount, ClusterInfo, SimilarityPair
)

logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "cs.AI": "#FF6B6B",
    "cs.CL": "#4ECDC4",
    "cs.CV": "#45B7D1",
    "cs.LG": "#96CEB4",
    "cs.NE": "#FFEAA7",
    "cs.RO": "#DDA0DD",
    "cs.CR": "#98D8C8",
    "cs.DB": "#F7DC6F",
    "cs.DC": "#BB8FCE",
    "cs.IR": "#85C1E9",
    "cs.SE": "#F8B500",
    "cs.HC": "#FF8C00",
    "cs.MA": "#00CED1",
    "cs.SY": "#9370DB",
    "cs.GT": "#20B2AA",
    "cs.DS": "#FF69B4",
    "cs.CG": "#7B68EE",
    "cs.CY": "#48D1CC",
    "cs.ET": "#C71585",
    "cs.FL": "#00FA9A",
    "math": "#9B59B6",
    "physics": "#3498DB",
    "stat": "#E74C3C",
    "q-bio": "#2ECC71",
    "q-fin": "#F39C12",
    "eess": "#1ABC9C",
    "econ": "#E91E63",
    "other": "#95A5A6"
}


def get_category_color(category: str) -> str:
    if category in CATEGORY_COLORS:
        return CATEGORY_COLORS[category]
    
    main_category = category.split(".")[0] if "." in category else category
    if main_category in CATEGORY_COLORS:
        return CATEGORY_COLORS[main_category]
    
    return CATEGORY_COLORS["other"]


def truncate_label(text: str, max_length: int = 25) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


class GraphService:
    def __init__(self):
        self.paper_repo = get_paper_repository()
        self.embedding_repo = get_paper_embedding_repository()

    def _normalize_date(self, date_str: str) -> str:
        import re
        date_str = date_str.strip()
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        if re.match(r'^\d{8}', date_str):
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        raise ValueError(f"Unsupported date format: {date_str}")

    async def get_papers_for_graph(
        self,
        date: str,
        category: Optional[str] = None,
        max_papers: int = 200
    ) -> List[Dict[str, Any]]:
        normalized_date = self._normalize_date(date)
        
        result = self.paper_repo.query_papers_by_date(
            date=normalized_date,
            category=category,
            start=0,
            max_results=max_papers
        )
        
        papers = result[0] if isinstance(result, tuple) else result
        return papers

    async def get_or_generate_embeddings(
        self,
        papers: List[Dict[str, Any]],
        date: Optional[str] = None
    ) -> Dict[str, List[float]]:
        embeddings = {}
        papers_need_embedding = []
        
        for paper in papers:
            paper_id = paper["id"]
            embedding_data = self.embedding_repo.get_embedding(paper_id)
            
            if embedding_data:
                embeddings[paper_id] = embedding_data["embedding"]
            else:
                papers_need_embedding.append(paper)
        
        if papers_need_embedding:
            logger.info(f"Generating embeddings for {len(papers_need_embedding)} papers")
            
            texts = [
                f"Title: {p.get('title', '')}\nAbstract: {p.get('abstract', '')}"
                for p in papers_need_embedding
            ]
            
            batch_embeddings, batch_model_name = embedding_service.encode_batch(texts)
            
            embeddings_data = [
                {
                    "paper_id": papers_need_embedding[j]["id"],
                    "embedding": batch_embeddings[j],
                    "model_name": batch_model_name,
                }
                for j in range(len(papers_need_embedding))
            ]
            
            logger.info(f"inserting embeddings for {len(papers_need_embedding)} papers")
            inserted = self.embedding_repo.upsert_embeddings_batch(embeddings_data)
            logger.info(f"embeddings inserted: {inserted}， date: {date}")
            
            if inserted > 0 and date:
                self.paper_repo.insert_embedding_index(
                    date=date,
                    total_count=inserted,
                    model_name=batch_model_name
                )
            
            for paper, embedding in zip(papers_need_embedding, batch_embeddings):
                paper_id = paper["id"]
                embeddings[paper_id] = embedding
                
        
        return embeddings

    def calculate_similarity_matrix(
        self,
        embeddings: Dict[str, List[float]],
        threshold: float = 0.5
    ) -> List[SimilarityPair]:
        import numpy as np
        
        paper_ids = list(embeddings.keys())
        n = len(paper_ids)
        
        if n < 2:
            return []
        
        embedding_matrix = np.array([embeddings[pid] for pid in paper_ids])
        
        norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
        normalized = embedding_matrix / (norms + 1e-10)
        
        similarity_matrix = np.dot(normalized, normalized.T)
        
        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                score = float(similarity_matrix[i, j])
                if score >= threshold:
                    similarities.append(SimilarityPair(
                        paper1_id=paper_ids[i],
                        paper2_id=paper_ids[j],
                        score=score
                    ))
        
        return similarities

    def build_graph(
        self,
        papers: List[Dict[str, Any]],
        similarities: List[SimilarityPair],
        date: str
    ) -> KnowledgeGraphData:
        paper_map = {p["id"]: p for p in papers}
        
        nodes = []
        for paper in papers:
            paper_id = paper["id"]
            category = paper.get("primary_category", "other") or "other"
            
            node = GraphNode(
                id=paper_id,
                label=truncate_label(paper.get("title", "")),
                title=paper.get("title", ""),
                group=category,
                value=max(1, paper.get("citations", 1) or 1),
                color=get_category_color(category),
                paper={
                    "id": paper_id,
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "authors": paper.get("authors", []),
                    "primaryCategory": category,
                    "categories": paper.get("categories", []),
                    "published": str(paper.get("published", "")),
                    "pdfUrl": paper.get("pdf_url", ""),
                    "absUrl": paper.get("abs_url", ""),
                }
            )
            nodes.append(node)
        
        edges = []
        for i, sim in enumerate(similarities):
            edge = GraphEdge(
                id=f"edge-{i}",
                from_id=sim.paper1_id,
                to_id=sim.paper2_id,
                value=sim.score,
                title=f"Similarity: {(sim.score * 100):.1f}%"
            )
            edges.append(edge)
        
        category_counts = Counter(p.get("primary_category", "other") or "other" for p in papers)
        top_categories = [
            CategoryCount(
                category_id=cat,
                category_name=cat,
                count=count
            )
            for cat, count in category_counts.most_common(10)
        ]
        
        avg_similarity = 0.0
        if similarities:
            avg_similarity = sum(s.score for s in similarities) / len(similarities)
        
        statistics = GraphStatistics(
            total_papers=len(papers),
            total_connections=len(similarities),
            top_categories=top_categories,
            avg_similarity=avg_similarity,
            clusters=[]
        )
        
        return KnowledgeGraphData(
            nodes=nodes,
            edges=edges,
            date=date,
            statistics=statistics
        )

    async def get_graph_data(
        self,
        date: str,
        threshold: float = 0.5,
        category: Optional[str] = None,
        max_papers: int = 200
    ) -> KnowledgeGraphData:
        normalized_date = self._normalize_date(date)
        
        papers = await self.get_papers_for_graph(normalized_date, category, max_papers)
        
        if not papers:
            return KnowledgeGraphData(
                nodes=[],
                edges=[],
                date=normalized_date,
                statistics=GraphStatistics(
                    total_papers=0,
                    total_connections=0,
                    top_categories=[],
                    avg_similarity=0.0,
                    clusters=[]
                )
            )
        
        embeddings = await self.get_or_generate_embeddings(papers, normalized_date)
        
        similarities = self.calculate_similarity_matrix(embeddings, threshold)
        
        return self.build_graph(papers, similarities, normalized_date)

    async def get_similarity_matrix(
        self,
        date: str,
        threshold: float = 0.3,
        category: Optional[str] = None,
        max_papers: int = 200
    ) -> Tuple[List[SimilarityPair], int]:
        normalized_date = self._normalize_date(date)
        
        papers = await self.get_papers_for_graph(normalized_date, category, max_papers)
        
        if not papers:
            return [], 0
        
        embeddings = await self.get_or_generate_embeddings(papers, normalized_date)
        
        similarities = self.calculate_similarity_matrix(embeddings, threshold)
        
        return similarities, len(papers)


graph_service = GraphService()
