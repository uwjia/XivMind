import logging
from typing import Dict, Any, List

from ..base import ToolProvider
from ..types import ToolCategory, ToolParameter
from ...types import SubAgentExecutionContext

logger = logging.getLogger(__name__)


class SearchPapersTool(ToolProvider):
    """Tool for searching papers using semantic search."""
    
    @property
    def id(self) -> str:
        return "search_papers"
    
    @property
    def name(self) -> str:
        return "Search Papers"
    
    @property
    def description(self) -> str:
        return "Search for papers using semantic search"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SEARCH
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Search keywords or phrases",
                required=True,
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                default=10,
            ),
        ]
    
    async def execute(
        self,
        args: Dict[str, Any],
        context: SubAgentExecutionContext
    ) -> str:
        query = args.get("query", "")
        top_k = args.get("top_k", 10)
        
        if not query:
            return "Error: Missing required argument 'query'"
        
        from app.services.paper_service import PaperService
        
        paper_service = PaperService()
        result = await paper_service.search_papers_semantic(query, top_k=top_k)
        
        papers = result.get("papers", [])
        if not papers:
            return "No papers found matching the query."
        
        context.papers = papers
        
        result_parts = [f"Found {len(papers)} papers:\n"]
        for i, paper in enumerate(papers[:5], 1):
            result_parts.append(f"{i}. {paper.get('title', 'Unknown')} (ID: {paper.get('id', 'N/A')})")
        
        return "\n".join(result_parts)
