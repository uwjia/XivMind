import logging
from typing import Dict, Any, List, Optional, Type, Callable

from .types import ToolDefinition, ToolResult, ToolCategory
from .base import ToolProvider

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing tool providers."""
    
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, ToolProvider] = {}
    _handlers: Dict[str, Callable] = {}
    
    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, tool: Type[ToolProvider]) -> None:
        """Register a tool provider class."""
        instance = tool()
        tool_id = instance.id
        
        if tool_id in cls._tools:
            logger.warning(f"Tool '{tool_id}' already registered, overwriting")
        
        cls._tools[tool_id] = instance
        logger.info(f"Registered tool: {tool_id}")
    
    @classmethod
    def register_handler(cls, tool_id: str, handler: Callable) -> None:
        """Register a handler function for a tool."""
        cls._handlers[tool_id] = handler
        logger.info(f"Registered handler for tool: {tool_id}")
    
    @classmethod
    def unregister(cls, tool_id: str) -> bool:
        """Unregister a tool."""
        if tool_id in cls._tools:
            del cls._tools[tool_id]
            logger.info(f"Unregistered tool: {tool_id}")
            return True
        return False
    
    @classmethod
    def get(cls, tool_id: str) -> Optional[ToolProvider]:
        """Get a tool by ID."""
        return cls._tools.get(tool_id)
    
    @classmethod
    def get_handler(cls, tool_id: str) -> Optional[Callable]:
        """Get a handler by tool ID."""
        return cls._handlers.get(tool_id)
    
    @classmethod
    def exists(cls, tool_id: str) -> bool:
        """Check if a tool exists."""
        return tool_id in cls._tools
    
    @classmethod
    def get_all(cls) -> List[ToolProvider]:
        """Get all registered tools."""
        return list(cls._tools.values())
    
    @classmethod
    def get_definitions(cls) -> List[ToolDefinition]:
        """Get all tool definitions."""
        return [tool.get_definition() for tool in cls._tools.values()]
    
    @classmethod
    def get_by_category(cls, category: ToolCategory) -> List[ToolProvider]:
        """Get tools by category."""
        return [
            tool for tool in cls._tools.values()
            if tool.category == category
        ]
    
    @classmethod
    def to_dict_list(cls) -> List[Dict[str, Any]]:
        """Get all tools as dictionary list."""
        return [tool.to_dict() for tool in cls._tools.values()]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools."""
        cls._tools.clear()
        cls._handlers.clear()
        logger.info("Cleared all registered tools")


tool_registry = ToolRegistry()


def register_tool(tool: Type[ToolProvider]) -> Type[ToolProvider]:
    """Decorator to register a tool provider."""
    ToolRegistry.register(tool)
    return tool
