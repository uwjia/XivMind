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
from app.services.team.nodes import (
    NodeRegistry,
    NodeContext,
    NodeResult,
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
    sessions = team_manager.list_sessions()
    return SessionListResponse(
        sessions=sessions,
        total=len(sessions),
    )


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    session = team_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session


@router.get("/sessions/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    summary = team_manager.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return SessionSummaryResponse(**summary)


@router.post("/sessions/{session_id}/cancel")
async def cancel_session(session_id: str):
    success = await team_manager.cancel_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found or cannot be cancelled")
    return {"success": True, "message": f"Session '{session_id}' cancelled"}


@router.get("/stats", response_model=TeamStatsResponse)
async def get_team_stats():
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
        context = NodeContext(
            session_id=session_id,
            workflow_id=workflow.id,
            input_data=input_data,
            node_results=node_results,
            workflow=workflow,
            get_analysis=get_analysis,
        )
        
        node_type = node.type.value
        if NodeRegistry.is_registered(node_type):
            node_instance = NodeRegistry.create(
                node_type=node_type,
                node_id=node.id,
                config=node.config,
            )
            result = await node_instance.execute(context)
            node_results[node.id] = result.to_dict()
        else:
            logger.warning(f"[Workflow] Unknown node type: {node_type}")
            node_results[node.id] = {"output": None, "error": f"Unknown node type: {node_type}"}
        
        await progress_streamer.notify_node_status(
            session_id, node.id, "success", result=node_results[node.id].get("output")
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
