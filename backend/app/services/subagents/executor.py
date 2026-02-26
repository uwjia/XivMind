import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import SubAgentBase
from .types import (
    SubAgentTask,
    SubAgentResult,
    SubAgentStatus,
    SubAgentMessage,
    SubAgentMessageRole,
    SubAgentToolCall,
    SubAgentExecutionContext,
)
from .context import SubAgentContextManager, ContextSummarizer
from .tools import ToolRegistry

logger = logging.getLogger(__name__)


class SubAgentExecutor:
    """Executor for running SubAgent tasks."""
    
    def __init__(self):
        self.context_manager = SubAgentContextManager()
        self.summarizer = ContextSummarizer()
    
    async def execute(self, agent: SubAgentBase, task: SubAgentTask) -> SubAgentResult:
        started_at = datetime.now()
        
        context = agent.create_context(task)
        self.context_manager.update_context(context)
        
        result = SubAgentResult(
            task_id=task.id,
            agent_id=agent.id,
            status=SubAgentStatus.RUNNING,
            started_at=started_at,
            provider=task.provider or agent.provider,
            model=task.model or agent.model,
        )
        
        try:
            output = await self._run_conversation(agent, context, task)
            
            result.status = SubAgentStatus.COMPLETED
            result.output = output
            result.messages = context.messages
            result.turns_used = context.current_turn
            
        except Exception as e:
            logger.error(f"SubAgent {agent.id} execution failed: {e}")
            result.status = SubAgentStatus.FAILED
            result.error = str(e)
        
        result.completed_at = datetime.now()
        
        self.context_manager.remove_context(task.id)
        
        return result
    
    async def _run_conversation(
        self,
        agent: SubAgentBase,
        context: SubAgentExecutionContext,
        task: SubAgentTask
    ) -> str:
        from app.services.llm_service import llm_service
        
        provider = task.provider or agent.provider
        model = task.model or agent.model
        
        context.provider = provider
        context.model = model
        
        logger.info(f"[SubAgent Execute] Agent: {agent.id}, Provider: {provider}, Model: {model}")
        logger.info(f"[SubAgent Task] Instruction: {task.instruction[:200]}...")
        if task.paper_ids:
            logger.info(f"[SubAgent Papers] IDs: {task.paper_ids}")
        
        while not self.context_manager.is_turn_limit_reached(context.task_id):
            self.context_manager.increment_turn(context.task_id)
            
            if self.summarizer.should_summarize(context):
                language = getattr(agent._config, 'language', 'en') or 'en'
                context.messages = self.summarizer.summarize_messages(context.messages, language=language)
            
            messages = context.get_messages_for_llm()
            logger.info(f"[SubAgent LLM Call] Turn {context.current_turn}, Messages: {len(messages)}")
            
            try:
                response = await llm_service.generate_with_messages(
                    messages=messages,
                    provider=provider,
                    model=model,
                    temperature=agent.temperature,
                )
                logger.info(f"[SubAgent LLM Response] Turn {context.current_turn}, Response: {response[:300]}...")
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                raise
            
            context.add_message(SubAgentMessageRole.ASSISTANT, response)
            
            if not response or not response.strip():
                logger.warning(f"[SubAgent Empty Response] Turn {context.current_turn}, LLM returned empty response")
                if context.current_turn >= context.max_turns:
                    return "The model returned an empty response. Please try again or use a different model."
                continue
            
            if self._should_stop(response):
                logger.info(f"[SubAgent Stop] Found stop marker in response")
                return response
            
            tool_calls = self._extract_tool_calls(response)
            if tool_calls:
                logger.info(f"[SubAgent Tool Calls] Found {len(tool_calls)} tool calls")
                for tool_call in tool_calls:
                    tool_result = await self._execute_tool(agent, tool_call, context)
                    context.add_message(
                        SubAgentMessageRole.TOOL,
                        tool_result,
                        name=tool_call.name,
                        tool_call_id=tool_call.id,
                    )
            else:
                return response
        
        return context.messages[-1].content if context.messages else ""
    
    def _should_stop(self, response: str) -> bool:
        stop_markers = ["[DONE]", "[COMPLETE]", "[FINISHED]"]
        return any(marker in response for marker in stop_markers)
    
    def _extract_tool_calls(self, response: str) -> List[SubAgentToolCall]:
        import re
        import uuid
        
        tool_calls = []
        
        pattern = r'\[TOOL:\s*(\w+)\s*\((.*?)\)\]'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            tool_name = match[0]
            args_str = match[1].strip()
            
            try:
                import json
                if args_str:
                    args = json.loads(args_str)
                else:
                    args = {}
            except json.JSONDecodeError:
                args = {"raw": args_str}
            
            tool_calls.append(SubAgentToolCall(
                id=str(uuid.uuid4()),
                name=tool_name,
                arguments=args,
            ))
        
        return tool_calls
    
    async def _execute_tool(
        self,
        agent: SubAgentBase,
        tool_call: SubAgentToolCall,
        context: SubAgentExecutionContext
    ) -> str:
        logger.info(f"[SubAgent Tool Call] Agent: {agent.id}, Tool: {tool_call.name}, Args: {tool_call.arguments}")
        
        tool = ToolRegistry.get(tool_call.name)
        
        if not tool:
            error_msg = f"Error: Unknown tool '{tool_call.name}'"
            logger.warning(f"[SubAgent Tool Error] {error_msg}")
            return error_msg
        
        if not agent.has_tool(tool_call.name):
            error_msg = f"Error: Agent '{agent.id}' does not have access to tool '{tool_call.name}'"
            logger.warning(f"[SubAgent Tool Error] {error_msg}")
            return error_msg
        
        try:
            result = await tool.execute(tool_call.arguments, context)
            logger.info(f"[SubAgent Tool Result] Tool: {tool_call.name}, Result: {str(result)[:500]}...")
            return result
        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            logger.error(f"[SubAgent Tool Exception] Tool: {tool_call.name}, Error: {e}")
            return error_msg
