import logging
from typing import Dict, Any

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


@NodeRegistry.register("analyze")
class AnalyzeNode(BaseNode):
    node_type = "analyze"
    node_label = "Analyze"
    
    async def execute(self, context: NodeContext) -> NodeResult:
        if context.get_analysis is None:
            return NodeResult.error_result("Analysis function not available in context")
        
        try:
            analysis = await context.get_analysis()
            
            logger.info(f"[AnalyzeNode] Task Analysis Result:")
            logger.info(f"  Complexity: {analysis.complexity.value}")
            logger.info(f"  Team Mode: {analysis.use_team_mode}")
            logger.info(f"  Subtasks: {len(analysis.subtasks)}")
            
            if analysis.use_team_mode and analysis.subtasks:
                for i, subtask in enumerate(analysis.subtasks):
                    agent = subtask.get("assigned_agent", "analysis-agent")
                    task_type = subtask.get("task_type", "analysis")
                    deps = subtask.get("dependencies", [])
                    instruction = subtask.get("instruction", "")[:60]
                    logger.info(f"  [{i}] Agent: {agent}, Type: {task_type}, Deps: {deps}")
                    logger.info(f"      Instruction: {instruction}...")
            
            output = {
                "complexity": analysis.complexity.value,
                "use_team_mode": analysis.use_team_mode,
                "subtasks": analysis.subtasks,
                "reasoning": analysis.reasoning,
            }
            
            return NodeResult.success(output=output)
            
        except Exception as e:
            logger.error(f"[AnalyzeNode] Analysis failed: {e}")
            return NodeResult.error_result(str(e))
