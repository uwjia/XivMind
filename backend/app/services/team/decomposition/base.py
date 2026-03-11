from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..types import DecompositionResult


class BaseDecomposer(ABC):
    """Base class for task decomposition strategies."""
    
    @abstractmethod
    def decompose(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
    ) -> DecompositionResult:
        """
        Decompose a task into subtasks.
        
        Args:
            instruction: The task instruction to decompose
            context: Additional context (papers, metadata, etc.)
            available_agents: List of available agent IDs
            
        Returns:
            DecompositionResult with complexity, subtasks, etc.
        """
        pass
    
    async def decompose_async(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        """
        Async version of decompose.
        
        Default implementation calls the sync version.
        Subclasses can override for true async support.
        """
        return self.decompose(instruction, context, available_agents)
