from pydantic import BaseModel, Field
from typing import Optional, List


class GraphNode(BaseModel):
    id: str
    label: str
    title: str
    group: str
    value: float
    color: Optional[str] = None
    paper: dict


class GraphEdge(BaseModel):
    id: str
    from_id: str = Field(..., serialization_alias="from")
    to_id: str = Field(..., serialization_alias="to")
    value: float
    title: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class CategoryCount(BaseModel):
    category_id: str = Field(..., serialization_alias="categoryId")
    category_name: str = Field(..., serialization_alias="categoryName")
    count: int

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class ClusterInfo(BaseModel):
    id: str
    name: str
    node_count: int = Field(..., serialization_alias="nodeCount")
    category: str

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class GraphStatistics(BaseModel):
    total_papers: int = Field(..., serialization_alias="totalPapers")
    total_connections: int = Field(..., serialization_alias="totalConnections")
    top_categories: List[CategoryCount] = Field(..., serialization_alias="topCategories")
    avg_similarity: float = Field(..., serialization_alias="avgSimilarity")
    clusters: List[ClusterInfo] = []

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class KnowledgeGraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    date: str
    statistics: GraphStatistics


class SimilarityPair(BaseModel):
    paper1_id: str
    paper2_id: str
    score: float


class SimilarityMatrixResponse(BaseModel):
    date: str
    similarities: List[SimilarityPair]
    total_papers: int
    threshold: float
