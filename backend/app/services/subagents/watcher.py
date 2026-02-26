import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime
from collections import defaultdict

from .types import AGENT_FILE_NAME

logger = logging.getLogger(__name__)


class SubAgentWatcher:
    """Watcher for SubAgent configuration file changes."""
    
    def __init__(
        self,
        agents_dir: str,
        on_change: Callable[[str, str], None],
        debounce_ms: int = 250,
    ):
        self.agents_dir = Path(agents_dir)
        self.on_change = on_change
        self.debounce_ms = debounce_ms
        self._running = False
        self._last_modified: dict = defaultdict(float)
        self._check_interval = 1.0
    
    async def start(self) -> None:
        if not self.agents_dir.exists():
            logger.warning(f"SubAgents directory does not exist: {self.agents_dir}")
            return
        
        self._running = True
        self._last_modified.clear()
        
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_file = agent_dir / AGENT_FILE_NAME
                if agent_file.exists():
                    self._last_modified[str(agent_dir)] = agent_file.stat().st_mtime
        
        logger.info(f"SubAgent watcher started for {self.agents_dir}")
        
        while self._running:
            try:
                await self._check_changes()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SubAgent watcher: {e}")
                await asyncio.sleep(self._check_interval * 2)
    
    async def _check_changes(self) -> None:
        current_dirs = set()
        
        if not self.agents_dir.exists():
            return
        
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            current_dirs.add(str(agent_dir))
            agent_file = agent_dir / AGENT_FILE_NAME
            
            if not agent_file.exists():
                continue
            
            try:
                current_mtime = agent_file.stat().st_mtime
                last_mtime = self._last_modified.get(str(agent_dir), 0)
                
                if current_mtime > last_mtime:
                    self._last_modified[str(agent_dir)] = current_mtime
                    
                    if last_mtime > 0:
                        await self._debounce(str(agent_dir), "modified")
            
            except OSError as e:
                logger.warning(f"Could not check {agent_file}: {e}")
        
        deleted_dirs = set(self._last_modified.keys()) - current_dirs
        for deleted_dir in deleted_dirs:
            del self._last_modified[deleted_dir]
            await self._debounce(deleted_dir, "deleted")
    
    async def _debounce(self, agent_dir: str, change_type: str) -> None:
        await asyncio.sleep(self.debounce_ms / 1000.0)
        
        try:
            self.on_change(agent_dir, change_type)
        except Exception as e:
            logger.error(f"Error in on_change callback: {e}")
    
    def stop(self) -> None:
        self._running = False
        logger.info("SubAgent watcher stopped")
    
    def is_running(self) -> bool:
        return self._running
