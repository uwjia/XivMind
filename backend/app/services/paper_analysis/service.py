import json
import logging
import re
from typing import Optional, List, Dict, Any, AsyncGenerator

from app.services.llm_service import llm_service
from app.services.paper_service import PaperService
from .prompts import ANALYSIS_PROMPTS
from .types import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisType,
    KeyPoint,
    QuestionAndConclusion,
)

logger = logging.getLogger(__name__)


ANALYSIS_TYPE_MAPPING = {
    AnalysisType.FULL: ["summary", "keypoints", "methodology", "questions_conclusions"],
    AnalysisType.SUMMARY: ["summary"],
    AnalysisType.KEYPOINTS: ["keypoints"],
    AnalysisType.METHODOLOGY: ["methodology"],
    AnalysisType.QUESTIONS: ["questions_conclusions"],
}

DEFAULT_ANALYSIS_TYPES = ["summary"]


def _create_summary_parser():
    def parser(parsed: Dict[str, Any]) -> Dict[str, Any]:
        return {"summary": parsed.get("summary", "")}
    return parser


def _create_keypoints_parser():
    def _parse_key_points(data: Any) -> Optional[List[KeyPoint]]:
        if not data or not isinstance(data, list):
            return None
        
        return [
            KeyPoint(
                title=item.get("title", ""),
                description=item.get("description", ""),
                importance=item.get("importance", "medium")
            )
            for item in data
            if isinstance(item, dict)
        ]

    def parser(parsed: Dict[str, Any]) -> Dict[str, Any]:
        key_points = _parse_key_points(parsed.get("key_points"))
        return {"key_points": [kp.model_dump() for kp in key_points] if key_points else []}
    return parser


def _create_methodology_parser():
    def parser(parsed: Dict[str, Any]) -> Dict[str, Any]:
        return {"methodology": parsed.get("methodology", "")}
    return parser


def _create_questions_conclusions_parser():
    def _parse_questions_conclusions(data: Any) -> Optional[List[QuestionAndConclusion]]:
        if not data or not isinstance(data, list):
            return None
        
        return [
            QuestionAndConclusion(
                question=item.get("question", ""),
                conclusion=item.get("conclusion", "")
            )
            for item in data
            if isinstance(item, dict)
        ]
    
    def parser(parsed: Dict[str, Any]) -> Dict[str, Any]:
        qa = _parse_questions_conclusions(parsed.get("questions_and_conclusions"))
        return {"questions_and_conclusions": [q.model_dump() for q in qa] if qa else []}
    return parser


PARSER_MAPPING = {
    "summary": _create_summary_parser(),
    "keypoints": _create_keypoints_parser(),
    "methodology": _create_methodology_parser(),
    "questions_conclusions": _create_questions_conclusions_parser(),
}


class PaperAnalysisService:
    def __init__(self):
        self.paper_service = PaperService()
    
    async def analyze_paper(
        self,
        paper_id: str,
        request: AnalysisRequest
    ) -> AnalysisResult:
        paper = await self._get_paper(paper_id)
        if not paper:
            raise ValueError(f"Paper not found: {paper_id}")
        
        prompt = self._build_prompt(paper, request.analysis_type, request.language)
        
        response = await llm_service.generate(
            prompt=prompt,
            provider=request.service,
            model=request.model
        )
        
        result = self._parse_response(response, paper_id, request)
        
        return result
    
    async def analyze_paper_stream(
        self,
        paper_id: str,
        request: AnalysisRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        paper = await self._get_paper(paper_id)
        if not paper:
            yield {"type": "error", "content": f"Paper not found: {paper_id}"}
            return
        
        analysis_types = self._get_analysis_types(request.analysis_type)
        
        for atype in analysis_types:
            yield {"type": "status", "content": f"Analyzing {atype}..."}
            
            prompt = self._build_prompt(paper, atype, request.language)
            
            try:
                response = await llm_service.generate(
                    prompt=prompt,
                    provider=request.service,
                    model=request.model
                )
                
                parsed = self._parse_partial_response(response, atype)
                yield {"type": atype, "content": parsed}
            except Exception as e:
                logger.error(f"Error analyzing {atype}: {e}")
                yield {"type": "error", "content": f"Failed to analyze {atype}: {str(e)}"}
        
        yield {"type": "done"}
    
    def _get_analysis_types(self, analysis_type: AnalysisType) -> List[str]:
        return ANALYSIS_TYPE_MAPPING.get(analysis_type, DEFAULT_ANALYSIS_TYPES)
    
    async def _get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        try:
            paper = self.paper_service.get_paper_by_id(paper_id)
            return paper
        except Exception as e:
            logger.error(f"Error fetching paper {paper_id}: {e}")
            return None
    
    def _build_prompt(
        self,
        paper: Dict[str, Any],
        analysis_type,
        language: str
    ) -> str:
        title = paper.get("title", "Unknown Title")
        authors = ", ".join(paper.get("authors", [])[:5])
        if len(paper.get("authors", [])) > 5:
            authors += " et al."
        abstract = paper.get("abstract", "No abstract available.")
        
        lang_key = "zh" if language == "zh" else "en"
        if isinstance(analysis_type, AnalysisType):
            type_key = analysis_type.value if analysis_type != AnalysisType.FULL else "full"
        else:
            type_key = analysis_type
        
        logger.info(f"Building prompt: type={type_key}, language={language}, lang_key={lang_key}")
        
        
        prompt_template = ANALYSIS_PROMPTS.get(type_key, ANALYSIS_PROMPTS["summary"])
        prompt = prompt_template[lang_key].format(
            title=title,
            authors=authors,
            abstract=abstract
        )
        
        return prompt
    
    def _parse_response(
        self,
        response: str,
        paper_id: str,
        request: AnalysisRequest
    ) -> AnalysisResult:
        parsed = self._extract_json(response)
        
        return AnalysisResult(
            paper_id=paper_id,
            summary=parsed.get("summary"),
            key_points=self._parse_key_points(parsed.get("key_points")),
            methodology=parsed.get("methodology"),
            questions_and_conclusions=self._parse_questions_conclusions(
                parsed.get("questions_and_conclusions")
            ),
            service_used=request.service or llm_service.settings.LLM_PROVIDER,
            model_used=request.model or llm_service.settings.LLM_MODEL
        )
    
    def _parse_partial_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        parsed = self._extract_json(response)
        parser = PARSER_MAPPING.get(analysis_type)
        if parser:
            return parser(parsed)
        return parsed
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                json_str = re.sub(r'[\x00-\x1f\x7f\x80-\x9f]', '', json_str)
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        
        return {}
    

paper_analysis_service = PaperAnalysisService()
