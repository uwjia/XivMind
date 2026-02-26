import logging
from typing import Dict, Any, List

from ..base import ToolProvider
from ..types import ToolCategory, ToolParameter
from ...types import SubAgentExecutionContext

logger = logging.getLogger(__name__)


class ExecuteSkillTool(ToolProvider):
    """Tool for executing skills on papers."""
    
    @property
    def id(self) -> str:
        return "execute_skill"
    
    @property
    def name(self) -> str:
        return "Execute Skill"
    
    @property
    def description(self) -> str:
        return "Execute a skill on the provided paper IDs"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ANALYSIS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="skill_id",
                type="string",
                description="Skill ID to execute",
                required=True,
            ),
            ToolParameter(
                name="paper_ids",
                type="array",
                description="List of paper IDs",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        args: Dict[str, Any],
        context: SubAgentExecutionContext
    ) -> str:
        skill_id = args.get("skill_id")
        paper_ids = args.get("paper_ids", [])
        
        if not skill_id:
            return "Error: Missing required argument 'skill_id'"
        
        from app.services.skill_service import skill_service
        
        if paper_ids:
            paper_ids_list = paper_ids if isinstance(paper_ids, list) else [paper_ids]
        elif context.papers:
            paper_ids_list = [p.get("id") for p in context.papers if p.get("id")]
        else:
            paper_ids_list = []
        
        result = await skill_service.execute_skill(
            skill_id=skill_id,
            paper_ids=paper_ids_list,
            context={"papers": context.papers},
            provider=context.provider,
            model=context.model,
        )
        
        if result.get("success"):
            paper_title = result.get("paper_title", "Unknown Paper")
            
            if "summary" in result:
                return f"Summary of '{paper_title}':\n\n{result['summary']}"
            elif "translation" in result:
                return f"Translation of '{paper_title}':\n\n{result['translation']}"
            elif "citations" in result:
                citations_str = "\n\n".join(
                    f"**{fmt}**:\n{citation}" 
                    for fmt, citation in result["citations"].items()
                )
                return f"Citations for '{paper_title}':\n\n{citations_str}"
            elif "related_papers" in result:
                papers = result["related_papers"]
                papers_str = "\n".join(
                    f"- {p.get('title', 'Unknown')} (ID: {p.get('id', 'N/A')})"
                    for p in papers[:5]
                )
                return f"Related papers for '{paper_title}':\n\n{papers_str}"
            elif "result" in result:
                return result["result"]
            else:
                return str(result)
        else:
            return f"Skill execution failed: {result.get('error', 'Unknown error')}"
