from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, TYPE_CHECKING

from .result import NodeResult
from .context import NodeContext

if TYPE_CHECKING:
    pass


class BaseNode(ABC):
    node_type: str = ""
    node_label: str = ""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
    
    @abstractmethod
    async def execute(self, context: NodeContext) -> NodeResult:
        pass
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        return True, []
    
    def get_dependencies(self, context: NodeContext) -> List[str]:
        return context.get_dependencies(self.node_id)
    
    def get_dependency_result(self, context: NodeContext) -> Any:
        deps = self.get_dependencies(context)
        if deps:
            return context.get_dependency_result(deps[0])
        return None
    
    def get_all_dependency_results(self, context: NodeContext) -> List[Any]:
        return context.get_all_dependency_results(self.node_id)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} node_id={self.node_id} type={self.node_type}>"
