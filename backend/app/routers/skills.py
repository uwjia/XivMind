from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.services.skill_service import skill_service

router = APIRouter(prefix="/skills", tags=["skills"])


class SkillExecuteRequest(BaseModel):
    paper_ids: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class SkillExecuteResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class SkillSaveRequest(BaseModel):
    content: str


@router.get("")
async def get_skills():
    """
    Get all available skills.
    
    Returns a list of all registered skills with their metadata.
    """
    skills = skill_service.get_all_skills()
    return {
        "skills": skills,
        "total": len(skills)
    }


@router.get("/categories")
async def get_skills_by_category():
    """
    Get skills grouped by category.
    
    Returns skills organized by their category (analysis, writing, search, etc.).
    """
    return skill_service.get_skills_by_category()


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """
    Get a specific skill by ID.
    
    Args:
        skill_id: The unique identifier of the skill.
    """
    skill = skill_service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
    return skill


@router.get("/{skill_id}/raw")
async def get_skill_raw(skill_id: str):
    """
    Get raw SKILL.md content for a skill.
    
    Args:
        skill_id: The unique identifier of the skill.
    
    Returns:
        The raw SKILL.md content.
    """
    raw_content = skill_service.get_skill_raw(skill_id)
    if not raw_content:
        raise HTTPException(status_code=404, detail=f"Skill not found or not a dynamic skill: {skill_id}")
    return {
        "skill_id": skill_id,
        "content": raw_content
    }


@router.post("/reload")
async def reload_skills():
    """
    Reload all dynamic skills from the skills directory.
    
    This will unload all dynamic skills and reload them from SKILL.md files.
    Built-in skills are not affected.
    """
    result = skill_service.reload_skills()
    return result


@router.post("/{skill_id}/reload")
async def reload_skill(skill_id: str):
    """
    Reload a specific skill.
    
    Args:
        skill_id: The unique identifier of the skill to reload.
    
    This will reload the skill from its SKILL.md file.
    """
    result = skill_service.reload_skill(skill_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.put("/{skill_id}")
async def save_skill(skill_id: str, request: SkillSaveRequest = Body(default=SkillSaveRequest(content=""))):
    """
    Save and reload a skill.
    
    Args:
        skill_id: The unique identifier of the skill to save.
        request: The save request containing the new SKILL.md content.
    
    This will save the content to SKILL.md file and reload the skill.
    """
    result = skill_service.save_skill(skill_id, request.content)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to save skill"))
    return result


@router.post("/{skill_id}/execute")
async def execute_skill(
    skill_id: str,
    request: SkillExecuteRequest = Body(default=SkillExecuteRequest())
):
    """
    Execute a skill.
    
    Args:
        skill_id: The unique identifier of the skill to execute.
        request: The execution request containing paper IDs and parameters.
    
    Returns:
        The skill execution result.
    """
    params = request.params or {}
    
    result = await skill_service.execute_skill(
        skill_id=skill_id,
        paper_ids=request.paper_ids,
        context=request.context,
        provider=request.provider,
        model=request.model,
        **params
    )
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to execute skill")
        )
    
    return result
