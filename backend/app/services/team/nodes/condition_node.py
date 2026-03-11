import logging
from typing import Dict, Any, List, Tuple

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("condition")
class ConditionNode(BaseNode):
    node_type = "condition"
    node_label = "Condition"
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        errors = []
        if not self.config.get("condition"):
            errors.append("Condition node must have 'condition' expression configured")
        return len(errors) == 0, errors
    
    async def execute(self, context: NodeContext) -> NodeResult:
        condition_expr = self.get_config("condition", "true")
        
        dep_results = self.get_all_dependency_results(context)
        
        try:
            local_vars = {
                "result": dep_results[0] if dep_results else None,
                "results": dep_results,
                "complexity": None,
                "status": None,
            }
            
            if dep_results and isinstance(dep_results[0], dict):
                local_vars["complexity"] = dep_results[0].get("complexity")
                local_vars["status"] = dep_results[0].get("status")
            
            result = eval(condition_expr, {"__builtins__": {}}, local_vars)
            branch = "true" if result else "false"
            
            logger.info(f"[ConditionNode] Condition '{condition_expr}' evaluated to: {branch}")
            
            return NodeResult.success(
                output=branch,
                metadata={"branch": branch, "condition": condition_expr}
            )
            
        except Exception as e:
            logger.warning(f"[ConditionNode] Condition evaluation failed: {e}, defaulting to 'true'")
            return NodeResult.success(
                output="true",
                metadata={"branch": "true", "error": str(e)}
            )
