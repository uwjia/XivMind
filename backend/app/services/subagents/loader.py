import os
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

import yaml

from .types import SubAgentConfig, AGENT_FILE_NAME

logger = logging.getLogger(__name__)


class SubAgentLoader:
    """Loader for SubAgent configurations from AGENT.md files."""
    
    def __init__(self, agents_dir: str):
        self.agents_dir = Path(agents_dir)
    
    def load_all_agents(self) -> List[Dict[str, Any]]:
        if not self.agents_dir.exists():
            logger.warning(f"Agents directory does not exist: {self.agents_dir}")
            return []
        
        configs = []
        
        for item in self.agents_dir.iterdir():
            if item.is_dir():
                config = self.load_agent(item)
                if config:
                    configs.append(config)
        
        return configs
    
    def load_agent(self, agent_dir: Path) -> Optional[Dict[str, Any]]:
        agent_file = agent_dir / AGENT_FILE_NAME
        
        if not agent_file.exists():
            logger.debug(f"No {AGENT_FILE_NAME} found in {agent_dir}")
            return None
        
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            config = self._parse_agent_file(content, str(agent_dir))
            return config
        except Exception as e:
            logger.error(f"Failed to load agent from {agent_dir}: {e}")
            return None
    
    def _parse_agent_file(self, content: str, agent_dir: str) -> Optional[Dict[str, Any]]:
        frontmatter, system_prompt = self._extract_frontmatter(content)
        
        if not frontmatter:
            logger.warning(f"No frontmatter found in {agent_dir}")
            return None
        
        try:
            config_data = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML frontmatter in {agent_dir}: {e}")
            return None
        
        if not config_data.get("id"):
            dir_name = Path(agent_dir).name
            config_data["id"] = dir_name
        
        config_data["system_prompt"] = system_prompt
        config_data["file_path"] = str(agent_dir)
        config_data["loaded_at"] = datetime.now().isoformat()
        config_data["source"] = "dynamic"
        
        config_data.setdefault("name", config_data.get("id", "Unknown Agent"))
        config_data.setdefault("description", "")
        config_data.setdefault("icon", "bot")
        config_data.setdefault("skills", [])
        config_data.setdefault("tools", [])
        config_data.setdefault("max_turns", 10)
        config_data.setdefault("temperature", 0.7)
        
        if "language" not in config_data:
            config_data["language"] = self._detect_language(config_data.get("system_prompt", ""))
        
        return config_data
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is primarily Chinese or English."""
        if not text:
            return "en"
        
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "en"
        
        chinese_ratio = chinese_chars / total_chars
        
        return "zh" if chinese_ratio > 0.3 else "en"
    
    def _extract_frontmatter(self, content: str) -> tuple[Optional[str], str]:
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            frontmatter = match.group(1)
            body = match.group(2).strip()
            return frontmatter, body
        
        return None, content.strip()
    
    def get_agent_raw(self, agent_id: str) -> Optional[str]:
        agent_dir = self.agents_dir / agent_id
        agent_file = agent_dir / AGENT_FILE_NAME
        
        if not agent_file.exists():
            return None
        
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read agent file {agent_file}: {e}")
            return None
    
    def save_agent_raw(self, agent_id: str, content: str) -> bool:
        agent_dir = self.agents_dir / agent_id
        agent_file = agent_dir / AGENT_FILE_NAME
        
        try:
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            with open(agent_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save agent file {agent_file}: {e}")
            return False
    
    def create_agent_from_template(
        self,
        agent_id: str,
        name: str,
        description: str = "",
        skills: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        system_prompt: str = "",
    ) -> bool:
        template = f"""---
id: {agent_id}
name: {name}
description: {description}
icon: bot
skills:
{self._format_list(skills or [])}
tools:
{self._format_list(tools or [])}
max_turns: 10
temperature: 0.7
---

{system_prompt or f"# {name}\\n\\nWrite your system prompt here..."}
"""
        return self.save_agent_raw(agent_id, template)
    
    def _format_list(self, items: List[str]) -> str:
        if not items:
            return "  []"
        return "\n".join(f"  - {item}" for item in items)
    
    def delete_agent(self, agent_id: str) -> bool:
        agent_dir = self.agents_dir / agent_id
        
        if not agent_dir.exists():
            return False
        
        try:
            import shutil
            shutil.rmtree(agent_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to delete agent directory {agent_dir}: {e}")
            return False
    
    def validate_config(self, config_data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not config_data.get("id"):
            errors.append("Missing required field: id")
        
        if not config_data.get("name"):
            errors.append("Missing required field: name")
        
        skills = config_data.get("skills", [])
        if not isinstance(skills, list):
            errors.append("Field 'skills' must be a list")
        
        tools = config_data.get("tools", [])
        if not isinstance(tools, list):
            errors.append("Field 'tools' must be a list")
        
        max_turns = config_data.get("max_turns", 10)
        if not isinstance(max_turns, int) or max_turns < 1:
            errors.append("Field 'max_turns' must be a positive integer")
        
        temperature = config_data.get("temperature", 0.7)
        if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
            errors.append("Field 'temperature' must be a number between 0 and 2")
        
        return errors
