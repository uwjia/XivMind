from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.services.subagents import subagent_manager
from app.models import (
    SubAgentInfo,
    SubAgentListResponse,
    SubAgentExecuteRequest,
    SubAgentExecuteResponse,
    SubAgentCreateRequest,
    SubAgentSaveRequest,
    SubAgentReloadResponse,
)

router = APIRouter(prefix="/subagents", tags=["subagents"])


@router.get("", response_model=SubAgentListResponse)
async def list_subagents():
    """
    List all available SubAgents.
    
    Returns list of all registered SubAgents with their configurations.
    """
    agents = subagent_manager.get_all_agents()
    return SubAgentListResponse(
        agents=[SubAgentInfo(**agent) for agent in agents],
        total=len(agents)
    )


@router.get("/{agent_id}", response_model=SubAgentInfo)
async def get_subagent(agent_id: str):
    """
    Get details of a specific SubAgent.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    agent = subagent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"SubAgent '{agent_id}' not found")
    return SubAgentInfo(**agent)


@router.get("/{agent_id}/raw")
async def get_subagent_raw(agent_id: str):
    """
    Get raw AGENT.md content for a SubAgent.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    content = subagent_manager.get_agent_raw(agent_id)
    if content is None:
        raise HTTPException(status_code=404, detail=f"SubAgent '{agent_id}' not found or has no raw content")
    return {"agent_id": agent_id, "content": content}


@router.post("", response_model=SubAgentInfo)
async def create_subagent(request: SubAgentCreateRequest):
    """
    Create a new SubAgent.
    
    Creates a new SubAgent from the provided configuration.
    """
    result = subagent_manager.create_agent(
        agent_id=request.id,
        name=request.name,
        description=request.description or "",
        skills=request.skills,
        tools=request.tools,
        system_prompt=request.system_prompt or "",
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create SubAgent"))
    
    agent = subagent_manager.get_agent(request.id)
    return SubAgentInfo(**agent)


@router.put("/{agent_id}", response_model=SubAgentInfo)
async def save_subagent(agent_id: str, request: SubAgentSaveRequest):
    """
    Save and reload a SubAgent's configuration.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    result = subagent_manager.save_agent(agent_id, request.content)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to save SubAgent"))
    
    agent = subagent_manager.get_agent(agent_id)
    return SubAgentInfo(**agent)


@router.delete("/{agent_id}")
async def delete_subagent(agent_id: str):
    """
    Delete a SubAgent.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    result = subagent_manager.delete_agent(agent_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete SubAgent"))
    
    return {"success": True, "message": f"SubAgent '{agent_id}' deleted"}


@router.post("/reload", response_model=SubAgentReloadResponse)
async def reload_all_subagents():
    """
    Reload all dynamic SubAgents from the configuration directory.
    """
    result = subagent_manager.reload_agents()
    return SubAgentReloadResponse(**result)


@router.post("/{agent_id}/reload", response_model=SubAgentReloadResponse)
async def reload_subagent(agent_id: str):
    """
    Reload a specific SubAgent.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    result = subagent_manager.reload_agent(agent_id)
    return SubAgentReloadResponse(**result)


@router.post("/{agent_id}/execute", response_model=SubAgentExecuteResponse)
async def execute_subagent(agent_id: str, request: SubAgentExecuteRequest):
    """
    Execute a task with a SubAgent.
    
    Args:
        agent_id: The unique identifier of the SubAgent
    """
    result = await subagent_manager.execute_agent(
        agent_id=agent_id,
        instruction=request.instruction,
        paper_ids=request.paper_ids,
        context=request.context,
        provider=request.provider,
        model=request.model,
        max_turns=request.max_turns,
    )
    
    return SubAgentExecuteResponse(
        task_id=result.task_id,
        agent_id=result.agent_id,
        status=result.status.value if hasattr(result.status, 'value') else result.status,
        output=result.output,
        messages=[msg.model_dump() for msg in result.messages] if result.messages else [],
        error=result.error,
        model=result.model,
        provider=result.provider,
        turns_used=result.turns_used,
    )


@router.post("/delegate", response_model=SubAgentExecuteResponse)
async def delegate_task(request: SubAgentExecuteRequest):
    """
    Delegate a task to the most suitable SubAgent.
    
    The system will automatically select an appropriate SubAgent based on the task.
    """
    agents = subagent_manager.get_all_agents()
    if not agents:
        raise HTTPException(status_code=404, detail="No SubAgents available")
    
    agent_id = agents[0]["id"]
    
    result = await subagent_manager.execute_agent(
        agent_id=agent_id,
        instruction=request.instruction,
        paper_ids=request.paper_ids,
        context=request.context,
        provider=request.provider,
        model=request.model,
        max_turns=request.max_turns,
    )
    
    return SubAgentExecuteResponse(
        task_id=result.task_id,
        agent_id=result.agent_id,
        status=result.status.value if hasattr(result.status, 'value') else result.status,
        output=result.output,
        error=result.error,
        model=result.model,
        provider=result.provider,
        turns_used=result.turns_used,
    )


@router.get("/by-skill/{skill_id}", response_model=SubAgentListResponse)
async def get_subagents_by_skill(skill_id: str):
    """
    Get SubAgents that have a specific skill.
    
    Args:
        skill_id: The skill identifier to filter by
    """
    agents = subagent_manager.get_agents_by_skill(skill_id)
    return SubAgentListResponse(
        agents=[SubAgentInfo(**agent) for agent in agents],
        total=len(agents)
    )


@router.get("/by-tool/{tool_name}", response_model=SubAgentListResponse)
async def get_subagents_by_tool(tool_name: str):
    """
    Get SubAgents that have a specific tool.
    
    Args:
        tool_name: The tool name to filter by
    """
    agents = subagent_manager.get_agents_by_tool(tool_name)
    return SubAgentListResponse(
        agents=[SubAgentInfo(**agent) for agent in agents],
        total=len(agents)
    )
