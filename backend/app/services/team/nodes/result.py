from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from enum import Enum


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class NodeResult:
    status: NodeStatus
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    @classmethod
    def success(cls, output: Any = None, metadata: Optional[Dict[str, Any]] = None) -> "NodeResult":
        return cls(
            status=NodeStatus.SUCCESS,
            output=output,
            metadata=metadata or {},
        )
    
    @classmethod
    def error_result(cls, error: str, output: Any = None) -> "NodeResult":
        return cls(
            status=NodeStatus.ERROR,
            output=output,
            error=error,
        )
    
    @classmethod
    def skipped(cls, reason: str = "") -> "NodeResult":
        return cls(
            status=NodeStatus.SKIPPED,
            metadata={"reason": reason},
        )
