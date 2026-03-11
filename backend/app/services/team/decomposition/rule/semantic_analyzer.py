import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ...types import TaskComplexity

logger = logging.getLogger(__name__)


@dataclass
class SemanticFeatures:
    topics: List[str]
    task_types: List[str]
    entities: List[str]
    complexity_score: float
    parallelism_score: float
    keywords: List[str]


@dataclass
class TaskTypePattern:
    name: str
    patterns: List[str]
    weight: float


DEFAULT_TASK_TYPE_PATTERNS = [
    TaskTypePattern("search", ["find", "search", "look for", "retrieve", "查找", "搜索", "寻找"], 1.0),
    TaskTypePattern("analysis", ["analyze", "analysis", "examine", "investigate", "分析", "研究"], 1.0),
    TaskTypePattern("comparison", ["compare", "contrast", "versus", "vs", "difference", "比较", "对比", "差异"], 1.2),
    TaskTypePattern("review", ["review", "survey", "overview", "summary", "综述", "调研", "概述"], 1.0),
    TaskTypePattern("synthesis", ["synthesize", "integrate", "combine", "merge", "综合", "整合"], 1.1),
    TaskTypePattern("writing", ["write", "draft", "compose", "summarize", "写作", "撰写", "总结"], 0.9),
]


COMPLEXITY_FEATURES = {
    "multi_topic_indicators": [
        "multiple", "various", "different", "several", "many", "all of",
        "and", "also", "additionally", "furthermore", "each", "every",
        "多个", "各种", "不同", "以及", "还有", "各个",
    ],
    "high_complexity_indicators": [
        "comprehensive", "thorough", "extensive", "detailed analysis",
        "literature review", "systematic review", "in-depth",
        "全面", "详细分析", "文献综述", "系统性", "深入",
    ],
    "parallel_indicators": [
        "compare", "contrast", "respectively", "separately", "in parallel",
        "比较", "对比", "分别", "并行",
    ],
}


class SemanticAnalyzer:
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        max_topics: int = 5,
    ):
        self._similarity_threshold = similarity_threshold
        self._max_topics = max_topics
        self._embedding_service = None
        self._task_type_patterns = list(DEFAULT_TASK_TYPE_PATTERNS)
        self._topic_cache: Dict[str, List[str]] = {}
    
    def _get_embedding_service(self):
        if self._embedding_service is None:
            from app.services.embedding_service import embedding_service
            self._embedding_service = embedding_service
        return self._embedding_service
    
    def analyze(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SemanticFeatures:
        topics = self.extract_topics(instruction)
        task_types = self.classify_task_types(instruction)
        entities = self.extract_entities(instruction)
        complexity_score = self.calculate_complexity_score(instruction, context)
        parallelism_score = self.calculate_parallelism_score(instruction)
        keywords = self.extract_keywords(instruction)
        
        return SemanticFeatures(
            topics=topics,
            task_types=task_types,
            entities=entities,
            complexity_score=complexity_score,
            parallelism_score=parallelism_score,
            keywords=keywords,
        )
    
    def extract_topics(self, instruction: str) -> List[str]:
        topics = []
        
        comparison_topics = self._extract_comparison_topics(instruction)
        if comparison_topics:
            topics.extend(comparison_topics)
        
        list_topics = self._extract_list_topics(instruction)
        if list_topics:
            topics.extend(list_topics)
        
        paper_topics = self._extract_paper_topics(instruction)
        if paper_topics:
            topics.extend(paper_topics)
        
        if not topics:
            main_topic = self._extract_main_topic(instruction)
            if main_topic:
                topics.append(main_topic)
        
        return list(dict.fromkeys(topics))[:self._max_topics]
    
    def _extract_comparison_topics(self, instruction: str) -> List[str]:
        patterns = [
            r"differences?\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+in|\s+including|\.|,|\$)",
            r"compare\s+(?:and\s+analyze\s+)?(?:the\s+)?(?:differences?\s+between\s+)?(.+?)\s+and\s+(.+?)(?:\s+in|\s+including|\.|,|\$)",
            r"compare\s+(.+?)\s+(?:and|with|vs|versus)\s+(.+?)(?:\.|,|\$)",
            r"(.+?)\s+(?:vs|versus)\s+(.+?)(?:\.|,|\$)",
            r"比较\s+(.+?)\s+(?:和|与)\s+(.+?)(?:。|，|\$)",
            r"(.+?)\s+and\s+(.+?)\s+(?:的)?差异|不同",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                topic1 = match.group(1).strip()
                topic2 = match.group(2).strip()
                return [topic1, topic2]
        
        return []
    
    def _extract_list_topics(self, instruction: str) -> List[str]:
        list_patterns = [
            r"(?:topics?|aspects?|areas?|papers?)\s*[:：]\s*(.+?)(?:\.|\$)",
            r"including\s+(.+?)(?:\.|\$)",
            r"covering\s+(.+?)(?:\.|\$)",
            r"关于\s+(.+?)(?:的|。|\$)",
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                items_str = match.group(1)
                items_str = re.sub(r'\s+and\s+', ', ', items_str, flags=re.IGNORECASE)
                separators = r'[,、，;；]'
                items = re.split(separators, items_str)
                topics = []
                for item in items:
                    item = item.strip()
                    item = re.sub(r'^and\s+', '', item, flags=re.IGNORECASE)
                    if item:
                        topics.append(item)
                if len(topics) >= 2:
                    return topics
        
        return []
    
    def _extract_paper_topics(self, instruction: str) -> List[str]:
        paper_pattern = r'(?:paper|论文|文章)\s*(\d+|[一二三四五六七八九十]+)'
        matches = re.findall(paper_pattern, instruction, re.IGNORECASE)
        
        if matches:
            return [f"Paper {m}" for m in matches]
        
        arxiv_pattern = r'\b(\d{4}\.\d{4,5}(?:v\d+)?)\b'
        arxiv_ids = re.findall(arxiv_pattern, instruction)
        
        if arxiv_ids:
            return [f"arXiv:{aid}" for aid in arxiv_ids]
        
        return []
    
    def _extract_main_topic(self, instruction: str) -> Optional[str]:
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can",
            "about", "on", "in", "at", "to", "for", "of", "with", "by",
            "please", "help", "me", "i", "my", "we", "our", "you", "your",
            "的", "是", "在", "有", "和", "与", "或", "请", "帮", "我",
        }
        
        words = re.findall(r'\b[\w\u4e00-\u9fff]+\b', instruction.lower())
        content_words = [w for w in words if w not in stop_words and len(w) > 1]
        
        if content_words:
            return " ".join(content_words[:3])
        
        return None
    
    def classify_task_types(self, instruction: str) -> List[str]:
        instruction_lower = instruction.lower()
        type_scores: Dict[str, float] = {}
        
        for pattern in self._task_type_patterns:
            score = 0.0
            for keyword in pattern.patterns:
                if keyword.lower() in instruction_lower:
                    score += pattern.weight
            
            if score > 0:
                type_scores[pattern.name] = score
        
        if type_scores:
            sorted_types = sorted(
                type_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [t[0] for t in sorted_types[:3]]
        
        return ["analysis"]
    
    def extract_entities(self, instruction: str) -> List[str]:
        entities = []
        
        arxiv_pattern = r'\b(\d{4}\.\d{4,5}(?:v\d+)?)\b'
        entities.extend(re.findall(arxiv_pattern, instruction))
        
        year_pattern = r'\b((?:19|20)\d{2})\b'
        entities.extend(re.findall(year_pattern, instruction))
        
        quoted_pattern = r'[""「」『』]([^""「」『』]+)[""「」『』]'
        entities.extend(re.findall(quoted_pattern, instruction))
        
        return list(dict.fromkeys(entities))[:10]
    
    def calculate_complexity_score(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        score = 0.0
        instruction_lower = instruction.lower()
        
        multi_topic_count = sum(
            1 for indicator in COMPLEXITY_FEATURES["multi_topic_indicators"]
            if indicator in instruction_lower
        )
        score += multi_topic_count * 0.15
        
        high_complexity_count = sum(
            1 for indicator in COMPLEXITY_FEATURES["high_complexity_indicators"]
            if indicator in instruction_lower
        )
        score += high_complexity_count * 0.25
        
        word_count = len(instruction.split())
        if word_count > 50:
            score += 0.2
        elif word_count > 30:
            score += 0.1
        
        if context:
            paper_ids = context.get("paper_ids", [])
            if paper_ids:
                score += min(len(paper_ids) * 0.1, 0.3)
        
        topics = self.extract_topics(instruction)
        score += min(len(topics) * 0.15, 0.3)
        
        return min(score, 1.0)
    
    def calculate_parallelism_score(self, instruction: str) -> float:
        score = 0.0
        instruction_lower = instruction.lower()
        
        parallel_count = sum(
            1 for indicator in COMPLEXITY_FEATURES["parallel_indicators"]
            if indicator in instruction_lower
        )
        score += min(parallel_count * 0.25, 0.5)
        
        topics = self.extract_topics(instruction)
        if len(topics) >= 2:
            score += 0.3
        
        if " and " in instruction_lower or "、".encode() in instruction.encode():
            score += 0.2
        
        return min(score, 1.0)
    
    def extract_keywords(self, instruction: str) -> List[str]:
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can",
            "about", "on", "in", "at", "to", "for", "of", "with", "by",
            "please", "help", "me", "i", "my", "we", "our", "you", "your",
            "的", "是", "在", "有", "和", "与", "或", "请", "帮", "我",
        }
        
        words = re.findall(r'\b[\w\u4e00-\u9fff]+\b', instruction.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return list(dict.fromkeys(keywords))[:10]
    
    def estimate_complexity(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskComplexity:
        score = self.calculate_complexity_score(instruction, context)
        parallelism = self.calculate_parallelism_score(instruction)
        
        combined_score = score * 0.7 + parallelism * 0.3
        
        if combined_score >= 0.7:
            return TaskComplexity.HIGH
        elif combined_score >= 0.5:
            return TaskComplexity.MODERATE
        elif combined_score >= 0.3:
            return TaskComplexity.STANDARD
        else:
            return TaskComplexity.SIMPLE
    
    async def compute_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:
        try:
            embedding_service = self._get_embedding_service()
            
            emb1, _ = embedding_service.encode(text1)
            emb2, _ = embedding_service.encode(text2)
            
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            norm1 = sum(a * a for a in emb1) ** 0.5
            norm2 = sum(b * b for b in emb2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.warning(f"[SemanticAnalyzer] Similarity computation failed: {e}")
            return 0.0
    
    def should_use_team_mode(
        self,
        features: SemanticFeatures,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if features.complexity_score >= 0.5:
            return True
        
        if features.parallelism_score >= 0.4:
            return True
        
        if len(features.topics) >= 2:
            return True
        
        if "comparison" in features.task_types:
            return True
        
        if context:
            paper_ids = context.get("paper_ids", [])
            if paper_ids and len(paper_ids) >= 3:
                return True
        
        return False
