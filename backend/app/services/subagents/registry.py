import logging
from typing import Dict, List, Optional, Type
from pathlib import Path

from .base import SubAgentBase
from .types import SubAgentConfig
from .loader import SubAgentLoader

logger = logging.getLogger(__name__)


class DynamicSubAgent(SubAgentBase):
    """A SubAgent dynamically loaded from AGENT.md file."""
    
    async def execute(self, task):
        from .executor import SubAgentExecutor
        
        executor = SubAgentExecutor()
        return await executor.execute(self, task)


class SubAgentRegistry:
    """Registry for all available SubAgents."""
    
    _instance = None
    _agents: Dict[str, SubAgentBase] = {}
    _dynamic_agents: Dict[str, DynamicSubAgent] = {}
    _agents_dir: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, agent_class: Type[SubAgentBase]) -> Type[SubAgentBase]:
        agent = agent_class.__new__(agent_class)
        agent.__init__(agent.config if hasattr(agent, '_config') else SubAgentConfig(
            id=agent_class.__name__.lower().replace('agent', '-agent'),
            name=agent_class.__name__,
        ))
        cls._agents[agent.id] = agent
        logger.info(f"Registered SubAgent: {agent.id}")
        return agent_class
    
    @classmethod
    def register_instance(cls, agent: SubAgentBase) -> None:
        cls._agents[agent.id] = agent
        logger.info(f"Registered SubAgent instance: {agent.id}")
    
    @classmethod
    def register_dynamic(cls, config_data: Dict) -> Optional[DynamicSubAgent]:
        try:
            config = SubAgentConfig(**config_data)
        except Exception as e:
            logger.error(f"Invalid SubAgent config: {e}")
            return None
        
        agent = DynamicSubAgent(config)
        cls._agents[agent.id] = agent
        cls._dynamic_agents[agent.id] = agent
        logger.info(f"Registered dynamic SubAgent: {agent.id}")
        return agent
    
    @classmethod
    def unregister(cls, agent_id: str) -> bool:
        if agent_id in cls._agents:
            del cls._agents[agent_id]
            if agent_id in cls._dynamic_agents:
                del cls._dynamic_agents[agent_id]
            logger.info(f"Unregistered SubAgent: {agent_id}")
            return True
        return False
    
    @classmethod
    def get(cls, agent_id: str) -> Optional[SubAgentBase]:
        return cls._agents.get(agent_id)
    
    @classmethod
    def get_all(cls) -> List[SubAgentBase]:
        return list(cls._agents.values())
    
    @classmethod
    def get_available(cls) -> List[SubAgentBase]:
        return [agent for agent in cls._agents.values() if agent.is_available()]
    
    @classmethod
    def get_by_skill(cls, skill_id: str) -> List[SubAgentBase]:
        return [
            agent for agent in cls._agents.values()
            if agent.has_skill(skill_id) and agent.is_available()
        ]
    
    @classmethod
    def get_by_tool(cls, tool_name: str) -> List[SubAgentBase]:
        return [
            agent for agent in cls._agents.values()
            if agent.has_tool(tool_name) and agent.is_available()
        ]
    
    @classmethod
    def load_dynamic_agents(cls, agents_dir: str) -> int:
        loader = SubAgentLoader(agents_dir)
        configs = loader.load_all_agents()
        
        loaded_count = 0
        for config in configs:
            agent = cls.register_dynamic(config)
            if agent:
                loaded_count += 1
        
        cls._agents_dir = Path(agents_dir)
        return loaded_count
    
    @classmethod
    def reload_dynamic_agents(cls) -> Dict[str, int]:
        dynamic_ids = list(cls._dynamic_agents.keys())
        for agent_id in dynamic_ids:
            cls.unregister(agent_id)
        
        loaded = 0
        if cls._agents_dir:
            loaded = cls.load_dynamic_agents(str(cls._agents_dir))
        
        return {
            "unloaded": len(dynamic_ids),
            "loaded": loaded
        }
    
    @classmethod
    def reload_agent(cls, agent_id: str) -> bool:
        if cls._agents_dir:
            agent_dir = cls._agents_dir / agent_id
            if agent_dir.exists():
                loader = SubAgentLoader(str(cls._agents_dir))
                config = loader.load_agent(agent_dir)
                if config:
                    cls.unregister(agent_id)
                    cls.register_dynamic(config)
                    return True
        return False
    
    @classmethod
    def is_dynamic(cls, agent_id: str) -> bool:
        return agent_id in cls._dynamic_agents
    
    @classmethod
    def get_dynamic_agents(cls) -> List[DynamicSubAgent]:
        return list(cls._dynamic_agents.values())
    
    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()
        cls._dynamic_agents.clear()
    
    @classmethod
    def count(cls) -> int:
        return len(cls._agents)
    
    @classmethod
    def exists(cls, agent_id: str) -> bool:
        return agent_id in cls._agents


from typing import Dict as _Dict
