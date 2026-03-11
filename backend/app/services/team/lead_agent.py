import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from .types import (
    TaskComplexity,
    TeamTask,
    TeamTaskStatus,
    SubTask,
    SubTaskStatus,
    TeamMessage,
    TeamMessageRole,
    TeamSession,
    DecompositionResult,
    LeadAgentConfig,
)
from .decomposer import TaskDecomposer

logger = logging.getLogger(__name__)


LEAD_AGENT_SYSTEM_PROMPT = """You are a Lead Agent responsible for orchestrating a team of specialized Sub-Agents for complex research tasks.

## Your Responsibilities

1. **Task Analysis**: Understand user intent and evaluate task complexity
2. **Task Decomposition**: Break complex tasks into independent subtasks
3. **Agent Selection**: Choose appropriate Sub-Agents for each subtask
4. **Parallel Dispatch**: Distribute tasks to multiple Sub-Agents
5. **Result Synthesis**: Integrate results into a coherent final output

## Decision Framework

### When to use Team Mode

- Task involves multiple topics → YES
- Task requires comparison → YES
- Task scope is broad → YES
- Simple single-topic query → NO

### Sub-Agent Selection

| Subtask Type | Recommended Agent |
|--------------|-------------------|
| Literature search | research-agent |
| Paper analysis | analysis-agent |
| Writing/summarizing | writer-agent |

## Tool Format

When using tools, use the following format:

[TOOL: delegate_task({"subtasks": [{"instruction": "...", "agent_id": "research-agent"}, {"instruction": "...", "agent_id": "analysis-agent"}]})]

[TOOL: synthesize_results({"results": ["result1", "result2"], "format": "report"})]

## Workflow

1. Analyze the user's request
2. Determine if Team Mode is needed
3. If YES: decompose and dispatch
4. Wait for all results
5. Synthesize final output
6. Output [DONE] marker when complete

## Output Format

When you have completed the task, provide a comprehensive response and end with [DONE].
"""


class LeadAgent:
    """Lead Agent for orchestrating multi-agent team tasks."""
    
    def __init__(
        self,
        config: Optional[LeadAgentConfig] = None,
        decomposer: Optional[TaskDecomposer] = None,
    ):
        self._config = config or LeadAgentConfig()
        self._decomposer = decomposer or TaskDecomposer()
        self._current_turn = 0
        self._max_turns = self._config.max_turns
    
    @property
    def id(self) -> str:
        return self._config.id
    
    @property
    def name(self) -> str:
        return self._config.name
    
    @property
    def config(self) -> LeadAgentConfig:
        return self._config
    
    def get_system_prompt(self) -> str:
        return LEAD_AGENT_SYSTEM_PROMPT
    
    def analyze_task(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DecompositionResult:
        logger.info(f"[LeadAgent] Analyzing task (sync): {instruction[:100]}...")
        
        result = self._decomposer.decompose(instruction, context)
        
        logger.info(
            f"[LeadAgent] Analysis complete - "
            f"Complexity: {result.complexity.value}, "
            f"Team Mode: {result.use_team_mode}, "
            f"Subtasks: {len(result.subtasks)}"
        )
        
        return result
    
    async def analyze_task_async(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        logger.info(f"[LeadAgent] Analyzing task (async): {instruction[:100]}...")
        
        result = await self._decomposer.decompose_async(
            instruction, context, provider=provider, model=model
        )
        
        logger.info(
            f"[LeadAgent] Analysis complete - "
            f"Complexity: {result.complexity.value}, "
            f"Team Mode: {result.use_team_mode}, "
            f"Subtasks: {len(result.subtasks)}"
        )
        
        return result
    
    def create_team_task(
        self,
        instruction: str,
        decomposition: DecompositionResult,
        context: Optional[Dict[str, Any]] = None,
        paper_ids: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> TeamTask:
        task = TeamTask(
            instruction=instruction,
            complexity=decomposition.complexity,
            context=context or {},
            paper_ids=paper_ids,
            provider=provider or self._config.provider,
            model=model or self._config.model,
        )
        
        if decomposition.use_team_mode:
            logger.info(f"[LeadAgent] Decomposed into {len(decomposition.subtasks)} subtasks:")
            for i, subtask_data in enumerate(decomposition.subtasks):
                agent = subtask_data.get("assigned_agent", "analysis-agent")
                task_type = subtask_data.get("task_type", "analysis")
                deps = subtask_data.get("dependencies", [])
                deps_str = [str(d) for d in deps] if deps else []
                metadata = subtask_data.get("metadata", {})
                instruction = subtask_data.get("instruction", "")[:100]
                
                subtask = SubTask(
                    id=f"{task.id}_sub_{i}",
                    parent_task_id=task.id,
                    instruction=instruction,
                    assigned_agent=subtask_data.get("assigned_agent"),
                    dependencies=deps_str,
                    metadata=metadata,
                )
                if subtask_data.get("paper_ids"):
                    subtask.metadata["paper_ids"] = subtask_data["paper_ids"]
                task.subtasks.append(subtask)
                
                logger.info(f"  [{i}] Agent: {agent}, Type: {task_type}, Deps: {deps_str}")
                logger.info(f"      Instruction: {instruction[:80]}...")
            
        logger.info(f"[LeadAgent] Created team task {task.id} with {len(task.subtasks)} subtasks")
        return task
    
    def get_initial_message(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> str:
        context_str = ""
        if context:
            papers = context.get("papers", [])
            if papers:
                context_str = "\n\n## Available Papers\n"
                for i, paper in enumerate(papers[:5], 1):
                    title = paper.get("title", "Unknown")
                    paper_id = paper.get("id", "")
                    context_str += f"{i}. [{paper_id}] {title}\n"
        
        return f"""Please help me with the following research task:

{instruction}
{context_str}

Analyze this task and determine the best approach. If it requires multiple agents, decompose it and use the delegate_task tool to dispatch subtasks to appropriate agents.
"""
    
    def parse_delegate_call(self, response: str) -> Optional[Dict[str, Any]]:
        pattern = r'\[TOOL:\s*delegate_task\s*\((.*?)\)\]'
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return None
        
        args_str = match.group(1).strip()
        
        try:
            args = json.loads(args_str)
            return args
        except json.JSONDecodeError:
            logger.warning(f"[LeadAgent] Failed to parse delegate_task arguments: {args_str}")
            return None
    
    def parse_synthesize_call(self, response: str) -> Optional[Dict[str, Any]]:
        pattern = r'\[TOOL:\s*synthesize_results\s*\((.*?)\)\]'
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return None
        
        args_str = match.group(1).strip()
        
        try:
            args = json.loads(args_str)
            return args
        except json.JSONDecodeError:
            logger.warning(f"[LeadAgent] Failed to parse synthesize_results arguments: {args_str}")
            return None
    
    def should_stop(self, response: str) -> bool:
        stop_markers = ["[DONE]", "[COMPLETE]", "[FINISHED]"]
        return any(marker in response for marker in stop_markers)
    
    def build_context_message(
        self,
        subtask_results: List[Dict[str, Any]],
    ) -> str:
        if not subtask_results:
            return ""
        
        message_parts = ["## Sub-Agent Results\n"]
        
        for i, result in enumerate(subtask_results, 1):
            agent_id = result.get("agent_id", "unknown")
            subtask_id = result.get("subtask_id", "unknown")
            status = result.get("status", "unknown")
            output = result.get("result", result.get("output", ""))
            
            if len(output) > 1000:
                output = output[:1000] + "..."
            
            message_parts.append(f"### Result {i} (Agent: {agent_id})")
            message_parts.append(f"Status: {status}")
            message_parts.append(f"Output:\n{output}\n")
        
        message_parts.append("\nPlease synthesize these results into a comprehensive response. Use [TOOL: synthesize_results(...)] if needed, or provide your final answer with [DONE].")
        
        return "\n".join(message_parts)
    
    def build_final_prompt(
        self,
        instruction: str,
        subtask_results: List[Dict[str, Any]],
    ) -> str:
        return f"""Based on the following sub-agent results, please provide a comprehensive response to the original request.

## Original Request
{instruction}

{self.build_context_message(subtask_results)}

Provide your synthesized response and end with [DONE].
"""
    
    def increment_turn(self) -> int:
        self._current_turn += 1
        return self._current_turn
    
    def is_turn_limit_reached(self) -> bool:
        return self._current_turn >= self._max_turns
    
    def reset_turns(self) -> None:
        self._current_turn = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "config": self._config.to_dict(),
            "current_turn": self._current_turn,
            "max_turns": self._max_turns,
        }
