from abc import ABC, abstractmethod
from typing import List
import pyarrow as pa


class BaseTableSchema(ABC):
    """Abstract base class for LanceDB table schemas."""
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the table description."""
        pass
    
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Return the embedding dimension."""
        pass
    
    @property
    def primary_key(self) -> str | None:
        """Return the primary key field name. Override in subclass if needed."""
        return None
    
    @abstractmethod
    def get_fields(self) -> List[pa.Field]:
        """Return the list of PyArrow fields."""
        pass
    
    def get_pyarrow_schema(self) -> pa.Schema:
        """Build and return the PyArrow Schema."""
        return pa.schema(self.get_fields())
