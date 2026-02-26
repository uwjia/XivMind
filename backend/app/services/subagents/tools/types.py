from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum


class ToolCategory(str, Enum):
    SEARCH = "search"
    ANALYSIS = "analysis"
    WRITING = "writing"
    SYSTEM = "system"


class ToolParameter(BaseModel):
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class ToolDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: ToolCategory = ToolCategory.SYSTEM
    parameters: List[ToolParameter] = []
    returns: str = "string"
    examples: List[str] = []


class ToolResult(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    papers: List[Dict[str, Any]] = []
    
    def to_string(self) -> str:
        if not self.success:
            return f"Error: {self.error}"
        if self.data is None:
            return "Success"
        return str(self.data)
