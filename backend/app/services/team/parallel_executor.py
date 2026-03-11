import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import TimeoutError

from .types import (
    SubTask,
    SubTaskStatus,
    SubTaskResult,
    TeamTask,
    TeamTaskStatus,
    MAX_CONCURRENT_SUBAGENTS,
    SUBTASK_TIMEOUT,
)

logger = logging.getLogger(__name__)


class ParallelExecutor:
    """Parallel executor for running multiple Sub-Agents concurrently."""
    
    def __init__(
        self,
        max_concurrent: int = MAX_CONCURRENT_SUBAGENTS,
        timeout: int = SUBTASK_TIMEOUT,
    ):
        self._max_concurrent = max_concurrent
        self._timeout = timeout
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._active_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_parallel(
        self,
        subtasks: List[SubTask],
        agent_executor_fn,
        context: Optional[Dict[str, Any]] = None,
        on_progress: Optional[callable] = None,
    ) -> List[SubTaskResult]:
        if not subtasks:
            return []
        
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
        
        results: List[SubTaskResult] = []
        pending_subtasks = list(subtasks)
        completed_subtask_ids: set = set()
        
        logger.info(f"[ParallelExecutor] Starting parallel execution of {len(subtasks)} subtasks")
        
        while pending_subtasks:
            ready_tasks = []
            blocked_tasks = []
            
            for subtask in pending_subtasks:
                deps = subtask.dependencies or []
                deps_completed = all(
                    dep_id in completed_subtask_ids or str(dep_id) in completed_subtask_ids
                    for dep_id in deps
                )
                
                if deps_completed:
                    ready_tasks.append(subtask)
                else:
                    blocked_tasks.append(subtask)
            
            if not ready_tasks:
                if blocked_tasks:
                    logger.warning(f"[ParallelExecutor] Deadlock detected: {len(blocked_tasks)} blocked tasks")
                    for subtask in blocked_tasks:
                        results.append(SubTaskResult(
                            subtask_id=subtask.id,
                            agent_id=subtask.assigned_agent or "unknown",
                            status=SubTaskStatus.FAILED,
                            error="Dependency deadlock detected",
                        ))
                break
            
            batch_results = await self._execute_batch(
                ready_tasks,
                agent_executor_fn,
                context,
                on_progress,
            )
            
            for result in batch_results:
                results.append(result)
                if result.status == SubTaskStatus.COMPLETED:
                    completed_subtask_ids.add(result.subtask_id)
            
            pending_subtasks = blocked_tasks
        
        logger.info(
            f"[ParallelExecutor] Completed: {len(results)} results, "
            f"{sum(1 for r in results if r.status == SubTaskStatus.COMPLETED)} successful"
        )
        
        return results
    
    async def _execute_batch(
        self,
        subtasks: List[SubTask],
        agent_executor_fn,
        context: Optional[Dict[str, Any]],
        on_progress: Optional[callable],
    ) -> List[SubTaskResult]:
        async def run_with_semaphore(subtask: SubTask) -> SubTaskResult:
            async with self._semaphore:
                return await self._execute_single(subtask, agent_executor_fn, context, on_progress)
        
        tasks = [run_with_semaphore(st) for st in subtasks]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(SubTaskResult(
                    subtask_id=subtasks[i].id,
                    agent_id=subtasks[i].assigned_agent or "unknown",
                    status=SubTaskStatus.FAILED,
                    error=str(result),
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single(
        self,
        subtask: SubTask,
        agent_executor_fn,
        context: Optional[Dict[str, Any]],
        on_progress: Optional[callable],
    ) -> SubTaskResult:
        started_at = datetime.now()
        
        logger.info(f"[ParallelExecutor] Starting subtask {subtask.id} with agent {subtask.assigned_agent}")
        
        if on_progress:
            on_progress(subtask.id, SubTaskStatus.RUNNING)
        
        try:
            result = await asyncio.wait_for(
                agent_executor_fn(
                    agent_id=subtask.assigned_agent,
                    instruction=subtask.instruction,
                    context=context,
                    paper_ids=subtask.metadata.get("paper_ids"),
                ),
                timeout=self._timeout,
            )
            
            completed_at = datetime.now()
            
            output = result.output if hasattr(result, 'output') else str(result)
            error = result.error if hasattr(result, 'error') else None
            status = SubTaskStatus.COMPLETED if not error else SubTaskStatus.FAILED
            
            if on_progress:
                on_progress(subtask.id, status)
            
            logger.info(f"[ParallelExecutor] Subtask {subtask.id} completed with status {status}")
            
            return SubTaskResult(
                subtask_id=subtask.id,
                agent_id=subtask.assigned_agent or "unknown",
                status=status,
                result=output,
                error=error,
                started_at=started_at,
                completed_at=completed_at,
            )
            
        except asyncio.TimeoutError:
            completed_at = datetime.now()
            logger.warning(f"[ParallelExecutor] Subtask {subtask.id} timed out after {self._timeout}s")
            
            if on_progress:
                on_progress(subtask.id, SubTaskStatus.FAILED)
            
            return SubTaskResult(
                subtask_id=subtask.id,
                agent_id=subtask.assigned_agent or "unknown",
                status=SubTaskStatus.FAILED,
                error=f"Task timed out after {self._timeout} seconds",
                started_at=started_at,
                completed_at=completed_at,
            )
            
        except Exception as e:
            completed_at = datetime.now()
            logger.error(f"[ParallelExecutor] Subtask {subtask.id} failed: {e}")
            
            if on_progress:
                on_progress(subtask.id, SubTaskStatus.FAILED)
            
            return SubTaskResult(
                subtask_id=subtask.id,
                agent_id=subtask.assigned_agent or "unknown",
                status=SubTaskStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=completed_at,
            )
    
    async def execute_single_agent(
        self,
        agent_id: str,
        instruction: str,
        agent_executor_fn,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
    ) -> SubTaskResult:
        subtask = SubTask(
            id="single",
            parent_task_id="single",
            instruction=instruction,
            assigned_agent=agent_id,
        )
        
        if paper_ids:
            subtask.metadata["paper_ids"] = paper_ids
        
        return await self._execute_single(
            subtask,
            agent_executor_fn,
            context,
            None,
        )
    
    def cancel_task(self, subtask_id: str) -> bool:
        if subtask_id in self._active_tasks:
            task = self._active_tasks[subtask_id]
            task.cancel()
            logger.info(f"[ParallelExecutor] Cancelled task {subtask_id}")
            return True
        return False
    
    def cancel_all(self) -> int:
        count = 0
        for subtask_id, task in list(self._active_tasks.items()):
            task.cancel()
            count += 1
        
        self._active_tasks.clear()
        logger.info(f"[ParallelExecutor] Cancelled {count} tasks")
        return count
    
    def get_active_count(self) -> int:
        return len(self._active_tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "max_concurrent": self._max_concurrent,
            "timeout": self._timeout,
            "active_tasks": len(self._active_tasks),
        }
