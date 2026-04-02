import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass

from app.db.factory import get_paper_repository
from app.models.daily_analysis import (
    DailyAnalysisRequest,
    DailyAnalysisResult,
    AnalysisMode,
)
from app.services.daily_analysis.analyzer import DailyAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class AnalysisTask:
    name: str
    mode: AnalysisMode
    status_message: str
    result_type: str
    result_field: str
    requires_interests: bool = False
    is_streaming: bool = False


ANALYSIS_TASKS = [
    AnalysisTask(
        name="summary",
        mode=AnalysisMode.SUMMARY,
        status_message="Generating daily summary...",
        result_type="summary",
        result_field="summary",
    ),
    AnalysisTask(
        name="trends",
        mode=AnalysisMode.TRENDS,
        status_message="Analyzing research trends...",
        result_type="trends",
        result_field="trends",
    ),
    AnalysisTask(
        name="high_value",
        mode=AnalysisMode.HIGH_VALUE,
        status_message="Identifying high-value papers...",
        result_type="high_value",
        result_field="high_value_papers",
        is_streaming=True,
    ),
    AnalysisTask(
        name="recommend",
        mode=AnalysisMode.RECOMMEND,
        status_message="Matching papers to your interests...",
        result_type="recommendations",
        result_field="recommendations",
        requires_interests=True,
        is_streaming=True,
    ),
]


class DailyAnalysisService:
    """Service for daily paper analysis."""
    
    def __init__(self):
        self.paper_repo = None
        self._analyzer_methods: Dict[str, Callable] = {}
    
    def _get_paper_repo(self):
        if self.paper_repo is None:
            self.paper_repo = get_paper_repository()
        return self.paper_repo
    
    def _get_papers_by_date(self, date: str) -> List[Dict[str, Any]]:
        paper_repo = self._get_paper_repo()
        papers, total = paper_repo.query_papers_by_date(
            date=date,
            category=None,
            start=0,
            max_results=1000
        )
        return papers
    
    def get_paper_count(self, date: str) -> int:
        """Get the total number of papers for a specific date."""
        paper_repo = self._get_paper_repo()
        _, total = paper_repo.query_papers_by_date(
            date=date,
            category=None,
            start=0,
            max_results=1
        )
        return total
    
    def _get_analyzer_method(self, analyzer: DailyAnalyzer, task_name: str, streaming: bool = False) -> Callable:
        method_map = {
            "summary": analyzer.analyze_summary,
            "trends": analyzer.analyze_trends,
            "high_value": analyzer.identify_high_value_stream if streaming else analyzer.identify_high_value,
            "recommend": analyzer.match_interests_stream if streaming else analyzer.match_interests,
        }
        return method_map[task_name]
    
    def _should_run_task(self, task: AnalysisTask, mode: AnalysisMode, has_interests: bool) -> bool:
        if task.requires_interests and not has_interests:
            return False
        return mode in [AnalysisMode.FULL, task.mode]
    
    async def _execute_task(
        self,
        analyzer: DailyAnalyzer,
        task: AnalysisTask,
        papers: List[Dict[str, Any]],
        date: str,
        user_interests: List[str] = None,
    ) -> Dict[str, Any]:
        method = self._get_analyzer_method(analyzer, task.name)
        
        args_map = {
            "summary": lambda: (papers, date),
            "trends": lambda: (papers,),
            "high_value": lambda: (papers,),
            "recommend": lambda: (papers, user_interests),
        }
        
        args = args_map[task.name]()
        return await method(*args)
    
    def _apply_result(self, result: DailyAnalysisResult, task: AnalysisTask, task_result: Dict[str, Any]):
        result_map = {
            "summary": lambda r: (
                setattr(result, "summary", r.get("summary")),
                setattr(result, "main_themes", r.get("main_themes")),
            ),
            "trends": lambda r: setattr(result, "trends", r.get("trends", [])),
            "high_value": lambda r: setattr(result, "high_value_papers", r.get("high_value_papers", [])),
            "recommend": lambda r: setattr(result, "recommendations", r.get("recommendations", [])),
        }
        result_map[task.name](task_result)
    
    async def analyze(self, request: DailyAnalysisRequest) -> DailyAnalysisResult:
        papers = self._get_papers_by_date(request.date)
        
        if not papers:
            raise ValueError(f"No papers found for date: {request.date}")
        
        total_papers = len(papers)
        max_papers = min(request.max_papers, total_papers)
        papers = papers[:max_papers]
        
        analyzer = DailyAnalyzer(
            provider=request.provider,
            model=request.model,
            language=request.language
        )
        
        result = DailyAnalysisResult(
            date=request.date,
            total_papers=len(papers),
            analyzed_at=datetime.now().isoformat(),
            model_used=request.model or "default"
        )
        
        has_interests = bool(request.user_interests)
        
        for task in ANALYSIS_TASKS:
            if not self._should_run_task(task, request.mode, has_interests):
                continue
            
            try:
                task_result = await self._execute_task(
                    analyzer, task, papers, request.date, request.user_interests
                )
                self._apply_result(result, task, task_result)
            except Exception as e:
                logger.error(f"Error in {task.name} analysis: {e}")
        
        return result
    
    async def analyze_stream(
        self, 
        request: DailyAnalysisRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        papers = self._get_papers_by_date(request.date)
        
        if not papers:
            yield {"type": "error", "content": f"No papers found for date: {request.date}"}
            return
        
        total_papers = len(papers)
        max_papers = min(request.max_papers, total_papers)
        papers = papers[:max_papers]
        
        analyzer = DailyAnalyzer(
            provider=request.provider,
            model=request.model,
            language=request.language
        )
        
        yield {
            "type": "status", 
            "content": f"Found {total_papers} papers, starting analysis {max_papers} papers from {request.date} ..."
        }
        
        has_interests = bool(request.user_interests)
        
        for task in ANALYSIS_TASKS:
            if not self._should_run_task(task, request.mode, has_interests):
                continue
            
            yield {"type": "status", "content": task.status_message}
            
            try:
                if task.is_streaming:
                    # Use streaming method for incremental results
                    method = self._get_analyzer_method(analyzer, task.name, streaming=True)
                    args_map = {
                        "high_value": lambda: (papers,),
                        "recommend": lambda: (papers, request.user_interests),
                    }
                    args = args_map[task.name]()
                    
                    async for item in method(*args):
                        yield item
                else:
                    # Non-streaming task
                    task_result = await self._execute_task(
                        analyzer, task, papers, request.date, request.user_interests
                    )
                    yield {"type": task.result_type, "content": task_result}
            except Exception as e:
                logger.error(f"Error in {task.name} analysis: {e}")
                yield {"type": "error", "content": f"{task.name.title()} analysis failed: {str(e)}"}
        
        yield {"type": "done", "content": "Analysis complete"}


daily_analysis_service = DailyAnalysisService()
