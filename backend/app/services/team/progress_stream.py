import asyncio
import json
import logging
from typing import Dict, Any, Optional, Set, Callable, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StreamClient:
    client_id: str
    session_id: str
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    connected: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class ProgressStreamer:
    def __init__(self):
        self._clients: Dict[str, StreamClient] = {}
        self._session_clients: Dict[str, Set[str]] = {}
        self._session_events: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    async def create_session(self, session_id: str):
        async with self._lock:
            if session_id not in self._session_clients:
                self._session_clients[session_id] = set()
            if session_id not in self._session_events:
                self._session_events[session_id] = []
            logger.info(f"[ProgressStreamer] Session {session_id} created")
    
    async def subscribe(self, session_id: str, client_id: str) -> StreamClient:
        async with self._lock:
            client = StreamClient(
                client_id=client_id,
                session_id=session_id,
            )
            self._clients[client_id] = client
            
            if session_id not in self._session_clients:
                self._session_clients[session_id] = set()
            self._session_clients[session_id].add(client_id)
            
            logger.info(f"[ProgressStreamer] Client {client_id} subscribed to session {session_id}")
            return client
    
    async def unsubscribe(self, client_id: str):
        async with self._lock:
            client = self._clients.pop(client_id, None)
            if client:
                client.connected = False
                if client.session_id in self._session_clients:
                    self._session_clients[client.session_id].discard(client_id)
                    if not self._session_clients[client.session_id]:
                        del self._session_clients[client.session_id]
                logger.info(f"[ProgressStreamer] Client {client_id} unsubscribed")
    
    async def broadcast_to_session(self, session_id: str, event: str, data: Dict[str, Any]):
        async with self._lock:
            client_ids = self._session_clients.get(session_id, set()).copy()
        
        message = self._format_sse(event, data)
        
        for client_id in client_ids:
            client = self._clients.get(client_id)
            if client and client.connected:
                try:
                    await client.queue.put(message)
                except Exception as e:
                    logger.warning(f"[ProgressStreamer] Failed to send to client {client_id}: {e}")
    
    async def send_to_client(self, client_id: str, event: str, data: Dict[str, Any]):
        client = self._clients.get(client_id)
        if client and client.connected:
            message = self._format_sse(event, data)
            await client.queue.put(message)
    
    def _format_sse(self, event: str, data: Dict[str, Any]) -> str:
        data_str = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event}\ndata: {data_str}\n\n"
    
    async def event_generator(self, client_id: str) -> AsyncGenerator[str, None]:
        client = self._clients.get(client_id)
        if not client:
            yield self._format_sse("error", {"message": "Client not found"})
            return
        
        yield self._format_sse("connected", {
            "client_id": client_id,
            "session_id": client.session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            while client.connected:
                try:
                    message = await asyncio.wait_for(
                        client.queue.get(),
                        timeout=30.0
                    )
                    yield message
                    
                    if "event: session_completed" in message:
                        break
                        
                except asyncio.TimeoutError:
                    yield self._format_sse("heartbeat", {"timestamp": datetime.now().isoformat()})
                    
        except asyncio.CancelledError:
            logger.info(f"[ProgressStreamer] Stream cancelled for client {client_id}")
        finally:
            await self.unsubscribe(client_id)
    
    async def notify_node_status(
        self,
        session_id: str,
        node_id: str,
        status: str,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        progress: Optional[float] = None,
    ):
        data = {
            "nodeId": node_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        if result is not None:
            data["result"] = result
        if error:
            data["error"] = error
        if progress is not None:
            data["progress"] = progress
        
        await self.broadcast_to_session(session_id, "node_status", data)
    
    async def notify_session_created(
        self,
        session_id: str,
        task_id: str,
        complexity: str,
        use_team_mode: bool,
    ):
        await self.broadcast_to_session(session_id, "session_created", {
            "sessionId": session_id,
            "taskId": task_id,
            "complexity": complexity,
            "useTeamMode": use_team_mode,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def notify_session_completed(
        self,
        session_id: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ):
        data = {
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat(),
        }
        if output:
            data["output"] = output
        if error:
            data["error"] = error
        
        await self.broadcast_to_session(session_id, "session_completed", data)
    
    async def notify_subtask_status(
        self,
        session_id: str,
        subtask_id: str,
        status: str,
        agent_id: Optional[str] = None,
    ):
        data = {
            "subtaskId": subtask_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        if agent_id:
            data["agentId"] = agent_id
        
        await self.broadcast_to_session(session_id, "subtask_status", data)
    
    async def notify_log(
        self,
        session_id: str,
        level: str,
        message: str,
        node_id: Optional[str] = None,
    ):
        data = {
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        if node_id:
            data["nodeId"] = node_id
        
        await self.broadcast_to_session(session_id, "log", data)
    
    def get_client_count(self, session_id: Optional[str] = None) -> int:
        if session_id:
            return len(self._session_clients.get(session_id, set()))
        return len(self._clients)
    
    async def disconnect_session(self, session_id: str):
        async with self._lock:
            client_ids = self._session_clients.get(session_id, set()).copy()
        
        for client_id in client_ids:
            await self.unsubscribe(client_id)


progress_streamer = ProgressStreamer()
