import logging
from typing import Dict, Any, List, Optional

from .skills.registry import SkillRegistry
from .skills.base import SkillProvider
from .skills.loader import SkillLoader
from .skills.watcher import SkillWatcher
from .paper_service import PaperService
from .skills.implementations import SummarySkill, TranslationSkill, CitationSkill, RelatedPapersSkill
from app.config import get_settings

logger = logging.getLogger(__name__)

skill_registry = SkillRegistry()


def register_default_skills():
    """Register default built-in skills."""
    skill_registry.register(SummarySkill)
    skill_registry.register(TranslationSkill)
    skill_registry.register(CitationSkill)
    skill_registry.register(RelatedPapersSkill)


def load_dynamic_skills():
    """Load dynamic skills from SKILL.md files."""
    settings = get_settings()
    if settings.SKILLS_RELOAD_ON_START:
        loaded = SkillRegistry.load_dynamic_skills(settings.SKILLS_DIR)
        logger.info(f"Loaded {loaded} dynamic skills")


def start_skill_watcher():
    """Start the skill file watcher."""
    settings = get_settings()
    if not settings.SKILLS_WATCH_ENABLED:
        return
    
    def on_skill_change(skill_dir: str, change_type: str):
        logger.info(f"Skill {change_type}: {skill_dir}")
        if change_type == "deleted":
            SkillRegistry.unregister(skill_dir)
        else:
            SkillRegistry.reload_skill(skill_dir)
    
    watcher = SkillWatcher(
        skills_dir=settings.SKILLS_DIR,
        on_change=on_skill_change,
        debounce_ms=settings.SKILLS_WATCH_DEBOUNCE_MS
    )
    
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(watcher.start())
        logger.info("Skill watcher started")
    except RuntimeError:
        logger.warning("No event loop available for skill watcher")


register_default_skills()
load_dynamic_skills()


class SkillService:
    """Service for managing and executing skills."""
    
    def __init__(self):
        self.paper_service = PaperService()
        self._watcher: Optional[SkillWatcher] = None
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Get all available skills."""
        return [skill.to_dict() for skill in SkillRegistry.get_available()]
    
    def get_skills_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get skills grouped by category."""
        categories = SkillRegistry.get_categories()
        return {
            category: [s.to_dict() for s in SkillRegistry.get_by_category(category)]
            for category in categories
        }
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific skill by ID."""
        skill = SkillRegistry.get(skill_id)
        return skill.to_dict() if skill else None
    
    def get_skill_raw(self, skill_id: str) -> Optional[str]:
        """Get raw SKILL.md content for a skill."""
        settings = get_settings()
        loader = SkillLoader(settings.SKILLS_DIR)
        return loader.get_skill_raw(skill_id)
    
    def reload_skills(self) -> Dict[str, Any]:
        """Reload all dynamic skills."""
        result = SkillRegistry.reload_dynamic_skills()
        result["success"] = True
        return result
    
    def reload_skill(self, skill_id: str) -> Dict[str, Any]:
        """Reload a specific skill."""
        success = SkillRegistry.reload_skill(skill_id)
        return {
            "success": success,
            "skill_id": skill_id,
            "message": "Skill reloaded" if success else "Skill not found or reload failed"
        }
    
    def save_skill(self, skill_id: str, content: str) -> Dict[str, Any]:
        """Save and reload a skill."""
        settings = get_settings()
        loader = SkillLoader(settings.SKILLS_DIR)
        
        saved = loader.save_skill_raw(skill_id, content)
        if not saved:
            return {
                "success": False,
                "skill_id": skill_id,
                "message": "Failed to save skill content"
            }
        
        success = SkillRegistry.reload_skill(skill_id)
        return {
            "success": success,
            "skill_id": skill_id,
            "message": "Skill saved and reloaded" if success else "Skill saved but reload failed"
        }
    
    async def execute_skill(
        self,
        skill_id: str,
        paper_ids: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a skill by ID."""
        skill = SkillRegistry.get(skill_id)
        if not skill:
            return {
                "error": f"Skill not found: {skill_id}",
                "success": False
            }
        
        if not skill.is_available():
            return {
                "error": f"Skill not available: {skill_id}",
                "success": False
            }
        
        context = context or {}
        context["llm_provider"] = provider
        context["llm_model"] = model
        
        if skill.requires_paper and paper_ids:
            try:
                papers = self.paper_service.get_papers_by_ids(paper_ids)
                if not papers:
                    return {
                        "error": "No papers found for the provided IDs",
                        "success": False
                    }
                context["papers"] = papers
            except Exception as e:
                logger.error(f"Failed to get papers: {e}")
                return {
                    "error": f"Failed to get papers: {str(e)}",
                    "success": False
                }
        
        try:
            result = await skill.execute(context, paper_ids, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Failed to execute skill {skill_id}: {e}")
            return {
                "error": f"Failed to execute skill: {str(e)}",
                "success": False
            }


skill_service = SkillService()
