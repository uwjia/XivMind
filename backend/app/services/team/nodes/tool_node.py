import logging
from typing import Dict, Any, List, Tuple

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("tool")
class ToolNode(BaseNode):
    node_type = "tool"
    node_label = "Tool"
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        errors = []
        if not self.config.get("toolId"):
            errors.append("Tool node must have 'toolId' configured")
        return len(errors) == 0, errors
    
    async def execute(self, context: NodeContext) -> NodeResult:
        tool_id = self.get_config("toolId", "")
        instruction = self.get_config("instruction") or context.get_instruction()
        
        paper_ids = context.get_paper_ids()
        ctx = context.get_context()
        
        logger.info(f"[ToolNode] Executing tool: {tool_id}")
        logger.info(f"[ToolNode] Instruction: {instruction[:100]}...")
        
        try:
            from app.services.subagents import subagent_manager
            
            agent_result = await subagent_manager.execute_agent(
                agent_id="research-agent",
                instruction=f"Use tool {tool_id}: {instruction}",
                paper_ids=paper_ids,
                context=ctx,
            )
            
            output = agent_result.output if hasattr(agent_result, 'output') else str(agent_result)
            
            logger.info(f"[ToolNode] Tool {tool_id} executed successfully")
            
            return NodeResult.success(output=output)
            
        except Exception as e:
            logger.error(f"[ToolNode] Tool {tool_id} execution failed: {e}")
            return NodeResult.error_result(str(e))
