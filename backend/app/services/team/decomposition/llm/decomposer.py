import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ...types import TaskComplexity, DecompositionResult, MAX_SUBTASKS
from ..base import BaseDecomposer

logger = logging.getLogger(__name__)


@dataclass
class DecompositionCache:
    instruction_hash: str
    result: DecompositionResult
    created_at: datetime
    ttl_seconds: int = 3600
    
    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)


@dataclass
class SubTaskSpec:
    instruction: str
    task_type: str
    assigned_agent: Optional[str] = None
    dependencies: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMDecompositionResult:
    complexity: TaskComplexity
    use_team_mode: bool
    subtasks: List[SubTaskSpec]
    reasoning: str


DECOMPOSITION_SYSTEM_PROMPT = """You are an intelligent task decomposition system for a multi-agent research platform.

Your role is to analyze user requests and decompose complex tasks into subtasks that can be executed by specialized agents.

## Available Agent Types

- **research-agent**: Specialized in searching and finding papers, literature discovery
- **analysis-agent**: Specialized in analyzing paper content, extracting insights, comparing papers
- **writer-agent**: Specialized in writing summaries, reports, translations

## Task Complexity Levels

- **simple**: Single topic, straightforward query, can be handled by one agent
- **standard**: Multiple aspects but cohesive, may benefit from 2 agents
- **moderate**: Multiple topics or requires comparison, needs 2-3 agents
- **high**: Comprehensive analysis, multiple papers, systematic review, needs 3+ agents

## Decomposition Guidelines

1. **Identify Task Type**: Determine if the task is search, analysis, comparison, review, or synthesis
2. **Extract Topics**: Identify distinct topics, papers, or aspects mentioned
3. **Determine Dependencies**: Some subtasks may depend on results from others
4. **Assign Agents**: Match subtasks to the most suitable agent type
5. **Add Synthesis**: For multi-agent tasks, add a final synthesis subtask

## Output Format

Return ONLY a valid JSON object with this structure:
{{
    "complexity": "simple|standard|moderate|high",
    "use_team_mode": true|false,
    "subtasks": [
        {{
            "instruction": "Clear instruction for the subtask",
            "task_type": "search|analysis|synthesis|writing",
            "assigned_agent": "agent-id",
            "dependencies": [0, 1]
        }}
    ],
    "reasoning": "Brief explanation of the decomposition decision"
}}

## Important Rules

- Maximum {max_subtasks} subtasks allowed
- Dependencies must reference subtask indices (0-based)
- Synthesis tasks should depend on all relevant analysis tasks
- Simple tasks should have use_team_mode=false and empty subtasks array
- Always return valid JSON, no markdown formatting"""


DECOMPOSITION_USER_PROMPT = """Analyze and decompose the following task:

## Task
{instruction}

## Context
{context}

## Available Agents
{available_agents}

## Additional Information
- Paper IDs: {paper_ids}
- Paper count: {paper_count}

Return the decomposition result as JSON."""


class LLMDecomposer(BaseDecomposer):
    """LLM-based intelligent task decomposition."""
    
    def __init__(
        self,
        cache_ttl: int = 3600,
        max_cache_size: int = 100,
        max_retries: int = 2,
    ):
        self._cache: Dict[str, DecompositionCache] = {}
        self._cache_ttl = cache_ttl
        self._max_cache_size = max_cache_size
        self._max_retries = max_retries
        self._llm_service = None
    
    def decompose(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
    ) -> DecompositionResult:
        """Sync decompose - uses fallback rule-based decomposition."""
        return self._fallback_decomposition(instruction, context, available_agents)
    
    def _get_llm_service(self):
        if self._llm_service is None:
            from app.services.llm_service import llm_service
            self._llm_service = llm_service
        return self._llm_service
    
    def _hash_instruction(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        content = instruction
        if context:
            paper_ids = context.get("paper_ids", [])
            if paper_ids:
                content += f"|papers:{','.join(sorted(paper_ids))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[DecompositionResult]:
        entry = self._cache.get(cache_key)
        if entry and not entry.is_expired():
            logger.debug(f"[LLMDecomposer] Cache hit for key: {cache_key[:8]}")
            return entry.result
        if entry:
            del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result: DecompositionResult) -> None:
        if len(self._cache) >= self._max_cache_size:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at
            )
            del self._cache[oldest_key]
        
        self._cache[cache_key] = DecompositionCache(
            instruction_hash=cache_key,
            result=result,
            created_at=datetime.now(),
            ttl_seconds=self._cache_ttl,
        )
    
    def _build_context_str(self, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return "No additional context provided."
        
        parts = []
        
        papers = context.get("papers", [])
        if papers:
            parts.append(f"Available papers: {len(papers)}")
            for i, paper in enumerate(papers[:3], 1):
                title = paper.get("title", "Unknown")
                parts.append(f"  {i}. {title[:80]}...")
        
        if not parts:
            return "No additional context provided."
        
        return "\n".join(parts)
    
    def _build_agents_str(self, available_agents: Optional[List[str]]) -> str:
        if not available_agents:
            return "research-agent, analysis-agent, writer-agent"
        return ", ".join(available_agents)
    
    async def decompose_async(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        cache_key = self._hash_instruction(instruction, context)
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = await self._decompose_with_llm(
            instruction=instruction,
            context=context,
            available_agents=available_agents,
            provider=provider,
            model=model,
        )
        
        self._set_cache(cache_key, result)
        
        return result
    
    async def _decompose_with_llm(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        llm_service = self._get_llm_service()
        
        paper_ids = context.get("paper_ids", []) if context else []
        paper_count = len(paper_ids) if paper_ids else 0
        
        system_prompt = DECOMPOSITION_SYSTEM_PROMPT.format(
            max_subtasks=MAX_SUBTASKS
        )
        
        user_prompt = DECOMPOSITION_USER_PROMPT.format(
            instruction=instruction,
            context=self._build_context_str(context),
            available_agents=self._build_agents_str(available_agents),
            paper_ids=", ".join(paper_ids) if paper_ids else "None",
            paper_count=paper_count,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        last_error = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await llm_service.generate_with_messages(
                    messages=messages,
                    provider=provider,
                    model=model,
                    temperature=0.3,
                )
                
                logger.info(f"[LLMDecomposer] LLM response received (length: {len(response) if response else 0})")
                logger.debug(f"[LLMDecomposer] LLM raw response: {response[:500] if response else 'None'}")
                
                parsed = self._parse_llm_response(response)
                
                if parsed:
                    return self._convert_to_result(parsed)
                else:
                    last_error = ValueError("Failed to parse LLM response as valid JSON")
                    logger.warning(f"[LLMDecomposer] Attempt {attempt + 1} failed: Could not parse response")
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[LLMDecomposer] Attempt {attempt + 1} failed: {e}"
                )
        
        logger.error(f"[LLMDecomposer] All attempts failed: {last_error}")
        
        return self._fallback_decomposition(instruction, context, available_agents)
    
    def _parse_llm_response(self, response: str) -> Optional[LLMDecompositionResult]:
        if not response:
            logger.warning("[LLMDecomposer] Empty response from LLM")
            return None
        
        json_str = response.strip()
        
        logger.debug(f"[LLMDecomposer] Raw response (first 200 chars): {json_str[:200]}")
        
        if "```json" in json_str:
            start = json_str.find("```json") + 7
            end = json_str.find("```", start)
            if end > start:
                json_str = json_str[start:end].strip()
        elif "```" in json_str:
            start = json_str.find("```") + 3
            end = json_str.find("```", start)
            if end > start:
                json_str = json_str[start:end].strip()
        
        json_str = json_str.strip()
        
        if json_str.startswith("{") and json_str.endswith("}"):
            pass
        elif "{" in json_str:
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if end > start:
                json_str = json_str[start:end]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"[LLMDecomposer] JSON parse error: {e}")
            logger.warning(f"[LLMDecomposer] Attempted to parse: {json_str[:500]}")
            return None
        
        if not isinstance(data, dict):
            logger.warning(f"[LLMDecomposer] Parsed data is not a dict: {type(data)}")
            return None
        
        try:
            complexity_str = data.get("complexity", "simple").lower()
            complexity = TaskComplexity(complexity_str)
        except ValueError:
            complexity = TaskComplexity.STANDARD
        
        use_team_mode = data.get("use_team_mode", False)
        
        subtasks = []
        for st_data in data.get("subtasks", [])[:MAX_SUBTASKS]:
            if not isinstance(st_data, dict):
                continue
            subtask = SubTaskSpec(
                instruction=st_data.get("instruction", ""),
                task_type=st_data.get("task_type", "analysis"),
                assigned_agent=st_data.get("assigned_agent"),
                dependencies=st_data.get("dependencies", []),
                metadata=st_data.get("metadata", {}),
            )
            subtasks.append(subtask)
        
        logger.info(f"[LLMDecomposer] Successfully parsed LLM response - Complexity: {complexity.value}, Team Mode: {use_team_mode}, Subtasks: {len(subtasks)}")
        
        return LLMDecompositionResult(
            complexity=complexity,
            use_team_mode=use_team_mode,
            subtasks=subtasks,
            reasoning=data.get("reasoning", ""),
        )
    
    def _convert_to_result(self, parsed: LLMDecompositionResult) -> DecompositionResult:
        subtasks_data = []
        
        for i, st in enumerate(parsed.subtasks):
            subtask_dict = {
                "instruction": st.instruction,
                "task_type": st.task_type,
                "assigned_agent": st.assigned_agent,
                "dependencies": st.dependencies,
                "metadata": {
                    **st.metadata,
                    "index": i,
                },
            }
            subtasks_data.append(subtask_dict)
        
        return DecompositionResult(
            complexity=parsed.complexity,
            use_team_mode=parsed.use_team_mode,
            subtasks=subtasks_data,
            reasoning=parsed.reasoning,
        )
    
    def _fallback_decomposition(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
    ) -> DecompositionResult:
        from ..rule.semantic_analyzer import SemanticAnalyzer
        from ..rule.agent_selector import AgentSelector
        
        logger.info("[LLMDecomposer] Using fallback decomposition (rule-based)")
        
        semantic_analyzer = SemanticAnalyzer()
        agent_selector = AgentSelector()
        
        features = semantic_analyzer.analyze(instruction, context)
        complexity = semantic_analyzer.estimate_complexity(instruction, context)
        use_team_mode = semantic_analyzer.should_use_team_mode(features, context)
        
        if not use_team_mode:
            return DecompositionResult(
                complexity=complexity,
                use_team_mode=False,
                subtasks=[],
                reasoning="Task is simple enough for single agent execution.",
            )
        
        subtasks = []
        topics = features.topics[:MAX_SUBTASKS]
        
        for i, topic in enumerate(topics):
            agent = agent_selector.select_best_agent("analysis", available_agents)
            subtasks.append({
                "instruction": f"Analyze and gather information about: {topic}",
                "assigned_agent": agent,
                "task_type": "analysis",
                "dependencies": [],
                "metadata": {"topic_index": i, "topic": topic},
            })
        
        if len(subtasks) > 1:
            synthesis_agent = agent_selector.select_best_agent("synthesis", available_agents)
            subtasks.append({
                "instruction": "Synthesize the results from all subtasks into a comprehensive response",
                "assigned_agent": synthesis_agent,
                "task_type": "synthesis",
                "dependencies": list(range(len(subtasks))),
                "metadata": {"is_synthesis": True},
            })
        
        return DecompositionResult(
            complexity=complexity,
            use_team_mode=True,
            subtasks=subtasks,
            reasoning=f"Fallback decomposition based on {len(topics)} topics.",
        )
    
    def clear_cache(self) -> None:
        self._cache.clear()
        logger.info("[LLMDecomposer] Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        valid_entries = sum(
            1 for entry in self._cache.values()
            if not entry.is_expired()
        )
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "max_size": self._max_cache_size,
        }
