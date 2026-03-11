from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..workflow_adapter import Workflow, WorkflowInput
    from ..types import DecompositionResult


@dataclass
class NodeContext:
    session_id: str
    workflow_id: str
    input_data: "WorkflowInput"
    node_results: Dict[str, Any]
    workflow: "Workflow"
    get_analysis: Optional[Callable[[], Awaitable["DecompositionResult"]]] = None
    
    def get_dependencies(self, node_id: str) -> List[str]:
        dependencies = []
        for edge in self.workflow.edges:
            if edge.target == node_id:
                dependencies.append(edge.source)
        return dependencies
    
    def get_dependency_result(self, node_id: str) -> Optional[Any]:
        result = self.node_results.get(node_id)
        if result is None:
            return None
        return result.get("output")
    
    def get_all_dependency_results(self, node_id: str) -> List[Any]:
        deps = self.get_dependencies(node_id)
        results = []
        for dep_id in deps:
            result = self.get_dependency_result(dep_id)
            if result is not None:
                results.append(result)
        return results
    
    def get_dependency_results_dict(self, node_id: str) -> Dict[str, Any]:
        deps = self.get_dependencies(node_id)
        return {dep_id: self.node_results.get(dep_id, {}) for dep_id in deps}
    
    def get_node_by_id(self, node_id: str) -> Optional[Any]:
        for node in self.workflow.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_instruction(self) -> str:
        return self.input_data.instruction
    
    def get_paper_ids(self) -> Optional[List[str]]:
        return self.input_data.paper_ids
    
    def get_context(self) -> Optional[Dict[str, Any]]:
        return self.input_data.context
