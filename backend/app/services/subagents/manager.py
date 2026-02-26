import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.config import get_settings

from .base import SubAgentBase
from .types import SubAgentTask, SubAgentResult, SubAgentConfig
from .registry import SubAgentRegistry
from .loader import SubAgentLoader
from .executor import SubAgentExecutor

logger = logging.getLogger(__name__)


def register_default_agents():
    """Register built-in SubAgents as fallback configurations.
    
    These will be overridden by dynamic agents loaded from AGENT.md files.
    """
    from .implementations import get_default_agent_configs, BuiltinSubAgent
    
    default_configs = get_default_agent_configs()
    for agent_id, config_data in default_configs.items():
        try:
            config = SubAgentConfig(**config_data)
            agent = BuiltinSubAgent(config)
            SubAgentRegistry.register_instance(agent)
            logger.info(f"Registered built-in SubAgent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to register built-in SubAgent {agent_id}: {e}")


def load_dynamic_agents():
    settings = get_settings()
    if settings.SUBAGENTS_RELOAD_ON_START:
        loaded = SubAgentRegistry.load_dynamic_agents(settings.SUBAGENTS_DIR)
        logger.info(f"Loaded {loaded} dynamic SubAgents")


def start_agent_watcher():
    from .watcher import SubAgentWatcher
    
    settings = get_settings()
    if not settings.SUBAGENTS_WATCH_ENABLED:
        return
    
    def on_agent_change(agent_dir: str, change_type: str):
        logger.info(f"SubAgent {change_type}: {agent_dir}")
        if change_type == "deleted":
            agent_id = Path(agent_dir).name
            SubAgentRegistry.unregister(agent_id)
        else:
            agent_id = Path(agent_dir).name
            SubAgentRegistry.reload_agent(agent_id)
    
    watcher = SubAgentWatcher(
        agents_dir=settings.SUBAGENTS_DIR,
        on_change=on_agent_change,
        debounce_ms=settings.SUBAGENTS_WATCH_DEBOUNCE_MS
    )
    
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(watcher.start())
        logger.info("SubAgent watcher started")
    except RuntimeError:
        logger.warning("No event loop available for SubAgent watcher")


class SubAgentManager:
    """High-level manager for SubAgent operations."""
    
    def __init__(self):
        self._executor = SubAgentExecutor()
        self._loader: Optional[SubAgentLoader] = None
        self._initialized = False
    
    def _ensure_initialized(self):
        if self._initialized:
            return
        
        settings = get_settings()
        self._loader = SubAgentLoader(settings.SUBAGENTS_DIR)
        self._initialized = True
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        return [agent.to_dict() for agent in SubAgentRegistry.get_available()]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()
        agent = SubAgentRegistry.get(agent_id)
        return agent.to_dict() if agent else None
    
    def get_agent_raw(self, agent_id: str) -> Optional[str]:
        self._ensure_initialized()
        if self._loader:
            return self._loader.get_agent_raw(agent_id)
        return None
    
    def create_agent(
        self,
        agent_id: str,
        name: str,
        description: str = "",
        skills: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        system_prompt: str = "",
    ) -> Dict[str, Any]:
        self._ensure_initialized()
        
        if SubAgentRegistry.exists(agent_id):
            return {
                "success": False,
                "error": f"SubAgent with ID '{agent_id}' already exists"
            }
        
        if self._loader:
            success = self._loader.create_agent_from_template(
                agent_id=agent_id,
                name=name,
                description=description,
                skills=skills,
                tools=tools,
                system_prompt=system_prompt,
            )
            
            if success:
                SubAgentRegistry.reload_agent(agent_id)
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": "SubAgent created successfully"
                }
        
        return {
            "success": False,
            "error": "Failed to create SubAgent"
        }
    
    def save_agent(self, agent_id: str, content: str) -> Dict[str, Any]:
        self._ensure_initialized()
        
        if self._loader:
            saved = self._loader.save_agent_raw(agent_id, content)
            if saved:
                SubAgentRegistry.reload_agent(agent_id)
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": "SubAgent saved and reloaded"
                }
        
        return {
            "success": False,
            "error": "Failed to save SubAgent"
        }
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        self._ensure_initialized()
        
        if not SubAgentRegistry.exists(agent_id):
            return {
                "success": False,
                "error": f"SubAgent '{agent_id}' not found"
            }
        
        if self._loader:
            deleted = self._loader.delete_agent(agent_id)
            if deleted:
                SubAgentRegistry.unregister(agent_id)
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": "SubAgent deleted"
                }
        
        return {
            "success": False,
            "error": "Failed to delete SubAgent"
        }
    
    def reload_agents(self) -> Dict[str, Any]:
        self._ensure_initialized()
        result = SubAgentRegistry.reload_dynamic_agents()
        result["success"] = True
        return result
    
    def reload_agent(self, agent_id: str) -> Dict[str, Any]:
        self._ensure_initialized()
        success = SubAgentRegistry.reload_agent(agent_id)
        return {
            "success": success,
            "agent_id": agent_id,
            "message": "SubAgent reloaded" if success else "SubAgent not found or reload failed"
        }
    
    async def execute_agent(
        self,
        agent_id: str,
        instruction: str,
        paper_ids: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_turns: Optional[int] = None,
    ) -> SubAgentResult:
        self._ensure_initialized()
        
        agent = SubAgentRegistry.get(agent_id)
        if not agent:
            return SubAgentResult(
                task_id="",
                agent_id=agent_id,
                status="failed",
                error=f"SubAgent '{agent_id}' not found"
            )
        
        if not agent.is_available():
            return SubAgentResult(
                task_id="",
                agent_id=agent_id,
                status="failed",
                error=f"SubAgent '{agent_id}' is not available"
            )
        
        papers = []
        if paper_ids:
            from app.services.paper_service import PaperService
            paper_service = PaperService()
            papers = paper_service.get_papers_by_ids(paper_ids)
            logging.info(f"[SubAgent Manager] Loading papers for IDs: {paper_ids}, Found: {len(papers)} papers")
            if papers:
                for p in papers[:3]:
                    logging.info(f"[SubAgent Manager] Paper: {p.get('id')} - {p.get('title', 'N/A')[:50]}...")
        
        task = SubAgentTask(
            agent_id=agent_id,
            instruction=instruction,
            context={
                **(context or {}),
                "papers": papers,
            },
            paper_ids=paper_ids,
            provider=provider,
            model=model,
            max_turns=max_turns,
        )
        
        return await self._executor.execute(agent, task)
    
    async def delegate_task(
        self,
        agent_id: str,
        task: str,
        papers: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> SubAgentResult:
        self._ensure_initialized()
        
        context = kwargs.pop("context", {})
        if papers:
            context["papers"] = papers
        
        paper_ids = [p.get("id") for p in papers if p.get("id")] if papers else None
        
        return await self.execute_agent(
            agent_id=agent_id,
            instruction=task,
            paper_ids=paper_ids,
            context=context,
            **kwargs
        )
    
    def get_agents_by_skill(self, skill_id: str) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        agents = SubAgentRegistry.get_by_skill(skill_id)
        return [agent.to_dict() for agent in agents]
    
    def get_agents_by_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        agents = SubAgentRegistry.get_by_tool(tool_name)
        return [agent.to_dict() for agent in agents]


subagent_manager = SubAgentManager()
