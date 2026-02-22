from typing import Dict, Any, List, Optional
from ..base import SkillProvider


class SummarySkill(SkillProvider):
    """Generate paper summary."""
    
    @property
    def id(self) -> str:
        return "summary"
    
    @property
    def name(self) -> str:
        return "Paper Summary"
    
    @property
    def description(self) -> str:
        return "Generate a concise summary including research question, methodology, key findings, and conclusions"
    
    @property
    def icon(self) -> str:
        return "file-text"
    
    @property
    def category(self) -> str:
        return "analysis"
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["brief", "detailed"],
                    "default": "brief",
                    "description": "Level of detail for the summary"
                }
            }
        }
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        detail_level: str = "brief",
        **kwargs
    ) -> Dict[str, Any]:
        from app.services.llm_service import llm_service
        
        papers = context.get("papers", [])
        if not papers:
            return {"error": "No papers provided", "success": False}
        
        paper = papers[0]
        
        provider = context.get("llm_provider")
        model = context.get("llm_model")
        
        if detail_level == "detailed":
            prompt = f"""Please provide a detailed summary of the following paper:

Title: {paper.get('title', '')}
Abstract: {paper.get('abstract', '')}

Please include:
1. Research Question/Objective
2. Background and Motivation
3. Methodology/Approach
4. Key Findings and Results
5. Contributions and Significance
6. Limitations
7. Conclusions and Future Work

Format the response in clear sections with markdown headings."""
        else:
            prompt = f"""Please provide a brief summary of the following paper:

Title: {paper.get('title', '')}
Abstract: {paper.get('abstract', '')}

Please include:
1. Research Question
2. Methodology
3. Key Findings
4. Conclusions

Keep the summary concise and to the point."""
        
        result = await llm_service.generate(prompt, provider=provider, model=model)
        
        return {
            "paper_id": paper.get("id"),
            "paper_title": paper.get("title", ""),
            "summary": result,
            "detail_level": detail_level,
            "success": True
        }
