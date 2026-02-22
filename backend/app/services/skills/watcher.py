import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillWatcher:
    """Watch skills directory for changes and trigger reload."""
    
    def __init__(
        self,
        skills_dir: str,
        on_change: Optional[Callable[[str, str], None]] = None,
        debounce_ms: int = 250
    ):
        self.skills_dir = Path(skills_dir)
        self.on_change = on_change
        self.debounce_ms = debounce_ms
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._pending_changes: Set[str] = set()
        self._last_reload: Optional[datetime] = None
    
    async def start(self):
        """Start watching for changes."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info(f"SkillWatcher started watching: {self.skills_dir}")
    
    async def stop(self):
        """Stop watching for changes."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SkillWatcher stopped")
    
    async def _watch_loop(self):
        """Main watch loop using watchfiles."""
        try:
            from watchfiles import awatch, Change
            
            async for changes in awatch(self.skills_dir):
                if not self._running:
                    break
                
                for change_type, path in changes:
                    path = Path(path)
                    
                    if path.name == "SKILL.md":
                        skill_dir = path.parent.name
                        change_name = "added" if change_type == Change.added else \
                                     "modified" if change_type == Change.modified else \
                                     "deleted"
                        
                        logger.info(f"Detected {change_name}: {skill_dir}/SKILL.md")
                        
                        if self.on_change:
                            self.on_change(skill_dir, change_name)
        
        except ImportError:
            logger.warning("watchfiles not installed, hot reload disabled")
        except Exception as e:
            logger.error(f"Error in watch loop: {e}")
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running


class SkillWatcherSync:
    """Synchronous wrapper for SkillWatcher."""
    
    def __init__(
        self,
        skills_dir: str,
        on_change: Optional[Callable[[str, str], None]] = None,
        debounce_ms: int = 250
    ):
        self.watcher = SkillWatcher(skills_dir, on_change, debounce_ms)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start(self):
        """Start watching in background thread."""
        import threading
        
        def run_watcher():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self.watcher.start())
            self._loop.run_forever()
        
        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop watching."""
        if self._loop:
            self._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.watcher.stop())
            )
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self.watcher.is_running()
