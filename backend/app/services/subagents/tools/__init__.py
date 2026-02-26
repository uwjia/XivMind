import logging

from .base import ToolProvider
from .registry import ToolRegistry
from .types import ToolCategory, ToolParameter, ToolDefinition, ToolResult
from .implementations import SearchPapersTool, GetPaperDetailsTool, ExecuteSkillTool

logger = logging.getLogger(__name__)

__all__ = [
    "ToolProvider",
    "ToolRegistry",
    "ToolCategory",
    "ToolParameter",
    "ToolDefinition",
    "ToolResult",
    "SearchPapersTool",
    "GetPaperDetailsTool",
    "ExecuteSkillTool",
    "register_default_tools",
]


def register_default_tools():
    """Register all default built-in tools."""
    ToolRegistry.register(SearchPapersTool)
    ToolRegistry.register(GetPaperDetailsTool)
    ToolRegistry.register(ExecuteSkillTool)
    logger.info("Registered default tools: search_papers, get_paper_details, execute_skill")
