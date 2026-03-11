import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from .types import (
    TaskComplexity,
    TeamTask,
    TeamTaskStatus,
    SubTask,
    SubTaskStatus,
    TeamSession,
    TeamSessionStatus,
    TeamMessage,
    TeamMessageRole,
    TeamResult,
    SubTaskResult,
    DecompositionResult,
    TEAM_SESSION_TIMEOUT,
)
from .memory import TeamMemory
from .decomposer import TaskDecomposer
from .lead_agent import LeadAgent
from .synthesizer import ResultSynthesizer
from .parallel_executor import ParallelExecutor

logger = logging.getLogger(__name__)


class TeamOrchestrator:
    """Orchestrator for managing multi-agent team sessions."""
    
    def __init__(
        self,
        memory: Optional[TeamMemory] = None,
        decomposer: Optional[TaskDecomposer] = None,
        lead_agent: Optional[LeadAgent] = None,
        synthesizer: Optional[ResultSynthesizer] = None,
        executor: Optional[ParallelExecutor] = None,
    ):
        self._memory = memory or TeamMemory()
        self._decomposer = decomposer or TaskDecomposer()
        self._lead_agent = lead_agent or LeadAgent(decomposer=self._decomposer)
        self._synthesizer = synthesizer or ResultSynthesizer()
        self._executor = executor or ParallelExecutor()
        
        self._agent_executor_fn: Optional[Callable] = None
        self._progress_callbacks: List[Callable] = []
    
    def set_agent_executor(self, executor_fn: Callable) -> None:
        self._agent_executor_fn = executor_fn
        logger.info("[TeamOrchestrator] Agent executor function set")
    
    def add_progress_callback(self, callback: Callable) -> None:
        self._progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable) -> None:
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)
    
    async def _notify_progress(self, event: str, data: Dict[str, Any]) -> None:
        for callback in self._progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, data)
                else:
                    callback(event, data)
            except Exception as e:
                logger.warning(f"[TeamOrchestrator] Progress callback error: {e}")
    
    async def create_session(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        available_agents: Optional[List[str]] = None,
    ) -> TeamSession:
        decomposition = self._lead_agent.analyze_task(instruction, context)
        
        task = self._lead_agent.create_team_task(
            instruction=instruction,
            decomposition=decomposition,
            context=context,
            paper_ids=paper_ids,
            provider=provider,
            model=model,
        )
        
        if not available_agents:
            available_agents = ["research-agent", "analysis-agent", "writer-agent"]
        
        session = self._memory.create_session(task, available_agents)
        
        session.add_message(
            role=TeamMessageRole.USER,
            content=instruction,
        )
        
        await self._notify_progress("session_created", {
            "session_id": session.id,
            "task_id": task.id,
            "complexity": decomposition.complexity.value,
            "use_team_mode": decomposition.use_team_mode,
        })
        
        logger.info(f"[TeamOrchestrator] Created session {session.id} for task {task.id}")
        return session
    
    async def run_session(
        self,
        session: TeamSession,
    ) -> TeamResult:
        if not session.task:
            return TeamResult(
                task_id="",
                session_id=session.id,
                status=TeamTaskStatus.FAILED,
                error="No task associated with session",
            )
        
        session.status = TeamSessionStatus.ACTIVE
        session.started_at = datetime.now()
        session.task.status = TeamTaskStatus.ANALYZING
        
        started_at = datetime.now()
        
        try:
            use_single_agent = (
                session.task.complexity == TaskComplexity.SIMPLE
                or len(session.task.subtasks) == 0
            )
            
            if use_single_agent:
                result = await self._run_single_agent(session)
            else:
                result = await self._run_team_mode(session)
            
            session.status = TeamSessionStatus.COMPLETED
            session.completed_at = datetime.now()
            session.task.status = TeamTaskStatus.COMPLETED
            session.task.completed_at = datetime.now()
            
            self._memory.save_session(session.id)
            
            await self._notify_progress("session_completed", {
                "session_id": session.id,
                "status": "completed",
            })
            
            return result
            
        except asyncio.CancelledError:
            session.status = TeamSessionStatus.CANCELLED
            session.task.status = TeamTaskStatus.CANCELLED
            logger.info(f"[TeamOrchestrator] Session {session.id} cancelled")
            
            return TeamResult(
                task_id=session.task.id,
                session_id=session.id,
                status=TeamTaskStatus.CANCELLED,
                error="Session was cancelled",
                started_at=started_at,
                completed_at=datetime.now(),
            )
            
        except Exception as e:
            session.status = TeamSessionStatus.FAILED
            session.task.status = TeamTaskStatus.FAILED
            logger.error(f"[TeamOrchestrator] Session {session.id} failed: {e}")
            
            return TeamResult(
                task_id=session.task.id,
                session_id=session.id,
                status=TeamTaskStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(),
            )
    
    async def _run_single_agent(
        self,
        session: TeamSession,
    ) -> TeamResult:
        task = session.task
        task.status = TeamTaskStatus.EXECUTING
        
        session.add_message(
            role=TeamMessageRole.SYSTEM,
            content="Task complexity is simple. Using single agent mode.",
        )
        
        await self._notify_progress("task_status", {
            "session_id": session.id,
            "status": "executing",
            "mode": "single_agent",
        })
        
        agent_id = self._select_agent_for_task(task.instruction, session.available_agents)
        
        if not self._agent_executor_fn:
            raise RuntimeError("Agent executor function not set")
        
        subtask_result = await self._executor.execute_single_agent(
            agent_id=agent_id,
            instruction=task.instruction,
            agent_executor_fn=self._agent_executor_fn,
            context=task.context,
            paper_ids=task.paper_ids,
        )
        
        self._memory.store_subtask_result(session.id, subtask_result)
        
        task.status = TeamTaskStatus.SYNTHESIZING
        
        output = subtask_result.result or ""
        if subtask_result.error:
            output = f"Error: {subtask_result.error}"
        
        session.add_message(
            role=TeamMessageRole.SUBAGENT,
            content=output,
            agent_id=agent_id,
            subtask_id=subtask_result.subtask_id,
        )
        
        return TeamResult(
            task_id=task.id,
            session_id=session.id,
            status=TeamTaskStatus.COMPLETED if subtask_result.status == SubTaskStatus.COMPLETED else TeamTaskStatus.FAILED,
            output=output,
            subtask_results=[subtask_result],
            messages=session.messages,
            error=subtask_result.error,
            complexity=task.complexity,
            total_subtasks=1,
            completed_subtasks=1 if subtask_result.status == SubTaskStatus.COMPLETED else 0,
            failed_subtasks=1 if subtask_result.status == SubTaskStatus.FAILED else 0,
            started_at=session.started_at,
            completed_at=datetime.now(),
        )
    
    async def _run_team_mode(
        self,
        session: TeamSession,
    ) -> TeamResult:
        task = session.task
        task.status = TeamTaskStatus.DISPATCHING
        
        session.add_message(
            role=TeamMessageRole.SYSTEM,
            content=f"Task complexity: {task.complexity.value}. Using team mode with {len(task.subtasks)} subtasks.",
        )
        
        await self._notify_progress("task_status", {
            "session_id": session.id,
            "status": "dispatching",
            "mode": "team",
            "subtask_count": len(task.subtasks),
        })
        
        for subtask in task.subtasks:
            session.add_message(
                role=TeamMessageRole.SYSTEM,
                content=f"Subtask created: {subtask.instruction[:100]}... -> {subtask.assigned_agent}",
                subtask_id=subtask.id,
            )
        
        task.status = TeamTaskStatus.EXECUTING
        
        if not self._agent_executor_fn:
            raise RuntimeError("Agent executor function not set")
        
        def on_progress(subtask_id: str, status: SubTaskStatus):
            asyncio.create_task(self._notify_progress("subtask_status", {
                "session_id": session.id,
                "subtask_id": subtask_id,
                "status": status.value,
            }))
        
        subtask_results = await self._executor.execute_parallel(
            subtasks=task.subtasks,
            agent_executor_fn=self._agent_executor_fn,
            context=task.context,
            on_progress=on_progress,
        )
        
        for result in subtask_results:
            self._memory.store_subtask_result(session.id, result)
            
            session.add_message(
                role=TeamMessageRole.SUBAGENT,
                content=result.result or result.error or "No output",
                agent_id=result.agent_id,
                subtask_id=result.subtask_id,
            )
        
        task.status = TeamTaskStatus.SYNTHESIZING
        
        await self._notify_progress("task_status", {
            "session_id": session.id,
            "status": "synthesizing",
        })
        
        synthesis = self._synthesizer.synthesize(
            original_instruction=task.instruction,
            subtask_results=subtask_results,
        )
        
        session.add_message(
            role=TeamMessageRole.LEAD,
            content=synthesis.output,
        )
        
        completed = sum(1 for r in subtask_results if r.status == SubTaskStatus.COMPLETED)
        failed = sum(1 for r in subtask_results if r.status == SubTaskStatus.FAILED)
        
        return TeamResult(
            task_id=task.id,
            session_id=session.id,
            status=TeamTaskStatus.COMPLETED if failed == 0 else TeamTaskStatus.COMPLETED,
            output=synthesis.output,
            subtask_results=subtask_results,
            messages=session.messages,
            error=None if failed == 0 else f"{failed} subtask(s) failed",
            complexity=task.complexity,
            total_subtasks=len(task.subtasks),
            completed_subtasks=completed,
            failed_subtasks=failed,
            started_at=session.started_at,
            completed_at=datetime.now(),
        )
    
    def _select_agent_for_task(
        self,
        instruction: str,
        available_agents: List[str],
    ) -> str:
        instruction_lower = instruction.lower()
        
        if any(kw in instruction_lower for kw in ["search", "find", "look for", "查找", "搜索"]):
            preferred = "research-agent"
        elif any(kw in instruction_lower for kw in ["analyze", "analysis", "分析"]):
            preferred = "analysis-agent"
        elif any(kw in instruction_lower for kw in ["write", "summarize", "translate", "写作", "总结", "翻译"]):
            preferred = "writer-agent"
        else:
            preferred = "research-agent"
        
        if preferred in available_agents:
            return preferred
        
        return available_agents[0] if available_agents else "research-agent"
    
    def get_session(self, session_id: str) -> Optional[TeamSession]:
        return self._memory.get_session(session_id)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._memory.get_session_summary(session_id)
    
    def list_sessions(self) -> List[str]:
        return self._memory.list_sessions()
    
    async def cancel_session(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.status = TeamSessionStatus.CANCELLED
        if session.task:
            session.task.status = TeamTaskStatus.CANCELLED
        
        self._executor.cancel_all()
        
        await self._notify_progress("session_cancelled", {
            "session_id": session_id,
        })
        
        logger.info(f"[TeamOrchestrator] Session {session_id} cancelled")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "active_sessions": self._memory.get_active_count(),
            "executor_stats": self._executor.get_stats(),
        }
