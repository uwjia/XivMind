import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillLoader:
    """Parse SKILL.md files and create skill instances."""
    
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
    
    def __init__(self, skills_dir: str = "./skills"):
        self.skills_dir = Path(skills_dir)
    
    def parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from SKILL.md content."""
        import yaml
        
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            logger.warning("No frontmatter found in SKILL.md")
            return None
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            return {
                "frontmatter": frontmatter,
                "body": body
            }
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse frontmatter: {e}")
            return None
    
    def parse_skill_md(self, skill_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a SKILL.md file and return skill configuration."""
        if not skill_path.exists():
            logger.warning(f"SKILL.md not found: {skill_path}")
            return None
        
        try:
            content = skill_path.read_text(encoding="utf-8")
            parsed = self.parse_frontmatter(content)
            if not parsed:
                return None
            
            frontmatter = parsed["frontmatter"]
            body = parsed["body"]
            
            if "name" not in frontmatter:
                logger.error(f"SKILL.md missing required 'name' field: {skill_path}")
                return None
            
            if "description" not in frontmatter:
                logger.error(f"SKILL.md missing required 'description' field: {skill_path}")
                return None
            
            metadata = frontmatter.get("metadata", {})
            xivmind_meta = metadata.get("xivmind", {}) if isinstance(metadata, dict) else {}
            
            return {
                "id": frontmatter["name"],
                "name": frontmatter.get("name", "").replace("-", " ").title(),
                "description": frontmatter.get("description", ""),
                "icon": frontmatter.get("icon", "default"),
                "category": frontmatter.get("category", "general"),
                "requires_paper": frontmatter.get("requires_paper", True),
                "input_schema": xivmind_meta.get("input_schema"),
                "template": self._extract_template(body),
                "body": body,
                "file_path": str(skill_path),
                "loaded_at": datetime.now().isoformat(),
                "source": "dynamic"
            }
        except Exception as e:
            logger.error(f"Failed to parse SKILL.md {skill_path}: {e}")
            return None
    
    def _extract_template(self, body: str) -> str:
        """Extract prompt template from body."""
        template_pattern = re.compile(r'```prompt\s*\n(.*?)\n```', re.DOTALL)
        match = template_pattern.search(body)
        if match:
            return match.group(1).strip()
        return body
    
    def load_skill(self, skill_dir: Path) -> Optional[Dict[str, Any]]:
        """Load a single skill directory."""
        skill_path = skill_dir / "SKILL.md"
        return self.parse_skill_md(skill_path)
    
    def load_all_skills(self) -> List[Dict[str, Any]]:
        """Load all skills from the skills directory."""
        skills = []
        
        if not self.skills_dir.exists():
            logger.info(f"Skills directory does not exist: {self.skills_dir}")
            return skills
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_config = self.load_skill(skill_dir)
                if skill_config:
                    skills.append(skill_config)
                    logger.info(f"Loaded skill: {skill_config['id']}")
        
        return skills
    
    def get_skill_raw(self, skill_id: str) -> Optional[str]:
        """Get raw SKILL.md content for a skill."""
        skill_dir = self.skills_dir / skill_id
        skill_path = skill_dir / "SKILL.md"
        
        if skill_path.exists():
            return skill_path.read_text(encoding="utf-8")
        return None


skill_loader = SkillLoader()
