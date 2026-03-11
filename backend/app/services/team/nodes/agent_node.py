import logging
from typing import Dict, Any, List, Tuple

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("agent")
class AgentNode(BaseNode):
    node_type = "agent"
    node_label = "Agent"
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        errors = []
        if not self.config.get("agentId"):
            errors.append("Agent node must have 'agentId' configured")
        return len(errors) == 0, errors
    
    async def execute(self, context: NodeContext) -> NodeResult:
        agent_id = self.get_config("agentId", "research-agent")
        instruction = self.get_config("instruction") or context.get_instruction()
        timeout = self.get_config("timeout", 300)
        
        paper_ids = context.get_paper_ids()
        ctx = context.get_context()
        
        logger.info(f"[AgentNode] Executing agent: {agent_id}")
        logger.info(f"[AgentNode] Instruction: {instruction[:100]}...")
        
        try:
            from app.services.subagents import subagent_manager
            
            agent_result = await subagent_manager.execute_agent(
                agent_id=agent_id,
                instruction=instruction,
                paper_ids=paper_ids,
                context=ctx,
            )
            
            output = agent_result.output if hasattr(agent_result, 'output') else str(agent_result)
            
            logger.info(f"[AgentNode] Agent {agent_id} completed successfully")
            
            return NodeResult.success(output=output)
            
        except Exception as e:
            logger.error(f"[AgentNode] Agent {agent_id} execution failed: {e}")
            return NodeResult.error_result(str(e))
