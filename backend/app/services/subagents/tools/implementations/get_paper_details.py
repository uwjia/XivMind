import logging
from typing import Dict, Any, List

from ..base import ToolProvider
from ..types import ToolCategory, ToolParameter
from ...types import SubAgentExecutionContext

logger = logging.getLogger(__name__)


class GetPaperDetailsTool(ToolProvider):
    """Tool for getting paper details by ID."""
    
    @property
    def id(self) -> str:
        return "get_paper_details"
    
    @property
    def name(self) -> str:
        return "Get Paper Details"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific paper by ID"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ANALYSIS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="paper_id",
                type="string",
                description="Paper ID to retrieve",
                required=True,
            ),
        ]
    
    async def execute(
        self,
        args: Dict[str, Any],
        context: SubAgentExecutionContext
    ) -> str:
        paper_id = args.get("paper_id")
        
        if not paper_id:
            return "Error: Missing required argument 'paper_id'"
        
        from app.services.paper_service import PaperService
        
        paper_service = PaperService()
        paper = paper_service.get_paper_by_id(paper_id)
        
        if not paper:
            return f"Paper not found: {paper_id}"
        
        return f"""Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Categories: {', '.join(paper.get('categories', []))}
Published: {paper.get('published', 'N/A')}
"""
