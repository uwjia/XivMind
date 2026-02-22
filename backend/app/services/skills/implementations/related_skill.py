from typing import Dict, Any, List, Optional
from ..base import SkillProvider


class RelatedPapersSkill(SkillProvider):
    """Find related papers."""
    
    @property
    def id(self) -> str:
        return "related"
    
    @property
    def name(self) -> str:
        return "Related Papers"
    
    @property
    def description(self) -> str:
        return "Find papers related to the selected paper using semantic search"
    
    @property
    def icon(self) -> str:
        return "link"
    
    @property
    def category(self) -> str:
        return "search"
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "top_k": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                    "description": "Number of related papers to return"
                }
            }
        }
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        top_k: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        from app.services.paper_service import PaperService
        
        papers = context.get("papers", [])
        if not papers:
            return {"error": "No papers provided", "success": False}
        
        paper = papers[0]
        paper_service = PaperService()
        
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        query_text = f"{title} {abstract}"
        
        try:
            result = await paper_service.search_papers_semantic(
                query=query_text,
                top_k=top_k + 1,
            )
            
            related = [
                p for p in result.get("papers", [])
                if p.get("id") != paper.get("id")
            ][:top_k]
            
            return {
                "paper_id": paper.get("id"),
                "paper_title": title,
                "related_papers": related,
                "total": len(related),
                "success": True
            }
        except Exception as e:
            return {
                "paper_id": paper.get("id"),
                "error": str(e),
                "success": False
            }
