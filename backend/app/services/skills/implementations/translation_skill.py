from typing import Dict, Any, List, Optional
from ..base import SkillProvider


class TranslationSkill(SkillProvider):
    """Translate paper content."""
    
    @property
    def id(self) -> str:
        return "translation"
    
    @property
    def name(self) -> str:
        return "Paper Translation"
    
    @property
    def description(self) -> str:
        return "Translate paper title and abstract to a specified language"
    
    @property
    def icon(self) -> str:
        return "languages"
    
    @property
    def category(self) -> str:
        return "writing"
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "target_language": {
                    "type": "string",
                    "enum": ["Chinese", "English", "Japanese", "Korean", "German", "French", "Spanish"],
                    "default": "Chinese",
                    "description": "Target language for translation"
                }
            },
            "required": ["target_language"]
        }
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        target_language: str = "Chinese",
        **kwargs
    ) -> Dict[str, Any]:
        from app.services.llm_service import llm_service
        
        papers = context.get("papers", [])
        if not papers:
            return {"error": "No papers provided", "success": False}
        
        paper = papers[0]
        
        provider = context.get("llm_provider")
        model = context.get("llm_model")
        
        language_prompts = {
            "Chinese": "中文",
            "English": "English",
            "Japanese": "日本語",
            "Korean": "한국어",
            "German": "Deutsch",
            "French": "Français",
            "Spanish": "Español"
        }
        
        target_lang_name = language_prompts.get(target_language, target_language)
        
        prompt = f"""Please translate the following paper content to {target_lang_name}:

Title: {paper.get('title', '')}

Abstract: {paper.get('abstract', '')}

Requirements:
1. Maintain academic writing style
2. Ensure accurate translation of technical terms
3. Preserve the original meaning and structure
4. Format the output clearly with "Title:" and "Abstract:" sections

Please provide the translation:"""
        
        result = await llm_service.generate(prompt, provider=provider, model=model)
        
        return {
            "paper_id": paper.get("id"),
            "paper_title": paper.get("title", ""),
            "target_language": target_language,
            "translation": result,
            "success": True
        }
