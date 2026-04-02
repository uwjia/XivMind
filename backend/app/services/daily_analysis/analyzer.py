import json
import re
import logging
from typing import List, Dict, Any, AsyncGenerator

from app.services.llm_service import llm_service
from app.services.daily_analysis.prompts import get_prompt

logger = logging.getLogger(__name__)


class DailyAnalyzer:
    """LLM-based daily paper analysis."""
    
    MAX_PAPERS_IN_PROMPT = 50
    MAX_ABSTRACT_IN_PROMPT = 1000
    MAX_PROCESS_PAPERS = 3000
    
    def __init__(self, provider: str = None, model: str = None, language: str = "en"):
        self.provider = provider
        self.model = model
        self.language = language
    
    async def analyze_summary(
        self, 
        papers: List[Dict], 
        date: str
    ) -> Dict[str, Any]:
        """Generate daily summary."""
        papers_text = self._format_papers(papers)
        
        prompt_template = get_prompt("summary", self.language)
        prompt = prompt_template.format(
            count=len(papers),
            date=date,
            papers=papers_text
        )
        
        response = await self._call_llm(prompt)
        return self._parse_json(response)
    
    async def analyze_trends(
        self, 
        papers: List[Dict]
    ) -> Dict[str, Any]:
        """Identify research trends."""
        papers_text = self._format_papers(papers)
        
        prompt_template = get_prompt("trends", self.language)
        prompt = prompt_template.format(papers=papers_text)
        
        response = await self._call_llm(prompt)
        return self._parse_json(response)
    
    async def identify_high_value_batch(
        self, 
        papers: List[Dict]
    ) -> Dict[str, Any]:
        """Identify high-value papers."""
        papers_text = self._format_papers(papers)
        
        prompt_template = get_prompt("high_value", self.language)
        prompt = prompt_template.format(papers=papers_text)
        
        response = await self._call_llm(prompt)
        return self._parse_json(response)

    async def identify_high_value(
        self, 
        papers: List[Dict]
    ) -> Dict[str, Any]:
        """Identify high-value papers (analyze one by one)."""
        high_value_papers = []
        
        for paper in papers[:self.MAX_PROCESS_PAPERS]:
            paper_result = await self._analyze_single_paper_high_value(paper)
            if paper_result and paper_result.get('confidence', 0) >= 0.7:
                high_value_papers.append(paper_result)
        
        # Sort by confidence
        high_value_papers.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Return top 20
        return {
            "high_value_papers": high_value_papers[:20]
        }
    
    async def identify_high_value_stream(
        self, 
        papers: List[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Identify high-value papers (stream results one by one)."""
        high_value_papers = []
        total_papers = min(len(papers), self.MAX_PROCESS_PAPERS)
        
        for i, paper in enumerate(papers[:self.MAX_PROCESS_PAPERS]):
            yield {
                "type": "progress",
                "content": {
                    "current": i + 1,
                    "total": total_papers,
                    "title": paper.get('title', 'Unknown')
                }
            }
            
            paper_result = await self._analyze_single_paper_high_value(paper)
            if paper_result and paper_result.get('confidence', 0) >= 0.7:
                high_value_papers.append(paper_result)
                yield {
                    "type": "high_value_item",
                    "content": paper_result
                }
        
        # Sort by confidence
        high_value_papers.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Return final sorted result
        yield {
            "type": "high_value_final",
            "content": {
                "high_value_papers": high_value_papers[:20]
            }
        }
    
    async def _analyze_single_paper_high_value(
        self, 
        paper: Dict
    ) -> Dict[str, Any]:
        """Analyze a single paper for high value."""
        paper_id = paper.get('id', 'N/A')
        title = paper.get('title', 'N/A')
        abstract = paper.get('abstract', '')
        
        prompt_template = get_prompt("high_value_single", self.language)
        prompt = prompt_template.format(
            paper_id=paper_id,
            title=title,
            abstract=abstract[:self.MAX_ABSTRACT_IN_PROMPT] + ('...' if len(abstract) > self.MAX_ABSTRACT_IN_PROMPT else '')
        )
        
        response = await self._call_llm(prompt)
        result = self._parse_json(response)
        
        # Ensure paper_id and title are from original data
        if result and not result.get('error'):
            return {
                "paper_id": paper_id,
                "title": title,
                "innovation_type": result.get('innovation_type', ''),
                "innovation_description": result.get('innovation_description', ''),
                "confidence": result.get('confidence', 0)
            }
        
        return None
    
    async def match_interests_batch(
        self, 
        papers: List[Dict], 
        interests: List[str]
    ) -> Dict[str, Any]:
        """Match papers to user interests."""
        papers_text = self._format_papers(papers)
        
        prompt_template = get_prompt("recommend", self.language)
        prompt = prompt_template.format(
            interests=", ".join(interests),
            papers=papers_text
        )
        
        response = await self._call_llm(prompt)
        return self._parse_json(response)

    async def match_interests(
        self, 
        papers: List[Dict], 
        interests: List[str]
    ) -> Dict[str, Any]:
        """Match papers to user interests (analyze one by one)."""
        recommendations = []
        
        for paper in papers[:self.MAX_PROCESS_PAPERS]:
            paper_result = await self._analyze_single_paper_interest(paper, interests)
            if paper_result and paper_result.get('relevance_score', 0) >= 70:
                recommendations.append(paper_result)
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            "recommendations": recommendations,
            "total_matched": len(recommendations)
        }
    
    async def match_interests_stream(
        self, 
        papers: List[Dict], 
        interests: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Match papers to user interests (stream results one by one)."""
        recommendations = []
        total_papers = min(len(papers), self.MAX_PROCESS_PAPERS)
        
        for i, paper in enumerate(papers[:self.MAX_PROCESS_PAPERS]):
            yield {
                "type": "progress",
                "content": {
                    "current": i + 1,
                    "total": total_papers,
                    "title": paper.get('title', 'Unknown')
                }
            }
            
            paper_result = await self._analyze_single_paper_interest(paper, interests)
            if paper_result and paper_result.get('relevance_score', 0) >= 70:
                recommendations.append(paper_result)
                yield {
                    "type": "recommend_item",
                    "content": paper_result
                }
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Return final sorted result
        yield {
            "type": "recommend_final",
            "content": {
                "recommendations": recommendations,
                "total_matched": len(recommendations)
            }
        }
    
    async def _analyze_single_paper_interest(
        self, 
        paper: Dict, 
        interests: List[str]
    ) -> Dict[str, Any]:
        """Analyze a single paper for interest matching."""
        paper_id = paper.get('id', 'N/A')
        title = paper.get('title', 'N/A')
        abstract = paper.get('abstract', '')
        
        prompt_template = get_prompt("recommend_single", self.language)
        prompt = prompt_template.format(
            interests=", ".join(interests),
            paper_id=paper_id,
            title=title,
            abstract=abstract[:self.MAX_ABSTRACT_IN_PROMPT] + ('...' if len(abstract) > self.MAX_ABSTRACT_IN_PROMPT else '')
        )
        
        response = await self._call_llm(prompt)
        result = self._parse_json(response)
        
        # Ensure paper_id and title are from original data
        if result and not result.get('error'):
            return {
                "paper_id": paper_id,
                "title": title,
                "relevance_score": result.get('relevance_score', 0),
                "matched_interests": result.get('matched_interests', []),
                "reason": result.get('reason', '')
            }
        
        return None
    
    def _format_papers(
        self, 
        papers: List[Dict], 
        max_papers: int = None
    ) -> str:
        """Format papers for LLM prompt."""
        limit = max_papers or self.MAX_PAPERS_IN_PROMPT
        formatted = []
        
        for i, paper in enumerate(papers[:limit]):
            paper_id = paper.get('id', 'N/A')
            title = paper.get('title', 'N/A')
            abstract = paper.get('abstract', '')
            
            text = f"[{i+1}]\n"
            text += f"paper_id: \"{paper_id}\"\n"
            text += f"title: \"{title}\"\n"
            text += f"abstract: \"{abstract[:self.MAX_ABSTRACT_IN_PROMPT]}{'...' if len(abstract) > self.MAX_ABSTRACT_IN_PROMPT else ''}\"\n"
            formatted.append(text)
        
        if len(papers) > limit:
            formatted.append(f"\n... and {len(papers) - limit} more papers")
        
        return "\n---\n".join(formatted)
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt."""
        system_prompts = {
            "en": "You are an expert research analyst. Always respond in valid JSON format.",
            "zh": "你是一位专业的研究分析师。请始终以有效的 JSON 格式回复。",
        }
        system_prompt = system_prompts.get(self.language, system_prompts["en"])
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await llm_service.generate(
            prompt=full_prompt,
            provider=self.provider,
            model=self.model,
            max_tokens=8192
        )
        
        return response
    
    def _parse_json(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        cleaned = response.strip()
        
        try:
            if '```json' in cleaned:
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', cleaned)
                if json_match:
                    cleaned = json_match.group(1).strip()
                else:
                    json_match = re.search(r'```json\s*([\s\S]*)', cleaned)
                    if json_match:
                        cleaned = json_match.group(1).strip()
            elif '```' in cleaned:
                json_match = re.search(r'```\s*([\s\S]*?)\s*```', cleaned)
                if json_match:
                    cleaned = json_match.group(1).strip()
                else:
                    json_match = re.search(r'```\s*([\s\S]*)', cleaned)
                    if json_match:
                        cleaned = json_match.group(1).strip()
            
            prefixes = ['InputBorder JSON:', 'JSON:', 'Output:', 'Response:']
            for prefix in prefixes:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            
            if not cleaned.startswith('{'):
                json_match = re.search(r'\{[\s\S]*\}', cleaned)
                if json_match:
                    cleaned = json_match.group()
            
            cleaned = re.sub(r'[\x00-\x1f\x7f\x80-\x9f]', '', cleaned)
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            logger.warning(f"Cleaned content (first 1000 chars): {cleaned[:1000]}")
            logger.warning(f"Original response (first 1000 chars): {response[:1000]}")
        
        return {"error": "Failed to parse response", "raw": response[:1000]}
