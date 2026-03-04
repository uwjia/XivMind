import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.memory.types import (
    CoreMemory,
    RecallMemory,
    MemoryExtractionResult,
    ShouldSaveResult,
    MemoryCategory,
)
from app.services.memory.prompts import MEMORY_EXTRACTION_PROMPT, SHOULD_SAVE_PROMPT
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Extracts memory information from conversations."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()

    async def should_save(
        self,
        content: str,
    ) -> ShouldSaveResult:
        try:
            prompt = SHOULD_SAVE_PROMPT.format(content=content)
            
            response = await self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            
            content_str = response.get("content", "")
            
            json_start = content_str.find("{")
            json_end = content_str.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content_str[json_start:json_end]
                data = json.loads(json_str)
                
                category_str = data.get("category", "context")
                try:
                    category = MemoryCategory(category_str)
                except ValueError:
                    category = MemoryCategory.CONTEXT
                
                return ShouldSaveResult(
                    should_save=data.get("should_save", False),
                    importance_score=data.get("importance_score", 0.5),
                    category=category,
                    reason=data.get("reason", ""),
                )
            
            return ShouldSaveResult(should_save=False)
            
        except Exception as e:
            logger.error(f"Failed to determine if should save: {e}")
            return ShouldSaveResult(should_save=False)
    
    async def extract_from_conversation(
        self,
        user_message: str,
        assistant_message: str,
        current_core_memory: Optional[CoreMemory] = None,
    ) -> MemoryExtractionResult:
        try:
            current_profile = ""
            if current_core_memory:
                current_profile = current_core_memory.to_context_string()
            else:
                current_profile = "no user profile available"
            
            prompt = MEMORY_EXTRACTION_PROMPT.format(
                current_profile=current_profile,
                user_message=user_message,
                assistant_message=assistant_message,
            )
            
            response = await self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            
            content = response.get("content", "")
            
            try:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    data = json.loads(json_str)
                    
                    return MemoryExtractionResult(
                        user_preferences=data.get("user_preferences", []),
                        research_interests=data.get("research_interests", []),
                        important_facts=data.get("important_facts", []),
                        should_update_core=data.get("should_update_core", False),
                        importance_score=data.get("importance_score", 0.5),
                    )
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse memory extraction result: {content}")
            
            return MemoryExtractionResult()
        except Exception as e:
            logger.error(f"Failed to extract memory from conversation: {e}")
            return MemoryExtractionResult()
    
    def create_recall_memory(
        self,
        user_id: str,
        session_id: str,
        content: str,
        embedding: Optional[List[float]] = None,
        importance_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecallMemory:
        return RecallMemory(
            user_id=user_id,
            session_id=session_id,
            content=content,
            embedding=embedding,
            importance_score=importance_score,
            metadata=metadata or {},
            timestamp=datetime.utcnow(),
        )
    
    def update_core_memory(
        self,
        current_memory: CoreMemory,
        extraction_result: MemoryExtractionResult,
    ) -> CoreMemory:
        updated = current_memory.model_copy()
        
        for interest in extraction_result.research_interests:
            if interest and interest not in updated.research_interests:
                updated.research_interests.append(interest)
        
        for pref in extraction_result.user_preferences:
            pref_lower = pref.lower()
            
            if "中文" in pref_lower or "chinese" in pref_lower:
                updated.language_preference = "zh-CN"
            elif "英文" in pref_lower or "english" in pref_lower:
                updated.language_preference = "en-US"
            
            if "详细" in pref_lower or "detailed" in pref_lower:
                updated.summary_style = "detailed"
            elif "简洁" in pref_lower or "brief" in pref_lower or "简短" in pref_lower:
                updated.summary_style = "brief"
            elif "要点" in pref_lower or "bullet" in pref_lower:
                updated.summary_style = "bullet_points"
        
        for fact in extraction_result.important_facts:
            if fact and fact not in updated.custom_instructions:
                if updated.custom_instructions:
                    updated.custom_instructions += f"\n{fact}"
                else:
                    updated.custom_instructions = fact
        
        updated.updated_at = datetime.utcnow()
        return updated
    
    def calculate_importance_score(
        self,
        content: str,
        has_user_preference: bool = False,
        has_research_interest: bool = False,
        has_important_fact: bool = False,
    ) -> float:
        base_score = 0.3
        
        if has_user_preference:
            base_score += 0.2
        if has_research_interest:
            base_score += 0.2
        if has_important_fact:
            base_score += 0.2
        
        keywords = [
            "记住", "记得", "保存", "重要", "关键", "发现",
            "remember", "important", "key", "significant",
        ]
        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                base_score += 0.05
        
        return min(base_score, 1.0)
