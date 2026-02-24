from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class PaperBase(BaseModel):
    id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None


class Paper(PaperBase):
    pass


class BookmarkCreate(BaseModel):
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    updated: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: str
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    updated: Optional[str] = None
    created_at: datetime
    embedding: Optional[List[float]] = None


class DownloadTaskCreate(BaseModel):
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    pdf_url: str


class DownloadTaskResponse(BaseModel):
    id: str
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    pdf_url: str
    status: DownloadStatus
    progress: int = 0
    file_path: Optional[str] = None
    file_size: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BookmarkListResponse(BaseModel):
    total: int
    items: List[BookmarkResponse]


class DownloadTaskListResponse(BaseModel):
    total: int
    items: List[DownloadTaskResponse]


class SearchResult(BaseModel):
    papers: List[BookmarkResponse]
    query: str
    total: int


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language query for semantic search")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category (e.g., 'cs.LG')")
    date_from: Optional[str] = Field(None, description="Filter papers from this date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter papers to this date (YYYY-MM-DD)")


class SemanticSearchResult(BaseModel):
    id: str
    title: str
    abstract: str
    authors: List[str] = []
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    similarity_score: float = 0.0


class SemanticSearchResponse(BaseModel):
    papers: List[SemanticSearchResult]
    total: int
    query: str
    model: Optional[str] = None
    error: Optional[str] = None


class SimilarPapersResponse(BaseModel):
    papers: List[SemanticSearchResult]
    source_paper_id: str
    error: Optional[str] = None


class GenerateEmbeddingsRequest(BaseModel):
    date: Optional[str] = Field(None, description="Generate embeddings for papers on this date")
    date_from: Optional[str] = Field(None, description="Start date for range")
    date_to: Optional[str] = Field(None, description="End date for range")
    force: bool = Field(False, description="Regenerate embeddings even if they exist")
    batch_size: int = Field(100, ge=10, le=500, description="Batch size for processing")


class GenerateEmbeddingsResponse(BaseModel):
    success: bool
    generated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    error: Optional[str] = None
    model_name: Optional[str] = None


class EmbeddingIndexResponse(BaseModel):
    date: str
    total_count: int
    generated_at: str
    model_name: Optional[str] = None


class EmbeddingIndexesResponse(BaseModel):
    indexes: List[EmbeddingIndexResponse]


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class AskRequest(BaseModel):
    question: str = Field(..., description="Question to ask about papers")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant papers to use as context")
    include_references: bool = Field(True, description="Include paper references in response")
    provider: Optional[str] = Field(None, description="LLM provider to use (openai, anthropic, glm, ollama)")
    model: Optional[str] = Field(None, description="Specific model to use")


class PaperReference(BaseModel):
    id: str
    title: str
    authors: List[str] = []
    published: Optional[str] = None
    relevance_score: float = 0.0


class AskResponse(BaseModel):
    answer: str
    references: List[PaperReference] = []
    model: Optional[str] = None
    error: Optional[str] = None


class LLMProviderInfo(BaseModel):
    id: str
    name: str
    models: List[str]
    available: bool
    description: str


class LLMProvidersResponse(BaseModel):
    providers: List[LLMProviderInfo]
    default_provider: Optional[str] = None


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
