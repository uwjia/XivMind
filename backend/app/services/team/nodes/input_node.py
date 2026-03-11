import logging
from typing import Dict, Any

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("input")
class InputNode(BaseNode):
    node_type = "input"
    node_label = "Input"
    
    async def execute(self, context: NodeContext) -> NodeResult:
        instruction = context.get_instruction()
        paper_ids = context.get_paper_ids()
        ctx = context.get_context()
        
        output = {
            "instruction": instruction,
            "paper_ids": paper_ids,
            "context": ctx,
        }
        
        logger.info(f"[InputNode] Processing input: instruction={instruction[:50]}...")
        
        return NodeResult.success(output=output)
