import re
import logging
from typing import Dict, Any, List, Optional

from .types import (
    TaskComplexity,
    DecompositionResult,
    MAX_SUBTASKS,
)
from .decomposition import (
    LLMDecomposer,
    SemanticAnalyzer,
    AgentSelector,
    config_manager,
)
from .decomposition.rule.semantic_analyzer import SemanticFeatures

logger = logging.getLogger(__name__)


class TaskDecomposer:
    """Task decomposer for analyzing and breaking down complex tasks.
    
    This class integrates multiple decomposition strategies:
    1. LLM-based intelligent decomposition (primary)
    2. Semantic analysis for feature extraction
    3. Rule-based decomposition (fallback)
    4. Dynamic agent selection
    """
    
    def __init__(
        self,
        use_llm: bool = True,
        cache_enabled: bool = True,
    ):
        self._cache: Dict[str, DecompositionResult] = {}
        self._llm_decomposer: Optional[LLMDecomposer] = None
        self._semantic_analyzer: Optional[SemanticAnalyzer] = None
        self._agent_selector: Optional[AgentSelector] = None
        self._use_llm = use_llm
        self._cache_enabled = cache_enabled
    
    @property
    def llm_decomposer(self) -> LLMDecomposer:
        if self._llm_decomposer is None:
            self._llm_decomposer = LLMDecomposer()
        return self._llm_decomposer
    
    @property
    def semantic_analyzer(self) -> SemanticAnalyzer:
        if self._semantic_analyzer is None:
            self._semantic_analyzer = SemanticAnalyzer()
        return self._semantic_analyzer
    
    @property
    def agent_selector(self) -> AgentSelector:
        if self._agent_selector is None:
            self._agent_selector = AgentSelector()
        return self._agent_selector
    
    def analyze_complexity(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskComplexity:
        features = self.semantic_analyzer.analyze(instruction, context)
        return self.semantic_analyzer.estimate_complexity(instruction, context)
    
    def should_use_team_mode(
        self,
        complexity: TaskComplexity,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if complexity == TaskComplexity.SIMPLE:
            return False
        
        if complexity == TaskComplexity.HIGH:
            return True
        
        features = self.semantic_analyzer.analyze(instruction, context)
        return self.semantic_analyzer.should_use_team_mode(features, context)
    
    def decompose(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
    ) -> DecompositionResult:
        logger.info("[TaskDecomposer] Strategy: Rule-based decomposition (sync interface)")
        return self._decompose_sync(instruction, context, available_agents)
    
    async def decompose_async(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        config = config_manager.get_config()
        
        if config.use_llm and self._use_llm:
            logger.info("[TaskDecomposer] Strategy: LLM-based decomposition (async interface)")
            return await self._decompose_with_llm(
                instruction, context, available_agents, provider, model
            )
        
        logger.info("[TaskDecomposer] Strategy: Rule-based decomposition (LLM disabled)")
        return self._decompose_sync(instruction, context, available_agents)
    
    async def _decompose_with_llm(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> DecompositionResult:
        logger.info("[TaskDecomposer] Attempting LLM-based decomposition...")
        try:
            result = await self.llm_decomposer.decompose_async(
                instruction=instruction,
                context=context,
                available_agents=available_agents,
                provider=provider,
                model=model,
            )
            
            logger.info(f"[TaskDecomposer] LLM decomposition successful - Complexity: {result.complexity.value}, Team Mode: {result.use_team_mode}, Subtasks: {len(result.subtasks)}")
            
            if result.use_team_mode and result.subtasks:
                result = self._enhance_subtasks(result, available_agents)
            
            return result
            
        except Exception as e:
            logger.warning(f"[TaskDecomposer] LLM decomposition failed: {e}")
            
            config = config_manager.get_config()
            if config.llm_fallback_enabled:
                logger.info("[TaskDecomposer] Falling back to rule-based decomposition")
                return self._decompose_sync(instruction, context, available_agents)
            
            raise
    
    def _decompose_sync(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
    ) -> DecompositionResult:
        logger.info("[TaskDecomposer] Using rule-based decomposition...")
        
        features = self.semantic_analyzer.analyze(instruction, context)
        complexity = self.semantic_analyzer.estimate_complexity(instruction, context)
        
        logger.info(f"[TaskDecomposer] Semantic analysis - Topics: {features.topics[:3]}, Task Types: {features.task_types[:2]}, Complexity Score: {features.complexity_score:.2f}")
        
        use_team_mode = self.semantic_analyzer.should_use_team_mode(features, context)
        
        if not use_team_mode:
            logger.info(f"[TaskDecomposer] Task determined as simple - Complexity: {complexity.value}, Team Mode: False")
            return DecompositionResult(
                complexity=complexity,
                use_team_mode=False,
                subtasks=[],
                reasoning="Task is simple enough for single agent execution.",
            )
        
        subtasks = self._generate_subtasks(
            instruction=instruction,
            context=context,
            available_agents=available_agents,
            features=features,
        )
        
        config = config_manager.get_config()
        min_subtasks = config.min_subtasks_for_team
        
        if len(subtasks) < min_subtasks:
            logger.info(f"[TaskDecomposer] Too few subtasks ({len(subtasks)} < {min_subtasks}), using single agent")
            return DecompositionResult(
                complexity=complexity,
                use_team_mode=False,
                subtasks=[],
                reasoning="Decomposition resulted in fewer than minimum subtasks. Using single agent.",
            )
        
        logger.info(f"[TaskDecomposer] Rule-based decomposition complete - {len(subtasks)} subtasks generated")
        reasoning = self._generate_reasoning(complexity, len(subtasks), instruction, features)
        
        return DecompositionResult(
            complexity=complexity,
            use_team_mode=True,
            subtasks=subtasks[:config.max_subtasks],
            reasoning=reasoning,
        )
    
    def _generate_subtasks(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        available_agents: Optional[List[str]] = None,
        features: Optional[SemanticFeatures] = None,
    ) -> List[Dict[str, Any]]:
        if features is None:
            features = self.semantic_analyzer.analyze(instruction, context)
        
        matched_rule = config_manager.match_rule(instruction)
        
        if matched_rule:
            logger.info(f"[TaskDecomposer] Matched rule: {matched_rule.name} (task_type: {matched_rule.task_type})")
            return self._decompose_by_rule(
                instruction, context, available_agents, features, matched_rule
            )
        
        task_types = features.task_types
        primary_type = task_types[0] if task_types else "analysis"
        
        logger.info(f"[TaskDecomposer] No rule matched, using task type: {primary_type}")
        
        if primary_type == "comparison":
            return self._decompose_comparison(instruction, context, available_agents, features)
        elif primary_type == "review":
            return self._decompose_review(instruction, context, available_agents, features)
        elif primary_type == "analysis":
            return self._decompose_analysis(instruction, context, available_agents, features)
        else:
            return self._decompose_general(instruction, context, available_agents, features)
    
    def _decompose_by_rule(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
        rule,
    ) -> List[Dict[str, Any]]:
        subtasks = []
        task_type = rule.task_type
        
        if task_type == "comparison":
            topics = features.topics if features.topics else self._extract_comparison_topics(instruction)
            subtasks = self._create_comparison_subtasks(topics, available_agents)
        elif task_type == "review":
            aspects = features.topics if features.topics else self._extract_review_aspects(instruction)
            subtasks = self._create_review_subtasks(aspects, available_agents)
        elif task_type == "analysis":
            subtasks = self._create_analysis_subtasks(instruction, context, available_agents, features)
        else:
            subtasks = self._create_general_subtasks(instruction, available_agents, features)
        
        if rule.requires_synthesis and len(subtasks) > 1:
            subtasks = self._add_synthesis_subtask(subtasks, instruction, available_agents)
        
        return subtasks[:rule.max_subtasks]
    
    def _decompose_comparison(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        topics = features.topics if features.topics else self._extract_comparison_topics(instruction)
        subtasks = self._create_comparison_subtasks(topics, available_agents)
        
        if len(subtasks) > 1:
            subtasks = self._add_synthesis_subtask(subtasks, instruction, available_agents)
        
        return subtasks
    
    def _decompose_review(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        aspects = features.topics if features.topics else self._extract_review_aspects(instruction)
        subtasks = self._create_review_subtasks(aspects, available_agents)
        
        if len(subtasks) > 1:
            subtasks = self._add_synthesis_subtask(subtasks, instruction, available_agents)
        
        return subtasks
    
    def _decompose_analysis(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        return self._create_analysis_subtasks(instruction, context, available_agents, features)
    
    def _decompose_general(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        return self._create_general_subtasks(instruction, available_agents, features)
    
    def _create_comparison_subtasks(
        self,
        topics: List[str],
        available_agents: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        subtasks = []
        
        if len(topics) >= 2:
            for i, topic in enumerate(topics[:MAX_SUBTASKS - 1]):
                agent = self.agent_selector.select_best_agent("analysis", available_agents)
                subtasks.append({
                    "instruction": f"Analyze and gather information about: {topic}",
                    "assigned_agent": agent,
                    "task_type": "analysis",
                    "dependencies": [],
                    "metadata": {"topic_index": i, "topic": topic},
                })
        else:
            agent = self.agent_selector.select_best_agent("analysis", available_agents)
            subtasks.append({
                "instruction": "Analyze the comparison topics",
                "assigned_agent": agent,
                "task_type": "analysis",
                "dependencies": [],
            })
        
        return subtasks
    
    def _create_review_subtasks(
        self,
        aspects: List[str],
        available_agents: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        subtasks = []
        
        for i, aspect in enumerate(aspects[:MAX_SUBTASKS - 1]):
            agent = self.agent_selector.select_best_agent("search", available_agents)
            subtasks.append({
                "instruction": f"Search and collect papers related to: {aspect}",
                "assigned_agent": agent,
                "task_type": "search",
                "dependencies": [],
                "metadata": {"aspect_index": i, "aspect": aspect},
            })
        
        return subtasks
    
    def _create_analysis_subtasks(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]],
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        subtasks = []
        
        paper_ids = context.get("paper_ids", []) if context else []
        
        if paper_ids and len(paper_ids) >= 2:
            for i, paper_id in enumerate(paper_ids[:MAX_SUBTASKS - 1]):
                agent = self.agent_selector.select_best_agent("analysis", available_agents)
                subtasks.append({
                    "instruction": f"Analyze paper {paper_id} in detail",
                    "assigned_agent": agent,
                    "task_type": "analysis",
                    "paper_ids": [paper_id],
                    "dependencies": [],
                    "metadata": {"paper_index": i, "paper_id": paper_id},
                })
            
            subtasks = self._add_synthesis_subtask(subtasks, instruction, available_agents)
        else:
            agent = self.agent_selector.select_best_agent("analysis", available_agents)
            subtasks.append({
                "instruction": instruction,
                "assigned_agent": agent,
                "task_type": "analysis",
                "dependencies": [],
            })
        
        return subtasks
    
    def _create_general_subtasks(
        self,
        instruction: str,
        available_agents: Optional[List[str]],
        features: SemanticFeatures,
    ) -> List[Dict[str, Any]]:
        subtasks = []
        
        search_agent = self.agent_selector.select_best_agent("search", available_agents)
        subtasks.append({
            "instruction": f"Search for relevant information: {instruction}",
            "assigned_agent": search_agent,
            "task_type": "search",
            "dependencies": [],
        })
        
        analysis_agent = self.agent_selector.select_best_agent("analysis", available_agents)
        subtasks.append({
            "instruction": "Analyze the search results and extract key insights",
            "assigned_agent": analysis_agent,
            "task_type": "analysis",
            "dependencies": [0],
        })
        
        return subtasks
    
    def _add_synthesis_subtask(
        self,
        subtasks: List[Dict[str, Any]],
        instruction: str,
        available_agents: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        if not subtasks:
            return subtasks
        
        synthesis_agent = self.agent_selector.select_best_agent("synthesis", available_agents)
        
        synthesis_subtask = {
            "instruction": "Synthesize the results from all subtasks into a comprehensive response",
            "assigned_agent": synthesis_agent,
            "task_type": "synthesis",
            "dependencies": list(range(len(subtasks))),
            "metadata": {"is_synthesis": True},
        }
        
        subtasks.append(synthesis_subtask)
        return subtasks
    
    def _enhance_subtasks(
        self,
        result: DecompositionResult,
        available_agents: Optional[List[str]],
    ) -> DecompositionResult:
        enhanced_subtasks = []
        
        for subtask in result.subtasks:
            if not subtask.get("assigned_agent"):
                task_type = subtask.get("task_type", "analysis")
                subtask["assigned_agent"] = self.agent_selector.select_best_agent(
                    task_type, available_agents
                )
            enhanced_subtasks.append(subtask)
        
        result.subtasks = enhanced_subtasks
        return result
    
    def _extract_comparison_topics(self, instruction: str) -> List[str]:
        patterns = [
            r"compare\s+(.+?)\s+(?:and|with|vs|versus)\s+(.+?)(?:\.|$)",
            r"(.+?)\s+(?:vs|versus)\s+(.+?)(?:\.|$)",
            r"比较\s+(.+?)\s+和\s+(.+?)(?:。|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        
        return ["Topic A", "Topic B"]
    
    def _extract_review_aspects(self, instruction: str) -> List[str]:
        aspects = []
        
        aspect_patterns = [
            r"including\s+(.+?)(?:\.|$)",
            r"covering\s+(.+?)(?:\.|$)",
            r"about\s+(.+?)(?:\.|$)",
            r"on\s+(.+?)(?:\.|$)",
        ]
        
        for pattern in aspect_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                aspects_str = match.group(1)
                aspects = [a.strip() for a in re.split(r"[,、]", aspects_str) if a.strip()]
                break
        
        if not aspects:
            aspects = ["main topic"]
        
        return aspects[:MAX_SUBTASKS]
    
    def _generate_reasoning(
        self,
        complexity: TaskComplexity,
        subtask_count: int,
        instruction: str,
        features: Optional[SemanticFeatures] = None,
    ) -> str:
        parts = [
            f"Task complexity assessed as {complexity.value}.",
            f"Decomposed into {subtask_count} subtasks.",
        ]
        
        if features:
            if features.topics:
                parts.append(f"Topics identified: {', '.join(features.topics[:3])}.")
            if features.task_types:
                parts.append(f"Task types: {', '.join(features.task_types[:2])}.")
        
        return " ".join(parts)
