import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import SkillProvider

logger = logging.getLogger(__name__)


class DynamicSkill(SkillProvider):
    """A skill dynamically loaded from SKILL.md file."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._id = config.get("id", "unknown")
        self._name = config.get("name", "Unknown Skill")
        self._description = config.get("description", "")
        self._icon = config.get("icon", "default")
        self._category = config.get("category", "general")
        self._requires_paper = config.get("requires_paper", True)
        self._input_schema = config.get("input_schema")
        self._template = config.get("template", "")
        self._file_path = config.get("file_path", "")
        self._loaded_at = config.get("loaded_at", datetime.now().isoformat())
        self._source = config.get("source", "dynamic")
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def icon(self) -> str:
        return self._icon
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def requires_paper(self) -> bool:
        return self._requires_paper
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return self._input_schema
    
    @property
    def file_path(self) -> str:
        return self._file_path
    
    @property
    def loaded_at(self) -> str:
        return self._loaded_at
    
    @property
    def source(self) -> str:
        return self._source
    
    def is_available(self) -> bool:
        return True
    
    def get_prompt_template(self) -> str:
        return self._template
    
    def render_template(self, context: Dict[str, Any], **kwargs) -> str:
        """Render the prompt template with context and parameters."""
        template = self._template
        if not template:
            return ""
        
        paper = context.get("papers", [{}])[0] if context.get("papers") else {}
        
        render_context = {
            "paper": {
                "id": paper.get("id", ""),
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "authors": ", ".join(paper.get("authors", [])),
                "categories": ", ".join(paper.get("categories", [])),
                "published": paper.get("published", ""),
                "abs_url": paper.get("abs_url", ""),
                "pdf_url": paper.get("pdf_url", ""),
            },
            **kwargs
        }
        
        template = self._render_conditionals(template, render_context)
        
        for key, value in render_context.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    placeholder = f"{{{key}.{sub_key}}}"
                    template = template.replace(placeholder, str(sub_value or ""))
            else:
                placeholder = f"{{{key}}}"
                template = template.replace(placeholder, str(value or ""))
        
        return template
    
    def _render_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Render conditional blocks in template."""
        conditional_pattern = re.compile(
            r'\{if\s+(\w+)\s*==\s*"([^"]+)"\}(.*?)\{elif\s+\w+\s*==\s*"([^"]+)"\}(.*?)\{else\}(.*?)\{endif\}',
            re.DOTALL
        )
        
        def replace_conditional(match):
            var_name = match.group(1)
            if_value = match.group(2)
            if_content = match.group(3)
            elif_value = match.group(4)
            elif_content = match.group(5)
            else_content = match.group(6)
            
            actual_value = context.get(var_name, "")
            
            if actual_value == if_value:
                return if_content
            elif actual_value == elif_value:
                return elif_content
            else:
                return else_content
        
        template = conditional_pattern.sub(replace_conditional, template)
        
        simple_if_pattern = re.compile(
            r'\{if\s+(\w+)\}(.*?)\{else\}(.*?)\{endif\}',
            re.DOTALL
        )
        
        def replace_simple_if(match):
            var_name = match.group(1)
            if_content = match.group(2)
            else_content = match.group(3)
            
            actual_value = context.get(var_name)
            if actual_value:
                return if_content
            else:
                return else_content
        
        template = simple_if_pattern.sub(replace_simple_if, template)
        
        return template
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the skill by rendering template and calling LLM."""
        from app.services.llm_service import llm_service
        
        papers = context.get("papers", [])
        if not papers and self._requires_paper:
            return {"error": "No papers provided", "success": False}
        
        provider = context.get("llm_provider")
        model = context.get("llm_model")
        
        prompt = self.render_template(context, **kwargs)
        
        if not prompt:
            return {"error": "Failed to render prompt template", "success": False}
        
        try:
            result = await llm_service.generate(prompt, provider=provider, model=model)
            
            response = {
                "success": True,
                "skill_id": self._id,
                "skill_name": self._name,
                "result": result
            }
            
            if papers:
                response["paper_id"] = papers[0].get("id")
                response["paper_title"] = papers[0].get("title")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute skill {self._id}: {e}")
            return {"error": str(e), "success": False}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary for API response."""
        base_dict = super().to_dict()
        base_dict.update({
            "source": self._source,
            "file_path": self._file_path,
            "loaded_at": self._loaded_at
        })
        return base_dict
