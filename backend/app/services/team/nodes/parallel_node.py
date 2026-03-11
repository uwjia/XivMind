import logging
import asyncio
from typing import Dict, Any, List

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("parallel")
class ParallelNode(BaseNode):
    node_type = "parallel"
    node_label = "Parallel"
    
    async def execute(self, context: NodeContext) -> NodeResult:
        dep_results = self.get_all_dependency_results(context)
        
        logger.info(f"[ParallelNode] Processing {len(dep_results)} parallel results")
        
        return NodeResult.success(
            output=dep_results,
            metadata={"parallel_count": len(dep_results)}
        )
