import logging
from typing import Dict, Any

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("decompose")
class DecomposeNode(BaseNode):
    node_type = "decompose"
    node_label = "Decompose"
    
    async def execute(self, context: NodeContext) -> NodeResult:
        if context.get_analysis is None:
            return NodeResult.error_result("Analysis function not available in context")
        
        try:
            analysis = await context.get_analysis()
            
            subtasks = analysis.subtasks
            
            logger.info(f"[DecomposeNode] Decomposed into {len(subtasks)} subtasks")
            
            return NodeResult.success(output=subtasks)
            
        except Exception as e:
            logger.error(f"[DecomposeNode] Decomposition failed: {e}")
            return NodeResult.error_result(str(e))
