from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .types import SubAgentConfig, SubAgentTask, SubAgentResult, SubAgentExecutionContext


class SubAgentBase(ABC):
    """Abstract base class for SubAgents."""
    
    def __init__(self, config: SubAgentConfig):
        self._config = config
        self._context: Optional[SubAgentExecutionContext] = None
    
    @property
    def id(self) -> str:
        return self._config.id
    
    @property
    def name(self) -> str:
        return self._config.name
    
    @property
    def description(self) -> str:
        return self._config.description
    
    @property
    def icon(self) -> str:
        return self._config.icon
    
    @property
    def config(self) -> SubAgentConfig:
        return self._config
    
    @property
    def skills(self) -> List[str]:
        return self._config.skills
    
    @property
    def tools(self) -> List[str]:
        return self._config.tools
    
    @property
    def max_turns(self) -> int:
        return self._config.max_turns
    
    @property
    def temperature(self) -> float:
        return self._config.temperature
    
    @property
    def model(self) -> Optional[str]:
        return self._config.model
    
    @property
    def provider(self) -> Optional[str]:
        return self._config.provider
    
    def get_system_prompt(self) -> str:
        return self._config.system_prompt
    
    def is_available(self) -> bool:
        return True
    
    def has_skill(self, skill_id: str) -> bool:
        return skill_id in self._config.skills
    
    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._config.tools
    
    def create_context(self, task: SubAgentTask) -> SubAgentExecutionContext:
        from .types import SubAgentMessage, SubAgentMessageRole
        import logging
        
        logger = logging.getLogger(__name__)
        
        papers = task.context.get("papers", [])
        logger.info(f"[SubAgent Context] Creating context, Papers in task.context: {len(papers)}")
        
        context = SubAgentExecutionContext(
            agent_id=self.id,
            task_id=task.id,
            max_turns=task.max_turns or self.max_turns,
            papers=papers,
            variables=task.context.get("variables", {}),
        )
        
        system_prompt = self.get_system_prompt()
        if system_prompt:
            context.add_message(SubAgentMessageRole.SYSTEM, system_prompt)
            logger.info(f"[SubAgent Context] Added system prompt, length: {len(system_prompt)}")
        
        if papers:
            paper_context = self._build_paper_context(papers)
            context.add_message(SubAgentMessageRole.SYSTEM, paper_context)
            logger.info(f"[SubAgent Context] Added paper context for {len(papers)} papers, length: {len(paper_context)}")
        else:
            logger.warning(f"[SubAgent Context] No papers found in task context!")
        
        context.add_message(SubAgentMessageRole.USER, task.instruction)
        logger.info(f"[SubAgent Context] Total messages: {len(context.messages)}")
        
        return context
    
    def _build_paper_context(self, papers: List[Dict[str, Any]]) -> str:
        if not papers:
            return ""
        
        language = getattr(self._config, 'language', 'en') or 'en'
        
        if language == 'zh':
            return self._build_paper_context_zh(papers)
        
        return self._build_paper_context_en(papers)
    
    def _build_paper_context_en(self, papers: List[Dict[str, Any]]) -> str:
        context_parts = ["Here is the relevant paper information:\n"]
        
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get("title", "Unknown Title")
            authors = paper.get("authors", [])
            authors_str = ", ".join(authors[:3]) if authors else "Unknown Authors"
            if len(authors) > 3:
                authors_str += " et al."
            
            abstract = paper.get("abstract", "No abstract available")
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            paper_id = paper.get("id", "")
            
            context_parts.append(f"""
Paper {i}:
ID: {paper_id}
Title: {title}
Authors: {authors_str}
Abstract: {abstract}
""")
        
        return "\n".join(context_parts)
    
    def _build_paper_context_zh(self, papers: List[Dict[str, Any]]) -> str:
        context_parts = ["以下是相关的论文信息：\n"]
        
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get("title", "未知标题")
            authors = paper.get("authors", [])
            authors_str = "、".join(authors[:3]) if authors else "未知作者"
            if len(authors) > 3:
                authors_str += " 等"
            
            abstract = paper.get("abstract", "无摘要")
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            paper_id = paper.get("id", "")
            
            context_parts.append(f"""
论文 {i}:
编号: {paper_id}
标题: {title}
作者: {authors_str}
摘要: {abstract}
""")
        
        return "\n".join(context_parts)
    
    @abstractmethod
    async def execute(self, task: SubAgentTask) -> SubAgentResult:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "skills": self.skills,
            "tools": self.tools,
            "max_turns": self.max_turns,
            "temperature": self.temperature,
            "model": self.model,
            "provider": self.provider,
            "available": self.is_available(),
            "source": self._config.source,
            "file_path": self._config.file_path,
            "loaded_at": self._config.loaded_at,
            "language": getattr(self._config, 'language', 'en') or 'en',
        }
