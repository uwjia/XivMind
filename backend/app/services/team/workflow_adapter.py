import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .types import (
    TaskComplexity,
    TeamTask,
    SubTask,
    TeamSession,
)

logger = logging.getLogger(__name__)


class WorkflowNodeType(str, Enum):
    INPUT = "input"
    ANALYZE = "analyze"
    DECOMPOSE = "decompose"
    AGENT = "agent"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SYNTHESIZE = "synthesize"
    OUTPUT = "output"
    TOOL = "tool"
    SKILL = "skill"


@dataclass
class WorkflowNode:
    id: str
    type: WorkflowNodeType
    label: str
    position: Dict[str, float]
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "idle"
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class WorkflowEdge:
    id: str
    source: str
    target: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    label: Optional[str] = None


@dataclass
class Workflow:
    id: str
    name: str
    description: str = ""
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WorkflowInput:
    instruction: str
    paper_ids: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionPlan:
    session_id: str
    nodes: List[WorkflowNode]
    execution_order: List[List[str]]
    input_node_id: Optional[str] = None
    output_node_id: Optional[str] = None
    input_data: Optional[WorkflowInput] = None


class WorkflowAdapter:
    def __init__(self):
        pass
    
    def parse_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        nodes = []
        for node_data in workflow_data.get("nodes", []):
            node = WorkflowNode(
                id=node_data.get("id", str(uuid.uuid4())),
                type=WorkflowNodeType(node_data.get("type", "input")),
                label=node_data.get("label", ""),
                position=node_data.get("position", {"x": 0, "y": 0}),
                config=node_data.get("config", {}),
                status=node_data.get("status", "idle"),
                inputs=node_data.get("inputs", []),
                outputs=node_data.get("outputs", []),
                result=node_data.get("result"),
                error=node_data.get("error"),
            )
            nodes.append(node)
        
        edges = []
        for edge_data in workflow_data.get("edges", []):
            edge = WorkflowEdge(
                id=edge_data.get("id", str(uuid.uuid4())),
                source=edge_data.get("source", ""),
                target=edge_data.get("target", ""),
                source_port=edge_data.get("sourcePort"),
                target_port=edge_data.get("targetPort"),
                label=edge_data.get("label"),
            )
            edges.append(edge)
        
        return Workflow(
            id=workflow_data.get("id", str(uuid.uuid4())),
            name=workflow_data.get("name", "Untitled"),
            description=workflow_data.get("description", ""),
            nodes=nodes,
            edges=edges,
            variables=workflow_data.get("variables", []),
        )
    
    def create_execution_plan(
        self,
        workflow: Workflow,
        input_data: WorkflowInput,
    ) -> ExecutionPlan:
        node_map = {node.id: node for node in workflow.nodes}
        
        input_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.INPUT]
        output_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.OUTPUT]
        
        input_node_id = input_nodes[0].id if input_nodes else None
        output_node_id = output_nodes[0].id if output_nodes else None
        
        execution_order = self._compute_execution_order(workflow)
        
        return ExecutionPlan(
            session_id=str(uuid.uuid4()),
            nodes=workflow.nodes,
            execution_order=execution_order,
            input_node_id=input_node_id,
            output_node_id=output_node_id,
            input_data=input_data,
        )
    
    def _compute_execution_order(self, workflow: Workflow) -> List[List[str]]:
        node_map = {node.id: node for node in workflow.nodes}
        
        in_degree = {node.id: 0 for node in workflow.nodes}
        adjacency = {node.id: [] for node in workflow.nodes}
        
        for edge in workflow.edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge.target)
            if edge.target in in_degree:
                in_degree[edge.target] += 1
        
        levels = []
        remaining = set(in_degree.keys())
        
        while remaining:
            level = [
                node_id for node_id in remaining
                if in_degree[node_id] == 0
            ]
            
            if not level:
                logger.warning("[WorkflowAdapter] Circular dependency detected")
                break
            
            levels.append(level)
            
            for node_id in level:
                remaining.remove(node_id)
                for neighbor in adjacency[node_id]:
                    if neighbor in in_degree:
                        in_degree[neighbor] -= 1
        
        return levels
    
    def get_node_dependencies(
        self,
        workflow: Workflow,
        node_id: str,
    ) -> List[str]:
        dependencies = []
        for edge in workflow.edges:
            if edge.target == node_id:
                dependencies.append(edge.source)
        return dependencies
    
    def get_node_successors(
        self,
        workflow: Workflow,
        node_id: str,
    ) -> List[str]:
        successors = []
        for edge in workflow.edges:
            if edge.source == node_id:
                successors.append(edge.target)
        return successors
    
    def workflow_to_team_task(
        self,
        workflow: Workflow,
        input_data: WorkflowInput,
    ) -> Tuple[TeamTask, Dict[str, WorkflowNode]]:
        node_map = {node.id: node for node in workflow.nodes}
        
        agent_nodes = [
            node for node in workflow.nodes
            if node.type == WorkflowNodeType.AGENT
        ]
        
        subtasks = []
        for i, node in enumerate(agent_nodes):
            agent_id = node.config.get("agentId", "research-agent")
            instruction = node.config.get("instruction") or input_data.instruction
            
            subtask = SubTask(
                id=f"st_{node.id}",
                instruction=instruction,
                assigned_agent=agent_id,
                dependencies=[],
                status="pending",
            )
            subtasks.append(subtask)
        
        task = TeamTask(
            id=f"task_{workflow.id}",
            instruction=input_data.instruction,
            complexity=TaskComplexity.MODERATE if len(subtasks) > 1 else TaskComplexity.SIMPLE,
            subtasks=subtasks,
            context=input_data.context or {},
            paper_ids=input_data.paper_ids or [],
        )
        
        return task, node_map
    
    def is_parallel_node(self, node: WorkflowNode) -> bool:
        return node.type == WorkflowNodeType.PARALLEL
    
    def is_condition_node(self, node: WorkflowNode) -> bool:
        return node.type == WorkflowNodeType.CONDITION
    
    def evaluate_condition(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
    ) -> str:
        condition = node.config.get("condition", "")
        
        try:
            local_vars = {
                "complexity": context.get("complexity", "simple"),
                "result": context.get("result"),
                "status": context.get("status"),
            }
            result = eval(condition, {"__builtins__": {}}, local_vars)
            return "true" if result else "false"
        except Exception as e:
            logger.warning(f"[WorkflowAdapter] Condition evaluation failed: {e}")
            return "true"
    
    def get_parallel_branches(
        self,
        workflow: Workflow,
        parallel_node_id: str,
    ) -> List[List[str]]:
        branches = []
        
        for edge in workflow.edges:
            if edge.source == parallel_node_id:
                branch = self._trace_branch(workflow, edge.target)
                branches.append(branch)
        
        return branches
    
    def _trace_branch(
        self,
        workflow: Workflow,
        start_node_id: str,
    ) -> List[str]:
        branch = [start_node_id]
        current = start_node_id
        
        while True:
            successors = self.get_node_successors(workflow, current)
            if len(successors) != 1:
                break
            next_node_id = successors[0]
            next_node = next((n for n in workflow.nodes if n.id == next_node_id), None)
            if next_node and next_node.type in [WorkflowNodeType.SYNTHESIZE, WorkflowNodeType.OUTPUT]:
                break
            branch.append(next_node_id)
            current = next_node_id
        
        return branch
    
    def validate_workflow(self, workflow: Workflow) -> Tuple[bool, List[str]]:
        errors = []
        
        if not workflow.nodes:
            errors.append("Workflow must have at least one node")
            return False, errors
        
        input_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.INPUT]
        if not input_nodes:
            errors.append("Workflow must have at least one input node")
        
        output_nodes = [n for n in workflow.nodes if n.type == WorkflowNodeType.OUTPUT]
        if not output_nodes:
            errors.append("Workflow must have at least one output node")
        
        for node in workflow.nodes:
            if node.type == WorkflowNodeType.AGENT:
                if not node.config.get("agentId"):
                    errors.append(f"Agent node '{node.label}' must have an agent selected")
            
            if node.type == WorkflowNodeType.SKILL:
                if not node.config.get("skillId"):
                    errors.append(f"Skill node '{node.label}' must have a skill selected")
        
        if self._has_circular_dependency(workflow):
            errors.append("Workflow contains circular dependencies")
        
        return len(errors) == 0, errors
    
    def _has_circular_dependency(self, workflow: Workflow) -> bool:
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for edge in workflow.edges:
                if edge.source == node_id:
                    neighbor = edge.target
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node in workflow.nodes:
            if node.id not in visited:
                if has_cycle(node.id):
                    return True
        
        return False


workflow_adapter = WorkflowAdapter()
