from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import asyncio
import uuid
import logging

from app.services.team import (
    team_manager,
    TeamExecuteRequest,
    TeamResult,
    TaskComplexity,
    DecompositionResult,
)
from app.services.team.progress_stream import progress_streamer
from app.services.team.workflow_adapter import (
    workflow_adapter,
    Workflow,
    WorkflowInput,
    WorkflowNode as AdapterWorkflowNode,
    WorkflowNodeType,
)

router = APIRouter(prefix="/team", tags=["team"])
logger = logging.getLogger(__name__)


class TeamExecuteResponse(BaseModel):
    task_id: str
    session_id: str
    status: str
    output: str = ""
    complexity: str
    total_subtasks: int = 0
    completed_subtasks: int = 0
    failed_subtasks: int = 0
    error: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskAnalysisResponse(BaseModel):
    complexity: str
    use_team_mode: bool
    subtasks: List[Dict[str, Any]] = []
    reasoning: str = ""


class SessionSummaryResponse(BaseModel):
    session_id: str
    task_id: Optional[str] = None
    instruction: Optional[str] = None
    status: Optional[str] = None
    total_subtasks: int = 0
    completed_subtasks: int = 0
    failed_subtasks: int = 0
    message_count: int = 0


class SessionListResponse(BaseModel):
    sessions: List[str]
    total: int


class TeamStatsResponse(BaseModel):
    initialized: bool
    orchestrator_stats: Dict[str, Any]
    available_agents: List[str]


class WorkflowExecuteRequest(BaseModel):
    workflow: Dict[str, Any]
    input: Dict[str, Any]


class WorkflowExecuteResponse(BaseModel):
    session_id: str
    status: str
    message: str


class WorkflowValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []


_active_workflow_sessions: Dict[str, asyncio.Task] = {}


@router.post("/analyze", response_model=TaskAnalysisResponse)
async def analyze_task(request: TeamExecuteRequest):
    """
    Analyze a task to determine complexity and decomposition.
    
    This endpoint analyzes the task without executing it, useful for
    previewing how the team system would handle a request.
    """
    result = await team_manager.analyze_task_async(
        instruction=request.instruction,
        context=request.context,
        provider=request.provider,
        model=request.model,
    )
    
    return TaskAnalysisResponse(
        complexity=result.complexity.value,
        use_team_mode=result.use_team_mode,
        subtasks=result.subtasks,
        reasoning=result.reasoning,
    )


@router.post("/execute", response_model=TeamExecuteResponse)
async def execute_team_task(request: TeamExecuteRequest):
    """
    Execute a task using the team system.
    
    The system will automatically determine whether to use single agent
    or team mode based on task complexity.
    
    Set force_team_mode=true to always use team mode.
    """
    result = await team_manager.execute(request)
    
    return TeamExecuteResponse(
        task_id=result.task_id,
        session_id=result.session_id,
        status=result.status.value if hasattr(result.status, 'value') else result.status,
        output=result.output,
        complexity=result.complexity.value if hasattr(result.complexity, 'value') else result.complexity,
        total_subtasks=result.total_subtasks,
        completed_subtasks=result.completed_subtasks,
        failed_subtasks=result.failed_subtasks,
        error=result.error,
        messages=[m.to_dict() if hasattr(m, 'to_dict') else m for m in result.messages],
        started_at=result.started_at.isoformat() if result.started_at else None,
        completed_at=result.completed_at.isoformat() if result.completed_at else None,
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """
    List all active team sessions.
    """
    sessions = team_manager.list_sessions()
    return SessionListResponse(
        sessions=sessions,
        total=len(sessions),
    )


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """
    Get details of a specific team session.
    """
    session = team_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session


@router.get("/sessions/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    """
    Get a summary of a team session.
    """
    summary = team_manager.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return SessionSummaryResponse(**summary)


@router.post("/sessions/{session_id}/cancel")
async def cancel_session(session_id: str):
    """
    Cancel an active team session.
    """
    success = await team_manager.cancel_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found or cannot be cancelled")
    return {"success": True, "message": f"Session '{session_id}' cancelled"}


@router.get("/stats", response_model=TeamStatsResponse)
async def get_team_stats():
    """
    Get statistics about the team system.
    """
    stats = team_manager.get_stats()
    
    available_agents = []
    if stats.get("initialized"):
        try:
            from app.services.subagents import subagent_manager
            agents = subagent_manager.get_all_agents()
            available_agents = [a.get("id") for a in agents if a.get("available", True)]
        except Exception:
            available_agents = ["research-agent", "analysis-agent", "writer-agent"]
    
    return TeamStatsResponse(
        initialized=stats.get("initialized", False),
        orchestrator_stats=stats.get("orchestrator_stats", {}),
        available_agents=available_agents,
    )


@router.post("/workflow/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(request: WorkflowExecuteRequest):
    workflow = workflow_adapter.parse_workflow(request.workflow)
    valid, errors = workflow_adapter.validate_workflow(workflow)
    return WorkflowValidationResponse(valid=valid, errors=errors)


@router.post("/workflow/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    workflow = workflow_adapter.parse_workflow(request.workflow)
    valid, errors = workflow_adapter.validate_workflow(workflow)
    
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    input_data = WorkflowInput(
        instruction=request.input.get("instruction", ""),
        paper_ids=request.input.get("paperIds"),
        context=request.input.get("context"),
    )
    
    session_id = str(uuid.uuid4())
    
    await progress_streamer.create_session(session_id)
    
    task = asyncio.create_task(
        _execute_workflow_background(session_id, workflow, input_data)
    )
    _active_workflow_sessions[session_id] = task
    
    return WorkflowExecuteResponse(
        session_id=session_id,
        status="started",
        message="Workflow execution started",
    )


@router.get("/workflow/stream/{session_id}")
async def stream_workflow_progress(session_id: str):
    client_id = str(uuid.uuid4())
    
    client = await progress_streamer.subscribe(session_id, client_id)
    
    return StreamingResponse(
        progress_streamer.event_generator(client_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/workflow/cancel/{session_id}")
async def cancel_workflow(session_id: str):
    if session_id in _active_workflow_sessions:
        task = _active_workflow_sessions[session_id]
        task.cancel()
        del _active_workflow_sessions[session_id]
        
        await progress_streamer.notify_session_completed(
            session_id, error="Workflow cancelled by user"
        )
        
        return {"success": True, "message": f"Workflow session '{session_id}' cancelled"}
    
    raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")


async def _execute_workflow_background(
    session_id: str,
    workflow: Workflow,
    input_data: WorkflowInput,
):
    node_map = {node.id: node for node in workflow.nodes}
    node_results: Dict[str, Any] = {}
    cached_analysis: Optional[DecompositionResult] = None
    
    async def get_or_analyze_task() -> DecompositionResult:
        nonlocal cached_analysis
        if cached_analysis is None:
            cached_analysis = await team_manager.analyze_task_async(
                input_data.instruction, input_data.context
            )
        return cached_analysis
    
    try:
        await asyncio.sleep(0.5)
        
        await progress_streamer.notify_log(
            session_id, "info", f"Starting workflow execution: {workflow.name}"
        )
        
        execution_order = workflow_adapter._compute_execution_order(workflow)
        
        for level_idx, level in enumerate(execution_order):
            parallel_nodes = [node_map[nid] for nid in level if nid in node_map]
            
            if len(parallel_nodes) > 1:
                await _execute_parallel_nodes(
                    session_id, workflow, parallel_nodes, node_results, input_data, get_or_analyze_task
                )
            else:
                for node in parallel_nodes:
                    await _execute_single_node(
                        session_id, workflow, node, node_results, input_data, get_or_analyze_task
                    )
        
        output_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.OUTPUT]
        final_output = ""
        if output_nodes:
            output_node = output_nodes[0]
            final_output = node_results.get(output_node.id, {}).get("output", "")
        
        await progress_streamer.notify_session_completed(session_id, output=final_output)
        
    except asyncio.CancelledError:
        logger.info(f"[Workflow] Session {session_id} cancelled")
        await progress_streamer.notify_session_completed(session_id, error="Cancelled")
        
    except Exception as e:
        logger.error(f"[Workflow] Session {session_id} failed: {e}")
        await progress_streamer.notify_session_completed(session_id, error=str(e))
        
    finally:
        if session_id in _active_workflow_sessions:
            del _active_workflow_sessions[session_id]


async def _execute_single_node(
    session_id: str,
    workflow: Workflow,
    node: AdapterWorkflowNode,
    node_results: Dict[str, Any],
    input_data: WorkflowInput,
    get_analysis,
):
    logger.info(f"[Workflow] ========== Executing Node =========")
    logger.info(f"[Workflow] Node ID: {node.id}")
    logger.info(f"[Workflow] Node Type: {node.type.value}")
    logger.info(f"[Workflow] Node Label: {node.label}")
    
    await progress_streamer.notify_node_status(
        session_id, node.id, "running"
    )
    
    try:
        context = _build_node_context(node, workflow, node_results, input_data)
        
        if node.type == WorkflowNodeType.INPUT:
            result = {"output": input_data.instruction}
            
        elif node.type == WorkflowNodeType.ANALYZE:
            analysis = await get_analysis()
            
            logger.info(f"[Workflow] Task Analysis Result:")
            logger.info(f"  Complexity: {analysis.complexity.value}")
            logger.info(f"  Team Mode: {analysis.use_team_mode}")
            logger.info(f"  Subtasks: {len(analysis.subtasks)}")
            
            if analysis.use_team_mode and analysis.subtasks:
                for i, subtask in enumerate(analysis.subtasks):
                    agent = subtask.get("assigned_agent", "analysis-agent")
                    task_type = subtask.get("task_type", "analysis")
                    deps = subtask.get("dependencies", [])
                    instruction = subtask.get("instruction", "")[:60]
                    logger.info(f"  [{i}] Agent: {agent}, Type: {task_type}, Deps: {deps}")
                    logger.info(f"      Instruction: {instruction}...")
            
            result = {
                "output": {
                    "complexity": analysis.complexity.value,
                    "use_team_mode": analysis.use_team_mode,
                    "subtasks": analysis.subtasks,
                    "reasoning": analysis.reasoning,
                }
            }
            
        elif node.type == WorkflowNodeType.DECOMPOSE:
            analysis = await get_analysis()
            result = {"output": analysis.subtasks}
            
        elif node.type == WorkflowNodeType.AGENT:
            agent_id = node.config.get("agentId", "research-agent")
            instruction = node.config.get("instruction") or input_data.instruction
            
            try:
                from app.services.subagents import subagent_manager
                agent_result = await subagent_manager.execute_agent(
                    agent_id=agent_id,
                    instruction=instruction,
                    paper_ids=input_data.paper_ids,
                    context=input_data.context,
                )
                result = {"output": agent_result.output if hasattr(agent_result, 'output') else str(agent_result)}
            except Exception as e:
                logger.error(f"[Workflow] Agent {agent_id} execution failed: {e}")
                result = {"output": "", "error": str(e)}
            
        elif node.type == WorkflowNodeType.CONDITION:
            condition_result = workflow_adapter.evaluate_condition(node, context)
            result = {"output": condition_result, "branch": condition_result}
            
        elif node.type == WorkflowNodeType.SYNTHESIZE:
            deps = workflow_adapter.get_node_dependencies(workflow, node.id)
            dep_results = [node_results.get(d, {}).get("output", "") for d in deps]
            combined = "\n\n".join(str(r) for r in dep_results if r)
            result = {"output": combined}
            
        elif node.type == WorkflowNodeType.OUTPUT:
            deps = workflow_adapter.get_node_dependencies(workflow, node.id)
            dep_results = [node_results.get(d, {}).get("output", "") for d in deps]
            result = {"output": dep_results[0] if dep_results else ""}
            
        elif node.type == WorkflowNodeType.SKILL:
            skill_id = node.config.get("skillId", "summary")
            instruction = node.config.get("instruction") or input_data.instruction
            
            try:
                from app.services.subagents import subagent_manager
                agent_result = await subagent_manager.execute_agent(
                    agent_id="research-agent",
                    instruction=f"Use skill {skill_id}: {instruction}",
                    paper_ids=input_data.paper_ids,
                    context=input_data.context,
                )
                result = {"output": agent_result.output if hasattr(agent_result, 'output') else str(agent_result)}
            except Exception as e:
                logger.error(f"[Workflow] Skill {skill_id} execution failed: {e}")
                result = {"output": "", "error": str(e)}
            
        elif node.type == WorkflowNodeType.TOOL:
            tool_id = node.config.get("toolId", "")
            instruction = node.config.get("instruction") or input_data.instruction
            
            try:
                from app.services.subagents import subagent_manager
                agent_result = await subagent_manager.execute_agent(
                    agent_id="research-agent",
                    instruction=f"Use tool {tool_id}: {instruction}",
                    paper_ids=input_data.paper_ids,
                    context=input_data.context,
                )
                result = {"output": agent_result.output if hasattr(agent_result, 'output') else str(agent_result)}
            except Exception as e:
                logger.error(f"[Workflow] Tool {tool_id} execution failed: {e}")
                result = {"output": "", "error": str(e)}
            
        else:
            result = {"output": None}
        
        node_results[node.id] = result
        await progress_streamer.notify_node_status(
            session_id, node.id, "success", result=result.get("output")
        )
        
    except Exception as e:
        logger.error(f"[Workflow] Node {node.id} failed: {e}")
        await progress_streamer.notify_node_status(
            session_id, node.id, "error", error=str(e)
        )
        node_results[node.id] = {"output": None, "error": str(e)}


async def _execute_parallel_nodes(
    session_id: str,
    workflow: Workflow,
    nodes: List[AdapterWorkflowNode],
    node_results: Dict[str, Any],
    input_data: WorkflowInput,
    get_analysis,
):
    tasks = [
        _execute_single_node(session_id, workflow, node, node_results, input_data, get_analysis)
        for node in nodes
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


def _build_node_context(
    node: AdapterWorkflowNode,
    workflow: Workflow,
    node_results: Dict[str, Any],
    input_data: WorkflowInput,
) -> Dict[str, Any]:
    deps = workflow_adapter.get_node_dependencies(workflow, node.id)
    dep_results = {d: node_results.get(d, {}) for d in deps}
    
    return {
        "input_data": input_data.instruction,
        "paper_ids": input_data.paper_ids,
        "dependencies": dep_results,
        "config": node.config,
    }
