import logging
from typing import Dict, List, Optional, Type
from pathlib import Path
from .base import SkillProvider
from .dynamic_skill import DynamicSkill
from .loader import SkillLoader

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for all available skills."""
    
    _instance = None
    _skills: Dict[str, SkillProvider] = {}
    _dynamic_skills: Dict[str, DynamicSkill] = {}
    _initialized = False
    _skills_dir: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, skill_class: Type[SkillProvider]) -> Type[SkillProvider]:
        """Register a skill class. Can be used as decorator."""
        skill = skill_class()
        cls._skills[skill.id] = skill
        return skill_class
    
    @classmethod
    def register_dynamic(cls, skill_config: Dict) -> Optional[DynamicSkill]:
        """Register a dynamic skill from configuration."""
        skill = DynamicSkill(skill_config)
        cls._skills[skill.id] = skill
        cls._dynamic_skills[skill.id] = skill
        logger.info(f"Registered dynamic skill: {skill.id}")
        return skill
    
    @classmethod
    def unregister(cls, skill_id: str) -> bool:
        """Unregister a skill by ID."""
        if skill_id in cls._skills:
            del cls._skills[skill_id]
            if skill_id in cls._dynamic_skills:
                del cls._dynamic_skills[skill_id]
            logger.info(f"Unregistered skill: {skill_id}")
            return True
        return False
    
    @classmethod
    def get(cls, skill_id: str) -> Optional[SkillProvider]:
        """Get a skill by ID."""
        return cls._skills.get(skill_id)
    
    @classmethod
    def get_all(cls) -> List[SkillProvider]:
        """Get all registered skills."""
        return list(cls._skills.values())
    
    @classmethod
    def get_by_category(cls, category: str) -> List[SkillProvider]:
        """Get skills by category."""
        return [s for s in cls._skills.values() if s.category == category]
    
    @classmethod
    def get_available(cls) -> List[SkillProvider]:
        """Get all available skills."""
        return [s for s in cls._skills.values() if s.is_available()]
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique categories."""
        return list(set(s.category for s in cls._skills.values()))
    
    @classmethod
    def get_dynamic_skills(cls) -> List[DynamicSkill]:
        """Get all dynamic skills."""
        return list(cls._dynamic_skills.values())
    
    @classmethod
    def is_dynamic(cls, skill_id: str) -> bool:
        """Check if a skill is dynamic."""
        return skill_id in cls._dynamic_skills
    
    @classmethod
    def load_dynamic_skills(cls, skills_dir: str) -> int:
        """Load all dynamic skills from directory."""
        loader = SkillLoader(skills_dir)
        skill_configs = loader.load_all_skills()
        
        loaded_count = 0
        for config in skill_configs:
            skill = cls.register_dynamic(config)
            if skill:
                loaded_count += 1
        
        cls._skills_dir = Path(skills_dir)
        return loaded_count
    
    @classmethod
    def reload_dynamic_skills(cls) -> Dict[str, int]:
        """Reload all dynamic skills."""
        dynamic_ids = list(cls._dynamic_skills.keys())
        for skill_id in dynamic_ids:
            cls.unregister(skill_id)
        
        loaded = 0
        if cls._skills_dir:
            loaded = cls.load_dynamic_skills(str(cls._skills_dir))
        
        return {
            "unloaded": len(dynamic_ids),
            "loaded": loaded
        }
    
    @classmethod
    def reload_skill(cls, skill_id: str) -> bool:
        """Reload a specific skill."""
        if cls._skills_dir:
            skill_dir = cls._skills_dir / skill_id
            if skill_dir.exists():
                loader = SkillLoader(str(cls._skills_dir))
                config = loader.load_skill(skill_dir)
                if config:
                    cls.unregister(skill_id)
                    cls.register_dynamic(config)
                    return True
        return False
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered skills."""
        cls._skills.clear()
        cls._dynamic_skills.clear()
        cls._initialized = False
