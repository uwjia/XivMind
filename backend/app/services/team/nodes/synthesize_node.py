import logging
from typing import Dict, Any, List, Tuple

from .base import BaseNode
from .context import NodeContext
from .result import NodeResult
from .registry import NodeRegistry

logger = logging.getLogger(__name__)


class SynthesizeStrategy(str):
    CONCATENATE = "concatenate"
    MERGE = "merge"
    SUMMARIZE = "summarize"


@NodeRegistry.register("synthesize")
class SynthesizeNode(BaseNode):
    node_type = "synthesize"
    node_label = "Synthesize"
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        return True, []
    
    async def execute(self, context: NodeContext) -> NodeResult:
        strategy = self.get_config("strategy", "concatenate")
        
        dep_results = self.get_all_dependency_results(context)
        
        if strategy == "concatenate":
            output = self._concatenate(dep_results)
        elif strategy == "merge":
            output = self._merge(dep_results)
        elif strategy == "summarize":
            output = await self._summarize(dep_results, context)
        else:
            output = self._concatenate(dep_results)
        
        logger.info(f"[SynthesizeNode] Synthesized {len(dep_results)} results using strategy: {strategy}")
        
        return NodeResult.success(
            output=output,
            metadata={"strategy": strategy, "input_count": len(dep_results)}
        )
    
    def _concatenate(self, results: List[Any]) -> str:
        return "\n\n".join(str(r) for r in results if r)
    
    def _merge(self, results: List[Any]) -> Dict[str, Any]:
        merged = {}
        for i, result in enumerate(results):
            if isinstance(result, dict):
                merged.update(result)
            else:
                merged[f"result_{i}"] = result
        return merged
    
    async def _summarize(self, results: List[Any], context: NodeContext) -> str:
        combined = self._concatenate(results)
        if len(combined) < 500:
            return combined
        
        try:
            from app.services.subagents import subagent_manager
            summary_result = await subagent_manager.execute_agent(
                agent_id="research-agent",
                instruction=f"Summarize the following content concisely:\n\n{combined}",
                paper_ids=None,
                context=None,
            )
            return summary_result.output if hasattr(summary_result, 'output') else combined
        except Exception as e:
            logger.warning(f"[SynthesizeNode] Summarization failed: {e}, falling back to concatenation")
            return combined
