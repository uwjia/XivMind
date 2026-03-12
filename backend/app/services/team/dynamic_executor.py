import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .progress_stream import progress_streamer
from .nodes import NodeRegistry, NodeContext
from .workflow_adapter import WorkflowInput, Workflow

logger = logging.getLogger(__name__)


@dataclass
class SubtaskInfo:
    id: str
    instruction: str
    assigned_agent: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DynamicNodeConfig:
    node_id: str
    node_type: str
    label: str
    config: Dict[str, Any]
    position: Dict[str, float]
    source_node_ids: List[str] = field(default_factory=list)


class DynamicWorkflowExecutor:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.subtasks: List[SubtaskInfo] = []
        self.node_results: Dict[str, Any] = {}
        self.dynamic_nodes: List[DynamicNodeConfig] = []
        self.workflow: Optional[Workflow] = None
        self.input_data: Optional[WorkflowInput] = None
        self._pending_executions: Dict[str, asyncio.Task] = {}
    
    async def initialize(
        self,
        workflow: Workflow,
        input_data: WorkflowInput,
    ):
        self.workflow = workflow
        self.input_data = input_data
        
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "initializing",
            "Initializing dynamic workflow execution"
        )
    
    async def execute_analysis(self) -> List[SubtaskInfo]:
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "analyzing",
            "Analyzing task and decomposing into subtasks"
        )
        
        analyze_nodes = [
            n for n in self.workflow.nodes
            if n.type.value == "analyze"
        ]
        
        if not analyze_nodes:
            raise ValueError("No analyze node found in workflow")
        
        analyze_node = analyze_nodes[0]
        
        node_instance = NodeRegistry.create(
            node_type="analyze",
            node_id=analyze_node.id,
            config=analyze_node.config,
        )
        
        async def get_analysis():
            from app.services.team import team_manager
            return await team_manager.analyze_task_async(
                self.input_data.instruction,
                self.input_data.context,
            )
        
        context = NodeContext(
            session_id=self.session_id,
            workflow_id=self.workflow.id,
            input_data=self.input_data,
            node_results=self.node_results,
            workflow=self.workflow,
            get_analysis=get_analysis,
        )
        
        await progress_streamer.notify_node_status(
            self.session_id,
            analyze_node.id,
            "running"
        )
        
        result = await node_instance.execute(context)
        self.node_results[analyze_node.id] = result.to_dict()
        
        if result.error:
            await progress_streamer.notify_node_status(
                self.session_id,
                analyze_node.id,
                "error",
                error=result.error
            )
            raise ValueError(f"Analysis failed: {result.error}")
        
        await progress_streamer.notify_node_status(
            self.session_id,
            analyze_node.id,
            "success",
            result=result.output
        )
        
        subtasks_data = result.output.get("subtasks", []) if result.output else []
        
        self.subtasks = [
            SubtaskInfo(
                id=st.get("id", f"subtask_{i}"),
                instruction=st.get("instruction", ""),
                assigned_agent=st.get("assigned_agent", "research-agent"),
                dependencies=st.get("dependencies", []),
                metadata=st.get("metadata", {}),
            )
            for i, st in enumerate(subtasks_data)
        ]
        
        return self.subtasks
    
    async def create_agent_nodes(self, subtasks: List[SubtaskInfo]):
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "creating_nodes",
            f"Creating {len(subtasks)} agent nodes dynamically"
        )
        
        analyze_nodes = [
            n for n in self.workflow.nodes
            if n.type.value == "analyze"
        ]
        source_x = analyze_nodes[0].position.get("x", 300) if analyze_nodes else 300
        source_y = analyze_nodes[0].position.get("y", 200) if analyze_nodes else 200
        
        start_x = source_x + 300
        vertical_spacing = 150
        
        created_nodes = []
        
        for i, subtask in enumerate(subtasks):
            node_id = f"dynamic_agent_{subtask.id}"
            position = {
                "x": start_x,
                "y": source_y + (i - len(subtasks) / 2) * vertical_spacing
            }
            
            config = {
                "agentId": subtask.assigned_agent,
                "instruction": subtask.instruction,
                "timeout": 300,
            }
            
            source_node_ids = []
            if analyze_nodes:
                source_node_ids.append(analyze_nodes[0].id)
            
            await progress_streamer.notify_dynamic_node_created(
                session_id=self.session_id,
                node_id=node_id,
                node_type="agent",
                label=f"Agent: {subtask.assigned_agent}",
                config=config,
                position=position,
                source_node_ids=source_node_ids,
            )
            
            node_config = DynamicNodeConfig(
                node_id=node_id,
                node_type="agent",
                label=f"Agent: {subtask.assigned_agent}",
                config=config,
                position=position,
                source_node_ids=source_node_ids,
            )
            created_nodes.append(node_config)
            self.dynamic_nodes.append(node_config)
        
        return created_nodes
    
    async def execute_agent_node(self, node_config: DynamicNodeConfig) -> Dict[str, Any]:
        node_id = node_config.node_id
        agent_id = node_config.config.get("agentId", "research-agent")
        instruction = node_config.config.get("instruction", "")
        
        await progress_streamer.notify_node_status(
            self.session_id,
            node_id,
            "running"
        )
        
        try:
            from app.services.subagents import subagent_manager
            
            agent_result = await subagent_manager.execute_agent(
                agent_id=agent_id,
                instruction=instruction,
                paper_ids=self.input_data.paper_ids if self.input_data else None,
                context=self.input_data.context if self.input_data else None,
            )
            
            output = agent_result.output if hasattr(agent_result, 'output') else str(agent_result)
            
            self.node_results[node_id] = {"output": output}
            
            await progress_streamer.notify_node_status(
                self.session_id,
                node_id,
                "success",
                result=output
            )
            
            return {"output": output}
            
        except Exception as e:
            logger.error(f"[DynamicExecutor] Agent {agent_id} execution failed: {e}")
            
            await progress_streamer.notify_node_status(
                self.session_id,
                node_id,
                "error",
                error=str(e)
            )
            
            self.node_results[node_id] = {"output": None, "error": str(e)}
            return {"output": None, "error": str(e)}
    
    async def execute_all_agents_parallel(self):
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "executing",
            f"Executing {len(self.dynamic_nodes)} agent nodes in parallel"
        )
        
        agent_nodes = [
            n for n in self.dynamic_nodes
            if n.node_type == "agent"
        ]
        
        tasks = [
            self.execute_agent_node(node)
            for node in agent_nodes
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("output"))
        failed = len(results) - successful
        
        logger.info(f"[DynamicExecutor] Parallel execution completed: {successful} success, {failed} failed")
        
        return results
    
    async def create_synthesize_node(self) -> DynamicNodeConfig:
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "synthesizing",
            "Creating synthesize node to combine results"
        )
        
        agent_nodes = [
            n for n in self.dynamic_nodes
            if n.node_type == "agent"
        ]
        
        if not agent_nodes:
            raise ValueError("No agent nodes to synthesize")
        
        avg_y = sum(n.position["y"] for n in agent_nodes) / len(agent_nodes)
        max_x = max(n.position["x"] for n in agent_nodes)
        
        position = {
            "x": max_x + 300,
            "y": avg_y
        }
        
        source_node_ids = [n.node_id for n in agent_nodes]
        
        node_id = "dynamic_synthesize"
        
        config = {
            "strategy": "merge"
        }
        
        await progress_streamer.notify_dynamic_node_created(
            session_id=self.session_id,
            node_id=node_id,
            node_type="synthesize",
            label="Synthesize Results",
            config=config,
            position=position,
            source_node_ids=source_node_ids,
        )
        
        node_config = DynamicNodeConfig(
            node_id=node_id,
            node_type="synthesize",
            label="Synthesize Results",
            config=config,
            position=position,
            source_node_ids=source_node_ids,
        )
        
        self.dynamic_nodes.append(node_config)
        return node_config
    
    async def execute_synthesize_node(self, node_config: DynamicNodeConfig) -> Dict[str, Any]:
        node_id = node_config.node_id
        
        await progress_streamer.notify_node_status(
            self.session_id,
            node_id,
            "running"
        )
        
        try:
            source_results = [
                self.node_results.get(source_id, {}).get("output", "")
                for source_id in node_config.source_node_ids
            ]
            
            combined = "\n\n".join(str(r) for r in source_results if r)
            
            self.node_results[node_id] = {"output": combined}
            
            await progress_streamer.notify_node_status(
                self.session_id,
                node_id,
                "success",
                result=combined
            )
            
            return {"output": combined}
            
        except Exception as e:
            logger.error(f"[DynamicExecutor] Synthesize execution failed: {e}")
            
            await progress_streamer.notify_node_status(
                self.session_id,
                node_id,
                "error",
                error=str(e)
            )
            
            return {"output": None, "error": str(e)}
    
    async def create_output_node(self, synthesize_node_id: str) -> DynamicNodeConfig:
        await progress_streamer.notify_execution_phase(
            self.session_id,
            "finalizing",
            "Creating output node"
        )
        
        synthesize_node = next(
            n for n in self.dynamic_nodes
            if n.node_id == synthesize_node_id
        )
        
        position = {
            "x": synthesize_node.position["x"] + 400,
            "y": synthesize_node.position["y"]
        }
        
        node_id = "dynamic_output"
        
        await progress_streamer.notify_dynamic_node_created(
            session_id=self.session_id,
            node_id=node_id,
            node_type="output",
            label="Final Output",
            config={},
            position=position,
            source_node_ids=[synthesize_node_id],
        )
        
        node_config = DynamicNodeConfig(
            node_id=node_id,
            node_type="output",
            label="Final Output",
            config={},
            position=position,
            source_node_ids=[synthesize_node_id],
        )
        
        self.dynamic_nodes.append(node_config)
        return node_config
    
    async def run_full_workflow(self) -> str:
        try:
            subtasks = await self.execute_analysis()
            
            if not subtasks:
                await progress_streamer.notify_session_completed(
                    self.session_id,
                    output="No subtasks generated"
                )
                return "No subtasks generated"
            
            await progress_streamer.notify_subtasks_created(
                self.session_id,
                [
                    {
                        "id": st.id,
                        "instruction": st.instruction,
                        "assignedAgent": st.assigned_agent,
                        "dependencies": st.dependencies,
                    }
                    for st in subtasks
                ]
            )
            
            await self.create_agent_nodes(subtasks)
            
            await self.execute_all_agents_parallel()
            
            synthesize_node = await self.create_synthesize_node()
            
            synthesize_result = await self.execute_synthesize_node(synthesize_node)
            
            output_node = await self.create_output_node(synthesize_node.node_id)
            
            final_output = self.node_results.get(synthesize_node.node_id, {}).get("output", "")
            
            await progress_streamer.notify_node_status(
                self.session_id,
                output_node.node_id,
                "success",
                result=final_output
            )
            
            await progress_streamer.notify_session_completed(self.session_id, output=final_output)
            
            return final_output
            
        except Exception as e:
            logger.error(f"[DynamicExecutor] Workflow execution failed: {e}")
            await progress_streamer.notify_session_completed(self.session_id, error=str(e))
            raise
