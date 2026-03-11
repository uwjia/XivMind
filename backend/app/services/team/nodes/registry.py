from __future__ import annotations

from typing import Dict, Type, List, Optional

from .base import BaseNode


class NodeRegistry:
    _registry: Dict[str, Type[BaseNode]] = {}
    
    @classmethod
    def register(cls, node_type: str):
        def decorator(node_class: Type[BaseNode]) -> Type[BaseNode]:
            cls._registry[node_type] = node_class
            return node_class
        return decorator
    
    @classmethod
    def create(cls, node_type: str, node_id: str, config: Dict[str, Any]) -> BaseNode:
        node_class = cls._registry.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")
        return node_class(node_id, config)
    
    @classmethod
    def get_node_class(cls, node_type: str) -> Optional[Type[BaseNode]]:
        return cls._registry.get(node_type)
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, node_type: str) -> bool:
        return node_type in cls._registry
    
    @classmethod
    def clear(cls):
        cls._registry.clear()
