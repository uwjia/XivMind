from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from .types import ToolDefinition, ToolResult, ToolCategory, ToolParameter


class ToolProvider(ABC):
    """Abstract base class for tool providers."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the tool."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for the tool."""
        pass
    
    @property
    def description(self) -> str:
        """Description of what the tool does."""
        return ""
    
    @property
    def category(self) -> ToolCategory:
        """Category of the tool."""
        return ToolCategory.SYSTEM
    
    @property
    def parameters(self) -> List[ToolParameter]:
        """List of parameters the tool accepts."""
        return []
    
    @property
    def returns(self) -> str:
        """Description of return value."""
        return "string"
    
    @property
    def examples(self) -> List[str]:
        """Example usage of the tool."""
        return []
    
    def get_definition(self) -> ToolDefinition:
        """Get the tool definition."""
        return ToolDefinition(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category,
            parameters=self.parameters,
            returns=self.returns,
            examples=self.examples,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": [p.model_dump() for p in self.parameters],
            "returns": self.returns,
            "examples": self.examples,
        }
    
    @abstractmethod
    async def execute(
        self,
        args: Dict[str, Any],
        context: Any,
    ) -> ToolResult:
        """Execute the tool with given arguments and context."""
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> List[str]:
        """Validate arguments against parameter definitions."""
        errors = []
        
        for param in self.parameters:
            if param.required and param.name not in args:
                errors.append(f"Missing required parameter: {param.name}")
            elif param.enum and args.get(param.name) not in param.enum:
                errors.append(
                    f"Invalid value for {param.name}. Must be one of: {param.enum}"
                )
        
        return errors
