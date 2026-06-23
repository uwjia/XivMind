import logging
import re
from collections import Counter
from typing import Any, Dict, List

from app.db.base import PaperRepository
from app.db.subject_utils import DEFAULT_SUBJECT
from app.services.paper_service import PaperService

logger = logging.getLogger(__name__)


class AuthorProfileService:
    def __init__(self, paper_service: PaperService):
        self.paper_service = paper_service

    def get_author_profile(self, author: str, subject: str = DEFAULT_SUBJECT) -> Dict[str, Any]:
        result = self.paper_service.query_papers_by_author(author, max_results=1000, subject=subject)
        papers = result.get("papers", [])
        
        if not papers:
            return self._empty_profile(author)
        
        years = self._extract_years(papers)
        categories = self._analyze_categories(papers)
        yearly_papers = self._analyze_yearly_papers(papers)
        collaborators = self._analyze_collaborators(papers, author)
        keywords = self._extract_keywords(papers)
        title_keywords = self._extract_title_keywords(papers)
        
        return {
            "name": author,
            "total_papers": len(papers),
            "first_paper_year": min(years) if years else None,
            "latest_paper_year": max(years) if years else None,
            "active_years": len(set(years)) if years else 0,
            "categories": categories,
            "yearly_papers": yearly_papers,
            "collaborators": collaborators,
            "keywords": keywords,
            "title_keywords": title_keywords,
        }

    def _empty_profile(self, author: str) -> Dict[str, Any]:
        return {
            "name": author,
            "total_papers": 0,
            "first_paper_year": None,
            "latest_paper_year": None,
            "active_years": 0,
            "categories": [],
            "yearly_papers": [],
            "collaborators": [],
            "keywords": [],
            "title_keywords": [],
        }

    def _extract_years(self, papers: List[Dict]) -> List[int]:
        years = []
        for paper in papers:
            published = paper.get("published", "")
            if published:
                try:
                    year = int(str(published)[:4])
                    years.append(year)
                except (ValueError, TypeError):
                    continue
        return years

    def _analyze_categories(self, papers: List[Dict]) -> List[Dict]:
        category_counter = Counter()
        category_names = self._get_category_names()
        
        for paper in papers:
            primary = paper.get("primary_category", "")
            if primary:
                category_counter[primary] += 1
            
            categories = paper.get("categories", [])
            if isinstance(categories, list):
                for cat in categories:
                    if cat and cat != primary:
                        category_counter[cat] += 1
        
        total = sum(category_counter.values())
        result = []
        
        for cat, count in category_counter.most_common(10):
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            result.append({
                "category": cat,
                "name": category_names.get(cat, cat),
                "count": count,
                "percentage": percentage,
            })
        
        return result

    def _analyze_yearly_papers(self, papers: List[Dict]) -> List[Dict]:
        year_counter = Counter()
        
        for paper in papers:
            published = paper.get("published", "")
            if published:
                try:
                    year = int(str(published)[:4])
                    year_counter[year] += 1
                except (ValueError, TypeError):
                    continue
        
        result = []
        for year in sorted(year_counter.keys()):
            result.append({
                "year": year,
                "count": year_counter[year],
            })
        
        return result

    def _analyze_collaborators(self, papers: List[Dict], author: str) -> List[Dict]:
        collaborator_counter = Counter()
        
        for paper in papers:
            authors = paper.get("authors", [])
            if isinstance(authors, list):
                for coauthor in authors:
                    if coauthor and coauthor != author:
                        collaborator_counter[coauthor] += 1
        
        result = []
        for name, count in collaborator_counter.most_common(50):
            result.append({
                "name": name,
                "collaboration_count": count,
            })
        
        return result

    def _extract_keywords(self, papers: List[Dict]) -> List[Dict]:
        word_counter = Counter()
        stop_words = self._get_stop_words()
        
        for paper in papers:
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")
            text = f"{title} {abstract}".lower()
            
            words = re.findall(r'\b[a-z]{3,}\b', text)
            
            for word in words:
                if word not in stop_words:
                    word_counter[word] += 1
        
        result = []
        for word, count in word_counter.most_common(20):
            result.append({
                "word": word,
                "frequency": count,
            })
        
        return result

    def _extract_title_keywords(self, papers: List[Dict]) -> List[Dict]:
        word_counter = Counter()
        stop_words = self._get_stop_words()
        
        for paper in papers:
            title = paper.get("title", "")
            text = title.lower()
            
            words = re.findall(r'\b[a-z]{3,}\b', text)
            
            for word in words:
                if word not in stop_words:
                    word_counter[word] += 1
        
        result = []
        for word, count in word_counter.most_common(20):
            result.append({
                "word": word,
                "frequency": count,
            })
        
        return result

    def _get_category_names(self) -> Dict[str, str]:
        return {
            "cs.AI": "Artificial Intelligence",
            "cs.LG": "Machine Learning",
            "cs.CL": "Computation and Language",
            "cs.CV": "Computer Vision",
            "cs.NE": "Neural and Evolutionary Computing",
            "cs.RO": "Robotics",
            "cs.SE": "Software Engineering",
            "cs.DB": "Databases",
            "cs.DC": "Distributed Computing",
            "cs.CR": "Cryptography and Security",
            "cs.IR": "Information Retrieval",
            "cs.MM": "Multimedia",
            "cs.HC": "Human-Computer Interaction",
            "cs.SY": "Systems and Control",
            "cs.IT": "Information Theory",
            "cs.DS": "Data Structures and Algorithms",
            "cs.GT": "Computer Science and Game Theory",
            "cs.MA": "Multiagent Systems",
            "cs.NI": "Networking and Internet Architecture",
            "cs.PL": "Programming Languages",
            "stat.ML": "Machine Learning (Statistics)",
            "math.OC": "Optimization and Control",
            "physics.comp-ph": "Computational Physics",
            "q-bio.QM": "Quantitative Methods",
            "q-fin.CP": "Computational Finance",
        }

    def _get_stop_words(self) -> set:
        return {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can", "need",
            "this", "that", "these", "those", "it", "its", "they", "them",
            "their", "we", "our", "you", "your", "he", "she", "him", "her",
            "his", "which", "who", "whom", "what", "where", "when", "why", "how",
            "all", "each", "every", "both", "few", "more", "most", "other",
            "some", "such", "no", "not", "only", "same", "so", "than", "too",
            "very", "just", "also", "now", "here", "there", "then", "once",
            "paper", "propose", "propose", "proposed", "proposes", "method",
            "methods", "approach", "approaches", "model", "models", "result",
            "results", "study", "studies", "show", "shows", "showed", "shown",
            "using", "used", "use", "uses", "based", "new", "novel", "present",
            "presents", "presented", "work", "works", "problem", "problems",
            "task", "tasks", "data", "dataset", "datasets", "experiment",
            "experiments", "performance", "analysis", "propose", "provides",
            "provide", "provided", "however", "therefore", "furthermore",
            "moreover", "addition", "given", "well", "one", "two", "three",
            "four", "five", "first", "second", "third", "many", "several",
        }
