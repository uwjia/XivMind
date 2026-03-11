import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    SEARCH = "search"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    WRITING = "writing"
    TRANSLATION = "translation"
    COMPARISON = "comparison"
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"


@dataclass
class AgentProfile:
    id: str
    name: str
    capabilities: Set[AgentCapability]
    specializations: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 3
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        return capability in self.capabilities
    
    def has_any_capability(self, capabilities: List[AgentCapability]) -> bool:
        return any(cap in self.capabilities for cap in capabilities)
    
    def capability_score(self, required: List[AgentCapability]) -> float:
        if not required:
            return 0.0
        matched = sum(1 for cap in required if cap in self.capabilities)
        return matched / len(required)


DEFAULT_AGENT_PROFILES = [
    AgentProfile(
        id="research-agent",
        name="Research Agent",
        capabilities={
            AgentCapability.SEARCH,
            AgentCapability.EXTRACTION,
            AgentCapability.SUMMARIZATION,
        },
        specializations=["literature_search", "paper_discovery", "citation_analysis"],
        priority=1,
    ),
    AgentProfile(
        id="analysis-agent",
        name="Analysis Agent",
        capabilities={
            AgentCapability.ANALYSIS,
            AgentCapability.COMPARISON,
            AgentCapability.EXTRACTION,
            AgentCapability.SYNTHESIS,
        },
        specializations=["paper_analysis", "method_comparison", "result_extraction"],
        priority=2,
    ),
    AgentProfile(
        id="writer-agent",
        name="Writer Agent",
        capabilities={
            AgentCapability.WRITING,
            AgentCapability.SUMMARIZATION,
            AgentCapability.TRANSLATION,
            AgentCapability.SYNTHESIS,
        },
        specializations=["report_writing", "summary_generation", "translation"],
        priority=1,
    ),
]


TASK_TYPE_CAPABILITIES: Dict[str, List[AgentCapability]] = {
    "search": [AgentCapability.SEARCH, AgentCapability.EXTRACTION],
    "analysis": [AgentCapability.ANALYSIS, AgentCapability.EXTRACTION],
    "comparison": [AgentCapability.COMPARISON, AgentCapability.ANALYSIS],
    "review": [AgentCapability.SEARCH, AgentCapability.ANALYSIS, AgentCapability.SYNTHESIS],
    "synthesis": [AgentCapability.SYNTHESIS, AgentCapability.WRITING],
    "writing": [AgentCapability.WRITING, AgentCapability.SUMMARIZATION],
    "translation": [AgentCapability.TRANSLATION, AgentCapability.WRITING],
    "summarization": [AgentCapability.SUMMARIZATION, AgentCapability.EXTRACTION],
}


class AgentSelector:
    def __init__(self):
        self._agents: Dict[str, AgentProfile] = {}
        self._task_assignments: Dict[str, List[str]] = {}
        
        for profile in DEFAULT_AGENT_PROFILES:
            self.register_agent(profile)
    
    def register_agent(self, profile: AgentProfile) -> None:
        self._agents[profile.id] = profile
        logger.info(f"[AgentSelector] Registered agent: {profile.id} with capabilities: {[c.value for c in profile.capabilities]}")
    
    def unregister_agent(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[AgentProfile]:
        return list(self._agents.values())
    
    def get_available_agents(self) -> List[str]:
        return list(self._agents.keys())
    
    def select_best_agent(
        self,
        task_type: str,
        available_agents: Optional[List[str]] = None,
        requirements: Optional[List[AgentCapability]] = None,
    ) -> str:
        required_capabilities = requirements or TASK_TYPE_CAPABILITIES.get(task_type, [])
        
        candidates = self._get_candidates(available_agents)
        
        if not candidates:
            return self._get_default_agent(task_type)
        
        scored_candidates = []
        for agent_id in candidates:
            profile = self._agents.get(agent_id)
            if profile:
                score = self._calculate_agent_score(profile, required_capabilities, task_type)
                scored_candidates.append((agent_id, score))
        
        if not scored_candidates:
            return self._get_default_agent(task_type)
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates[0][0]
    
    def select_agents_for_parallel(
        self,
        task_type: str,
        count: int,
        available_agents: Optional[List[str]] = None,
    ) -> List[str]:
        candidates = self._get_candidates(available_agents)
        
        if not candidates:
            default = self._get_default_agent(task_type)
            return [default] * min(count, 1)
        
        required_capabilities = TASK_TYPE_CAPABILITIES.get(task_type, [])
        
        scored_candidates = []
        for agent_id in candidates:
            profile = self._agents.get(agent_id)
            if profile:
                score = self._calculate_agent_score(profile, required_capabilities, task_type)
                scored_candidates.append((agent_id, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [agent_id for agent_id, _ in scored_candidates[:count]]
    
    def _get_candidates(self, available_agents: Optional[List[str]]) -> List[str]:
        if available_agents:
            return [aid for aid in available_agents if aid in self._agents]
        return list(self._agents.keys())
    
    def _calculate_agent_score(
        self,
        profile: AgentProfile,
        required_capabilities: List[AgentCapability],
        task_type: str,
    ) -> float:
        score = 0.0
        
        if required_capabilities:
            capability_score = profile.capability_score(required_capabilities)
            score += capability_score * 0.6
        
        if task_type in profile.specializations:
            score += 0.3
        
        score += profile.priority * 0.02
        
        return score
    
    def _get_default_agent(self, task_type: str) -> str:
        default_mapping = {
            "search": "research-agent",
            "analysis": "analysis-agent",
            "comparison": "analysis-agent",
            "review": "research-agent",
            "synthesis": "analysis-agent",
            "writing": "writer-agent",
            "translation": "writer-agent",
            "summarization": "writer-agent",
        }
        return default_mapping.get(task_type, "research-agent")
    
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        profile = self._agents.get(agent_id)
        if profile:
            return [cap.value for cap in profile.capabilities]
        return []
    
    def find_agents_by_capability(
        self,
        capability: AgentCapability,
        available_agents: Optional[List[str]] = None,
    ) -> List[str]:
        candidates = self._get_candidates(available_agents)
        
        matching_agents = []
        for agent_id in candidates:
            profile = self._agents.get(agent_id)
            if profile and profile.has_capability(capability):
                matching_agents.append(agent_id)
        
        return matching_agents
    
    def get_recommended_agent_count(
        self,
        task_type: str,
        complexity_score: float,
        topic_count: int,
    ) -> int:
        base_count = 1
        
        if task_type == "comparison":
            base_count = max(2, topic_count)
        elif task_type == "review":
            base_count = min(3, max(2, topic_count))
        elif task_type == "analysis":
            base_count = min(3, max(1, topic_count))
        
        if complexity_score >= 0.7:
            base_count = min(base_count + 1, 5)
        elif complexity_score >= 0.5:
            base_count = min(base_count + 1, 4)
        
        return min(base_count, 5)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agents": {
                agent_id: {
                    "id": profile.id,
                    "name": profile.name,
                    "capabilities": [cap.value for cap in profile.capabilities],
                    "specializations": profile.specializations,
                    "priority": profile.priority,
                }
                for agent_id, profile in self._agents.items()
            },
            "task_type_capabilities": {
                task_type: [cap.value for cap in caps]
                for task_type, caps in TASK_TYPE_CAPABILITIES.items()
            },
        }
