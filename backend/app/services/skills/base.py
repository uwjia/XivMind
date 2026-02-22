from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class SkillProvider(ABC):
    """Abstract base class for Skills."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique skill identifier."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for UI."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Skill description."""
        pass
    
    @property
    def icon(self) -> str:
        """Icon name for UI."""
        return "default"
    
    @property
    def category(self) -> str:
        """Skill category (analysis, writing, search, etc.)."""
        return "general"
    
    @property
    def requires_paper(self) -> bool:
        """Whether skill requires paper context."""
        return True
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        """JSON Schema for input validation."""
        return None
    
    @property
    def output_schema(self) -> Optional[Dict[str, Any]]:
        """JSON Schema for output validation."""
        return None
    
    @abstractmethod
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the skill."""
        pass
    
    def is_available(self) -> bool:
        """Check if skill is available."""
        return True
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for this skill."""
        return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "requires_paper": self.requires_paper,
            "available": self.is_available(),
            "input_schema": self.input_schema,
        }
