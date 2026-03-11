from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    STANDARD = "standard"
    MODERATE = "moderate"
    HIGH = "high"


class TeamTaskStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DECOMPOSING = "decomposing"
    DISPATCHING = "dispatching"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubTaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TeamSessionStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TeamMessageRole(str, Enum):
    USER = "user"
    LEAD = "lead"
    SUBAGENT = "subagent"
    SYSTEM = "system"


class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    parent_task_id: str
    instruction: str
    assigned_agent: Optional[str] = None
    dependencies: List[str] = []
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_task_id": self.parent_task_id,
            "instruction": self.instruction,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


class TeamTask(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    instruction: str
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    subtasks: List[SubTask] = []
    status: TeamTaskStatus = TeamTaskStatus.PENDING
    context: Dict[str, Any] = {}
    paper_ids: Optional[List[str]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "instruction": self.instruction,
            "complexity": self.complexity.value,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "status": self.status.value,
            "context": self.context,
            "paper_ids": self.paper_ids,
            "provider": self.provider,
            "model": self.model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TeamMessage(BaseModel):
    role: TeamMessageRole
    content: str
    agent_id: Optional[str] = None
    subtask_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "agent_id": self.agent_id,
            "subtask_id": self.subtask_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
        }


class SubTaskResult(BaseModel):
    subtask_id: str
    agent_id: str
    status: SubTaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "subtask_id": self.subtask_id,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TeamResult(BaseModel):
    task_id: str
    session_id: str
    status: TeamTaskStatus
    output: str = ""
    subtask_results: List[SubTaskResult] = []
    messages: List[TeamMessage] = []
    error: Optional[str] = None
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    total_subtasks: int = 0
    completed_subtasks: int = 0
    failed_subtasks: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "output": self.output,
            "subtask_results": [r.to_dict() for r in self.subtask_results],
            "messages": [m.to_dict() for m in self.messages],
            "error": self.error,
            "complexity": self.complexity.value,
            "total_subtasks": self.total_subtasks,
            "completed_subtasks": self.completed_subtasks,
            "failed_subtasks": self.failed_subtasks,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class LeadAgentConfig(BaseModel):
    id: str = "lead-agent"
    name: str = "Team Lead Agent"
    description: str = "Orchestrates multiple Sub-Agents for complex research tasks"
    icon: str = "users"
    max_turns: int = 20
    temperature: float = 0.3
    model: Optional[str] = None
    provider: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "max_turns": self.max_turns,
            "temperature": self.temperature,
            "model": self.model,
            "provider": self.provider,
        }


class TeamSession(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    task: Optional[TeamTask] = None
    lead_agent_config: LeadAgentConfig = Field(default_factory=LeadAgentConfig)
    available_agents: List[str] = []
    messages: List[TeamMessage] = []
    status: TeamSessionStatus = TeamSessionStatus.INITIALIZING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def add_message(
        self,
        role: TeamMessageRole,
        content: str,
        agent_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TeamMessage:
        message = TeamMessage(
            role=role,
            content=content,
            agent_id=agent_id,
            subtask_id=subtask_id,
            metadata=metadata or {},
        )
        self.messages.append(message)
        return message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task": self.task.to_dict() if self.task else None,
            "lead_agent_config": self.lead_agent_config.to_dict(),
            "available_agents": self.available_agents,
            "messages": [m.to_dict() for m in self.messages],
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TeamExecuteRequest(BaseModel):
    instruction: str
    context: Optional[Dict[str, Any]] = None
    paper_ids: Optional[List[str]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    force_team_mode: bool = False


class TaskType(str, Enum):
    SEARCH = "search"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    WRITING = "writing"
    COMPARISON = "comparison"
    REVIEW = "review"
    TRANSLATION = "translation"


class DecompositionStrategy(str, Enum):
    LLM = "llm"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


class DecompositionResult(BaseModel):
    complexity: TaskComplexity
    use_team_mode: bool
    subtasks: List[Dict[str, Any]] = []
    reasoning: str = ""
    strategy: DecompositionStrategy = DecompositionStrategy.HYBRID
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "complexity": self.complexity.value,
            "use_team_mode": self.use_team_mode,
            "subtasks": self.subtasks,
            "reasoning": self.reasoning,
            "strategy": self.strategy.value,
            "confidence": self.confidence,
        }


class SynthesisResult(BaseModel):
    output: str
    sources: List[str] = []
    confidence: float = 0.8
    needs_more_info: bool = False
    follow_up_questions: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "output": self.output,
            "sources": self.sources,
            "confidence": self.confidence,
            "needs_more_info": self.needs_more_info,
            "follow_up_questions": self.follow_up_questions,
        }


MAX_CONCURRENT_SUBAGENTS = 5
MAX_SUBTASKS = 10
SUBTASK_TIMEOUT = 300
TEAM_SESSION_TIMEOUT = 1800
MIN_SUBTASKS_FOR_TEAM = 2
