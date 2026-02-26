import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .types import (
    SubAgentExecutionContext,
    SubAgentMessage,
    SubAgentMessageRole,
)

logger = logging.getLogger(__name__)


class SubAgentContextManager:
    """Manager for SubAgent execution contexts."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self._storage_dir = Path(storage_dir) if storage_dir else None
        self._active_contexts: Dict[str, SubAgentExecutionContext] = {}
        
        if self._storage_dir:
            self._storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_context(
        self,
        agent_id: str,
        task_id: str,
        max_turns: int = 10,
        initial_messages: Optional[List[SubAgentMessage]] = None,
        variables: Optional[Dict[str, Any]] = None,
        papers: Optional[List[Dict[str, Any]]] = None,
    ) -> SubAgentExecutionContext:
        context = SubAgentExecutionContext(
            agent_id=agent_id,
            task_id=task_id,
            messages=initial_messages or [],
            variables=variables or {},
            papers=papers or [],
            current_turn=0,
            max_turns=max_turns,
        )
        
        self._active_contexts[task_id] = context
        return context
    
    def get_context(self, task_id: str) -> Optional[SubAgentExecutionContext]:
        return self._active_contexts.get(task_id)
    
    def update_context(self, context: SubAgentExecutionContext) -> None:
        self._active_contexts[context.task_id] = context
    
    def remove_context(self, task_id: str) -> bool:
        if task_id in self._active_contexts:
            del self._active_contexts[task_id]
            return True
        return False
    
    def add_message(
        self,
        task_id: str,
        role: SubAgentMessageRole,
        content: str,
        **kwargs
    ) -> bool:
        context = self.get_context(task_id)
        if not context:
            return False
        
        context.add_message(role, content, **kwargs)
        return True
    
    def increment_turn(self, task_id: str) -> int:
        context = self.get_context(task_id)
        if not context:
            return -1
        
        context.current_turn += 1
        return context.current_turn
    
    def is_turn_limit_reached(self, task_id: str) -> bool:
        context = self.get_context(task_id)
        if not context:
            return True
        
        return context.current_turn >= context.max_turns
    
    def save_context(self, task_id: str) -> bool:
        if not self._storage_dir:
            return False
        
        context = self.get_context(task_id)
        if not context:
            return False
        
        try:
            file_path = self._storage_dir / f"{task_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save context {task_id}: {e}")
            return False
    
    def load_context(self, task_id: str) -> Optional[SubAgentExecutionContext]:
        if not self._storage_dir:
            return None
        
        try:
            file_path = self._storage_dir / f"{task_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            context = SubAgentExecutionContext.from_dict(data)
            self._active_contexts[task_id] = context
            return context
        except Exception as e:
            logger.error(f"Failed to load context {task_id}: {e}")
            return None
    
    def delete_context_file(self, task_id: str) -> bool:
        if not self._storage_dir:
            return False
        
        try:
            file_path = self._storage_dir / f"{task_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete context file {task_id}: {e}")
            return False
    
    def get_active_count(self) -> int:
        return len(self._active_contexts)
    
    def list_active_contexts(self) -> List[str]:
        return list(self._active_contexts.keys())
    
    def clear_all(self) -> int:
        count = len(self._active_contexts)
        self._active_contexts.clear()
        return count


class ContextSummarizer:
    """Summarizer for compressing context when it gets too long."""
    
    def __init__(self, max_messages: int = 50, keep_recent: int = 10):
        self.max_messages = max_messages
        self.keep_recent = keep_recent
    
    def should_summarize(self, context: SubAgentExecutionContext) -> bool:
        return len(context.messages) > self.max_messages
    
    def summarize_messages(
        self,
        messages: List[SubAgentMessage],
        keep_recent: Optional[int] = None,
        language: str = "en"
    ) -> List[SubAgentMessage]:
        if len(messages) <= self.max_messages:
            return messages
        
        keep = keep_recent or self.keep_recent
        recent_messages = messages[-keep:]
        old_messages = messages[:-keep]
        
        if language == "zh":
            return self._summarize_zh(old_messages, recent_messages)
        return self._summarize_en(old_messages, recent_messages)
    
    def _summarize_en(
        self,
        old_messages: List[SubAgentMessage],
        recent_messages: List[SubAgentMessage]
    ) -> List[SubAgentMessage]:
        summary_parts = ["[Conversation History Summary]\n"]
        for msg in old_messages:
            role_name = {
                SubAgentMessageRole.SYSTEM: "System",
                SubAgentMessageRole.USER: "User",
                SubAgentMessageRole.ASSISTANT: "Assistant",
                SubAgentMessageRole.TOOL: "Tool",
            }.get(msg.role, msg.role.value)
            
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            summary_parts.append(f"{role_name}: {content}\n")
        
        summary_message = SubAgentMessage(
            role=SubAgentMessageRole.SYSTEM,
            content="\n".join(summary_parts),
            timestamp=datetime.now()
        )
        
        return [summary_message] + recent_messages
    
    def _summarize_zh(
        self,
        old_messages: List[SubAgentMessage],
        recent_messages: List[SubAgentMessage]
    ) -> List[SubAgentMessage]:
        summary_parts = ["[历史对话摘要]\n"]
        for msg in old_messages:
            role_name = {
                SubAgentMessageRole.SYSTEM: "系统",
                SubAgentMessageRole.USER: "用户",
                SubAgentMessageRole.ASSISTANT: "助手",
                SubAgentMessageRole.TOOL: "工具",
            }.get(msg.role, msg.role.value)
            
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            summary_parts.append(f"{role_name}: {content}\n")
        
        summary_message = SubAgentMessage(
            role=SubAgentMessageRole.SYSTEM,
            content="\n".join(summary_parts),
            timestamp=datetime.now()
        )
        
        return [summary_message] + recent_messages
