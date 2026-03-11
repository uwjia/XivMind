import logging
from typing import Dict, Any

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("output")
class OutputNode(BaseNode):
    node_type = "output"
    node_label = "Output"
    
    async def execute(self, context: NodeContext) -> NodeResult:
        dep_results = self.get_all_dependency_results(context)
        
        if dep_results:
            if len(dep_results) == 1:
                output = dep_results[0]
            else:
                output = "\n\n".join(str(r) for r in dep_results if r)
        else:
            output = ""
        
        logger.info(f"[OutputNode] Generating final output")
        
        return NodeResult.success(output=output)
