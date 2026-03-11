import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .types import (
    TeamSession,
    TeamTask,
    SubTask,
    TeamMessage,
    TeamMessageRole,
    SubTaskResult,
)

logger = logging.getLogger(__name__)


class TeamMemory:
    """Team memory for storing task plans, intermediate results, and execution state."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self._storage_dir = Path(storage_dir) if storage_dir else None
        self._sessions: Dict[str, TeamSession] = {}
        self._task_results: Dict[str, List[SubTaskResult]] = {}
        self._intermediate_results: Dict[str, Dict[str, Any]] = {}
        
        if self._storage_dir:
            self._storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(
        self,
        task: TeamTask,
        available_agents: List[str],
    ) -> TeamSession:
        session = TeamSession(
            task=task,
            available_agents=available_agents,
        )
        self._sessions[session.id] = session
        self._task_results[session.id] = []
        self._intermediate_results[session.id] = {}
        
        logger.info(f"[TeamMemory] Created session {session.id} for task {task.id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[TeamSession]:
        return self._sessions.get(session_id)
    
    def update_session(self, session: TeamSession) -> None:
        self._sessions[session.id] = session
    
    def remove_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._task_results.pop(session_id, None)
            self._intermediate_results.pop(session_id, None)
            logger.info(f"[TeamMemory] Removed session {session_id}")
            return True
        return False
    
    def add_message(
        self,
        session_id: str,
        role: TeamMessageRole,
        content: str,
        agent_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TeamMessage]:
        session = self.get_session(session_id)
        if not session:
            return None
        
        message = session.add_message(
            role=role,
            content=content,
            agent_id=agent_id,
            subtask_id=subtask_id,
            metadata=metadata,
        )
        return message
    
    def store_subtask_result(
        self,
        session_id: str,
        result: SubTaskResult,
    ) -> bool:
        if session_id not in self._task_results:
            self._task_results[session_id] = []
        
        self._task_results[session_id].append(result)
        
        session = self.get_session(session_id)
        if session and session.task:
            for subtask in session.task.subtasks:
                if subtask.id == result.subtask_id:
                    subtask.status = result.status
                    subtask.result = result.result
                    subtask.error = result.error
                    subtask.completed_at = result.completed_at
                    break
        
        logger.info(f"[TeamMemory] Stored result for subtask {result.subtask_id} in session {session_id}")
        return True
    
    def get_subtask_results(self, session_id: str) -> List[SubTaskResult]:
        return self._task_results.get(session_id, [])
    
    def store_intermediate(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> bool:
        if session_id not in self._intermediate_results:
            self._intermediate_results[session_id] = {}
        
        self._intermediate_results[session_id][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }
        return True
    
    def get_intermediate(
        self,
        session_id: str,
        key: str,
    ) -> Optional[Any]:
        session_data = self._intermediate_results.get(session_id, {})
        entry = session_data.get(key)
        return entry.get("value") if entry else None
    
    def save_session(self, session_id: str) -> bool:
        if not self._storage_dir:
            return False
        
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            file_path = self._storage_dir / f"{session_id}.json"
            data = {
                "session": session.to_dict(),
                "results": [r.to_dict() for r in self._task_results.get(session_id, [])],
                "intermediate": self._intermediate_results.get(session_id, {}),
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"[TeamMemory] Saved session {session_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"[TeamMemory] Failed to save session {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[TeamSession]:
        if not self._storage_dir:
            return None
        
        try:
            file_path = self._storage_dir / f"{session_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            session_data = data.get("session", {})
            task_data = session_data.get("task")
            
            task = None
            if task_data:
                subtasks = [
                    SubTask(**st) for st in task_data.get("subtasks", [])
                ]
                task = TeamTask(
                    id=task_data["id"],
                    instruction=task_data["instruction"],
                    subtasks=subtasks,
                    **{k: v for k, v in task_data.items() if k not in ["id", "instruction", "subtasks"]},
                )
            
            messages = [
                TeamMessage(**m) for m in session_data.get("messages", [])
            ]
            
            session = TeamSession(
                id=session_data["id"],
                task=task,
                available_agents=session_data.get("available_agents", []),
                messages=messages,
                status=session_data.get("status", "initializing"),
            )
            
            self._sessions[session_id] = session
            
            results_data = data.get("results", [])
            self._task_results[session_id] = [
                SubTaskResult(**r) for r in results_data
            ]
            
            self._intermediate_results[session_id] = data.get("intermediate", {})
            
            logger.info(f"[TeamMemory] Loaded session {session_id}")
            return session
        except Exception as e:
            logger.error(f"[TeamMemory] Failed to load session {session_id}: {e}")
            return None
    
    def delete_session_file(self, session_id: str) -> bool:
        if not self._storage_dir:
            return False
        
        try:
            file_path = self._storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"[TeamMemory] Failed to delete session file {session_id}: {e}")
            return False
    
    def list_sessions(self) -> List[str]:
        return list(self._sessions.keys())
    
    def get_active_count(self) -> int:
        return len(self._sessions)
    
    def clear_all(self) -> int:
        count = len(self._sessions)
        self._sessions.clear()
        self._task_results.clear()
        self._intermediate_results.clear()
        return count
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        
        results = self.get_subtask_results(session_id)
        
        return {
            "session_id": session_id,
            "task_id": session.task.id if session.task else None,
            "instruction": session.task.instruction if session.task else None,
            "status": session.status.value if session.status else None,
            "total_subtasks": len(session.task.subtasks) if session.task else 0,
            "completed_subtasks": sum(1 for r in results if r.status == "completed"),
            "failed_subtasks": sum(1 for r in results if r.status == "failed"),
            "message_count": len(session.messages),
        }
