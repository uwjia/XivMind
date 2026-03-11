import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ...types import TaskComplexity

logger = logging.getLogger(__name__)


@dataclass
class DecompositionRule:
    name: str
    description: str
    patterns: List[str]
    task_type: str
    min_complexity: TaskComplexity = TaskComplexity.SIMPLE
    max_subtasks: int = 5
    requires_synthesis: bool = True
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecompositionConfig:
    use_llm: bool = True
    llm_fallback_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    max_subtasks: int = 10
    min_subtasks_for_team: int = 2
    complexity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "simple": 0.0,
        "standard": 0.3,
        "moderate": 0.5,
        "high": 0.7,
    })
    parallelism_threshold: float = 0.4
    rules: List[DecompositionRule] = field(default_factory=list)


DEFAULT_RULES = [
    DecompositionRule(
        name="comparison_decomposition",
        description="Decompose comparison tasks into parallel analysis",
        patterns=["compare", "contrast", "versus", "vs", "比较", "对比"],
        task_type="comparison",
        min_complexity=TaskComplexity.STANDARD,
        max_subtasks=4,
        requires_synthesis=True,
        priority=10,
    ),
    DecompositionRule(
        name="review_decomposition",
        description="Decompose review tasks into aspect-based search",
        patterns=["review", "survey", "overview", "综述", "调研"],
        task_type="review",
        min_complexity=TaskComplexity.MODERATE,
        max_subtasks=5,
        requires_synthesis=True,
        priority=8,
    ),
    DecompositionRule(
        name="analysis_decomposition",
        description="Decompose analysis tasks for multiple papers",
        patterns=["analyze", "analysis", "分析"],
        task_type="analysis",
        min_complexity=TaskComplexity.STANDARD,
        max_subtasks=4,
        requires_synthesis=True,
        priority=6,
    ),
    DecompositionRule(
        name="multi_paper_decomposition",
        description="Decompose tasks involving multiple papers",
        patterns=["papers", "multiple papers", "论文", "多篇"],
        task_type="analysis",
        min_complexity=TaskComplexity.MODERATE,
        max_subtasks=5,
        requires_synthesis=True,
        priority=7,
    ),
]


class DecompositionConfigManager:
    DEFAULT_CONFIG_PATH = "config/decomposition.json"
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        self._config: Optional[DecompositionConfig] = None
        self._last_loaded: Optional[datetime] = None
    
    def get_config(self) -> DecompositionConfig:
        if self._config is None:
            self._load_config()
        return self._config
    
    def _load_config(self) -> None:
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = self._parse_config(data)
                self._last_loaded = datetime.now()
                logger.info(f"[ConfigManager] Loaded config from {self._config_path}")
                return
            except Exception as e:
                logger.warning(f"[ConfigManager] Failed to load config: {e}")
        
        self._config = self._get_default_config()
        self._last_loaded = datetime.now()
        logger.info("[ConfigManager] Using default config")
    
    def _parse_config(self, data: Dict[str, Any]) -> DecompositionConfig:
        rules = []
        for rule_data in data.get("rules", []):
            try:
                min_complexity = TaskComplexity(
                    rule_data.get("min_complexity", "simple")
                )
            except ValueError:
                min_complexity = TaskComplexity.SIMPLE
            
            rule = DecompositionRule(
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                patterns=rule_data.get("patterns", []),
                task_type=rule_data.get("task_type", "analysis"),
                min_complexity=min_complexity,
                max_subtasks=rule_data.get("max_subtasks", 5),
                requires_synthesis=rule_data.get("requires_synthesis", True),
                priority=rule_data.get("priority", 0),
                enabled=rule_data.get("enabled", True),
                metadata=rule_data.get("metadata", {}),
            )
            rules.append(rule)
        
        return DecompositionConfig(
            use_llm=data.get("use_llm", True),
            llm_fallback_enabled=data.get("llm_fallback_enabled", True),
            cache_enabled=data.get("cache_enabled", True),
            cache_ttl_seconds=data.get("cache_ttl_seconds", 3600),
            max_subtasks=data.get("max_subtasks", 10),
            min_subtasks_for_team=data.get("min_subtasks_for_team", 2),
            complexity_thresholds=data.get(
                "complexity_thresholds",
                {"simple": 0.0, "standard": 0.3, "moderate": 0.5, "high": 0.7}
            ),
            parallelism_threshold=data.get("parallelism_threshold", 0.4),
            rules=rules if rules else list(DEFAULT_RULES),
        )
    
    def _get_default_config(self) -> DecompositionConfig:
        return DecompositionConfig(
            use_llm=True,
            llm_fallback_enabled=True,
            cache_enabled=True,
            cache_ttl_seconds=3600,
            max_subtasks=10,
            min_subtasks_for_team=2,
            complexity_thresholds={
                "simple": 0.0,
                "standard": 0.3,
                "moderate": 0.5,
                "high": 0.7,
            },
            parallelism_threshold=0.4,
            rules=list(DEFAULT_RULES),
        )
    
    def save_config(self, config: Optional[DecompositionConfig] = None) -> bool:
        config = config or self._config
        if config is None:
            return False
        
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "use_llm": config.use_llm,
                "llm_fallback_enabled": config.llm_fallback_enabled,
                "cache_enabled": config.cache_enabled,
                "cache_ttl_seconds": config.cache_ttl_seconds,
                "max_subtasks": config.max_subtasks,
                "min_subtasks_for_team": config.min_subtasks_for_team,
                "complexity_thresholds": config.complexity_thresholds,
                "parallelism_threshold": config.parallelism_threshold,
                "rules": [
                    {
                        "name": rule.name,
                        "description": rule.description,
                        "patterns": rule.patterns,
                        "task_type": rule.task_type,
                        "min_complexity": rule.min_complexity.value,
                        "max_subtasks": rule.max_subtasks,
                        "requires_synthesis": rule.requires_synthesis,
                        "priority": rule.priority,
                        "enabled": rule.enabled,
                        "metadata": rule.metadata,
                    }
                    for rule in config.rules
                ],
            }
            
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._config = config
            self._last_loaded = datetime.now()
            logger.info(f"[ConfigManager] Saved config to {self._config_path}")
            return True
            
        except Exception as e:
            logger.error(f"[ConfigManager] Failed to save config: {e}")
            return False
    
    def reload_config(self) -> None:
        self._config = None
        self._load_config()
    
    def match_rule(self, instruction: str) -> Optional[DecompositionRule]:
        config = self.get_config()
        instruction_lower = instruction.lower()
        
        matched_rules = []
        for rule in config.rules:
            if not rule.enabled:
                continue
            
            for pattern in rule.patterns:
                if pattern.lower() in instruction_lower:
                    matched_rules.append(rule)
                    break
        
        if matched_rules:
            matched_rules.sort(key=lambda r: r.priority, reverse=True)
            return matched_rules[0]
        
        return None
    
    def get_complexity_from_score(self, score: float) -> TaskComplexity:
        config = self.get_config()
        thresholds = config.complexity_thresholds
        
        if score >= thresholds.get("high", 0.7):
            return TaskComplexity.HIGH
        elif score >= thresholds.get("moderate", 0.5):
            return TaskComplexity.MODERATE
        elif score >= thresholds.get("standard", 0.3):
            return TaskComplexity.STANDARD
        else:
            return TaskComplexity.SIMPLE
    
    def update_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
        config = self.get_config()
        
        for rule in config.rules:
            if rule.name == rule_name:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        if key == "min_complexity" and isinstance(value, str):
                            try:
                                value = TaskComplexity(value)
                            except ValueError:
                                continue
                        setattr(rule, key, value)
                return True
        
        return False
    
    def add_rule(self, rule: DecompositionRule) -> None:
        config = self.get_config()
        config.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        config = self.get_config()
        
        for i, rule in enumerate(config.rules):
            if rule.name == rule_name:
                config.rules.pop(i)
                return True
        
        return False


config_manager = DecompositionConfigManager()
