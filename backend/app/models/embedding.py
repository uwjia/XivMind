from pydantic import BaseModel, Field
from typing import Optional, List


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
