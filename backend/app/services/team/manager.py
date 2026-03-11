import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime

from app.config import get_settings

from .types import (
    TaskComplexity,
    TeamTask,
    TeamTaskStatus,
    TeamSession,
    TeamResult,
    TeamExecuteRequest,
    DecompositionResult,
)
from .memory import TeamMemory
from .decomposer import TaskDecomposer
from .lead_agent import LeadAgent
from .synthesizer import ResultSynthesizer
from .parallel_executor import ParallelExecutor
from .orchestrator import TeamOrchestrator

logger = logging.getLogger(__name__)


class TeamManager:
    """High-level manager for team-based multi-agent operations."""
    
    def __init__(
        self,
        storage_dir: Optional[str] = None,
    ):
        settings = get_settings()
        
        self._storage_dir = storage_dir or str(
            Path(settings.SQLITE_DB_PATH).parent / "team_sessions"
        )
        
        self._memory = TeamMemory(storage_dir=self._storage_dir)
        self._decomposer = TaskDecomposer()
        self._lead_agent = LeadAgent(decomposer=self._decomposer)
        self._synthesizer = ResultSynthesizer()
        self._executor = ParallelExecutor()
        self._orchestrator = TeamOrchestrator(
            memory=self._memory,
            decomposer=self._decomposer,
            lead_agent=self._lead_agent,
            synthesizer=self._synthesizer,
            executor=self._executor,
        )
        
        self._subagent_manager = None
        self._initialized = False
    
    def initialize(self) -> None:
        if self._initialized:
            return
        
        try:
            from app.services.subagents import subagent_manager
            self._subagent_manager = subagent_manager
            
            self._orchestrator.set_agent_executor(self._execute_subagent)
            
            self._initialized = True
            logger.info("[TeamManager] Initialized with SubAgentManager")
        except ImportError:
            logger.warning("[TeamManager] SubAgentManager not available, using mock executor")
            self._orchestrator.set_agent_executor(self._mock_executor)
            self._initialized = True
    
    async def _execute_subagent(
        self,
        agent_id: str,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
    ) -> Any:
        if not self._subagent_manager:
            return await self._mock_executor(agent_id, instruction, context, paper_ids)
        
        logger.info(f"[TeamManager] Executing SubAgent: {agent_id}")
        
        result = await self._subagent_manager.execute_agent(
            agent_id=agent_id,
            instruction=instruction,
            paper_ids=paper_ids,
            context=context,
        )
        
        return result
    
    async def _mock_executor(
        self,
        agent_id: str,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
    ) -> Any:
        from .types import SubTaskResult, SubTaskStatus
        
        logger.warning(f"[TeamManager] Using mock executor for {agent_id}")
        
        return SubTaskResult(
            subtask_id="mock",
            agent_id=agent_id,
            status=SubTaskStatus.COMPLETED,
            result=f"[Mock Result from {agent_id}]\n\nExecuted instruction: {instruction[:200]}...",
        )
    
    def analyze_task(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DecompositionResult:
        self._ensure_initialized()
        return self._lead_agent.analyze_task(instruction, context)
    
    async def analyze_task_async(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        self._ensure_initialized()
        return await self._lead_agent.analyze_task_async(
            instruction, context, provider, model
        )
    
    async def execute(
        self,
        request: TeamExecuteRequest,
    ) -> TeamResult:
        self._ensure_initialized()
        
        available_agents = []
        if self._subagent_manager:
            agents = self._subagent_manager.get_all_agents()
            available_agents = [a.get("id") for a in agents if a.get("available", True)]
        
        if not available_agents:
            available_agents = ["research-agent", "analysis-agent", "writer-agent"]
        
        session = await self._orchestrator.create_session(
            instruction=request.instruction,
            context=request.context,
            paper_ids=request.paper_ids,
            provider=request.provider,
            model=request.model,
            available_agents=available_agents,
        )
        
        if request.force_team_mode and session.task:
            session.task.complexity = TaskComplexity.MODERATE
        
        result = await self._orchestrator.run_session(session)
        
        return result
    
    async def execute_instruction(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        force_team_mode: bool = False,
    ) -> TeamResult:
        request = TeamExecuteRequest(
            instruction=instruction,
            context=context,
            paper_ids=paper_ids,
            provider=provider,
            model=model,
            force_team_mode=force_team_mode,
        )
        return await self.execute(request)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()
        session = self._orchestrator.get_session(session_id)
        return session.to_dict() if session else None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()
        return self._orchestrator.get_session_summary(session_id)
    
    def list_sessions(self) -> List[str]:
        self._ensure_initialized()
        return self._orchestrator.list_sessions()
    
    async def cancel_session(self, session_id: str) -> bool:
        self._ensure_initialized()
        return await self._orchestrator.cancel_session(session_id)
    
    def add_progress_callback(self, callback: Callable) -> None:
        self._orchestrator.add_progress_callback(callback)
    
    def remove_progress_callback(self, callback: Callable) -> None:
        self._orchestrator.remove_progress_callback(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "storage_dir": self._storage_dir,
            "orchestrator_stats": self._orchestrator.get_stats(),
        }
    
    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        
        if self._subagent_manager:
            return self._subagent_manager.get_all_agents()
        
        return [
            {"id": "research-agent", "name": "Research Agent", "available": True},
            {"id": "analysis-agent", "name": "Analysis Agent", "available": True},
            {"id": "writer-agent", "name": "Writer Agent", "available": True},
        ]


team_manager = TeamManager()
