import logging
from typing import Dict, Any, List, Tuple

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("skill")
class SkillNode(BaseNode):
    node_type = "skill"
    node_label = "Skill"
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        errors = []
        if not self.config.get("skillId"):
            errors.append("Skill node must have 'skillId' configured")
        return len(errors) == 0, errors
    
    async def execute(self, context: NodeContext) -> NodeResult:
        skill_id = self.get_config("skillId", "summary")
        instruction = self.get_config("instruction") or context.get_instruction()
        
        paper_ids = context.get_paper_ids()
        ctx = context.get_context()
        
        logger.info(f"[SkillNode] Executing skill: {skill_id}")
        logger.info(f"[SkillNode] Instruction: {instruction[:100]}...")
        
        try:
            from app.services.subagents import subagent_manager
            
            agent_result = await subagent_manager.execute_agent(
                agent_id="research-agent",
                instruction=f"Use skill {skill_id}: {instruction}",
                paper_ids=paper_ids,
                context=ctx,
            )
            
            output = agent_result.output if hasattr(agent_result, 'output') else str(agent_result)
            
            logger.info(f"[SkillNode] Skill {skill_id} executed successfully")
            
            return NodeResult.success(output=output)
            
        except Exception as e:
            logger.error(f"[SkillNode] Skill {skill_id} execution failed: {e}")
            return NodeResult.error_result(str(e))
