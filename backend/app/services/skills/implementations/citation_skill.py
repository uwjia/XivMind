from typing import Dict, Any, List, Optional
from ..base import SkillProvider


class CitationSkill(SkillProvider):
    """Generate citation in various formats."""
    
    @property
    def id(self) -> str:
        return "citation"
    
    @property
    def name(self) -> str:
        return "Citation Generator"
    
    @property
    def description(self) -> str:
        return "Generate citations in multiple formats (APA, MLA, Chicago, BibTeX, IEEE)"
    
    @property
    def icon(self) -> str:
        return "quote"
    
    @property
    def category(self) -> str:
        return "writing"
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["APA", "MLA", "Chicago", "BibTeX", "IEEE", "all"],
                    "default": "APA",
                    "description": "Citation format"
                }
            },
            "required": ["format"]
        }
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        format: str = "APA",
        **kwargs
    ) -> Dict[str, Any]:
        papers = context.get("papers", [])
        if not papers:
            return {"error": "No papers provided", "success": False}
        
        paper = papers[0]
        
        if format == "all":
            citations = {
                fmt: self._generate_citation(paper, fmt)
                for fmt in ["APA", "MLA", "Chicago", "BibTeX", "IEEE"]
            }
        else:
            citations = {format: self._generate_citation(paper, format)}
        
        return {
            "paper_id": paper.get("id"),
            "paper_title": paper.get("title", ""),
            "format": format,
            "citations": citations,
            "success": True
        }
    
    def _generate_citation(self, paper: Dict[str, Any], format: str) -> str:
        """Generate citation string."""
        authors = paper.get("authors", [])
        title = paper.get("title", "")
        published = paper.get("published", "")
        year = published[:4] if published else "n.d."
        arxiv_id = paper.get("id", "")
        url = paper.get("abs_url", f"https://arxiv.org/abs/{arxiv_id}")
        
        if format == "APA":
            return self._format_apa(authors, year, title, arxiv_id)
        elif format == "MLA":
            return self._format_mla(authors, title, arxiv_id, year)
        elif format == "Chicago":
            return self._format_chicago(authors, title, arxiv_id, year)
        elif format == "BibTeX":
            return self._format_bibtex(authors, title, year, arxiv_id)
        elif format == "IEEE":
            return self._format_ieee(authors, title, year, arxiv_id)
        
        return ""
    
    def _format_apa(self, authors: List[str], year: str, title: str, arxiv_id: str) -> str:
        if len(authors) == 0:
            author_str = "Unknown"
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 3:
            author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
        else:
            author_str = authors[0] + " et al."
        
        return f"{author_str} ({year}). {title}. arXiv. https://arxiv.org/abs/{arxiv_id}"
    
    def _format_mla(self, authors: List[str], title: str, arxiv_id: str, year: str) -> str:
        if len(authors) == 0:
            author_str = "Unknown"
        elif len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = authors[0] + ", et al."
        
        return f'{author_str}. "{title}." arXiv, {year}, https://arxiv.org/abs/{arxiv_id}.'
    
    def _format_chicago(self, authors: List[str], title: str, arxiv_id: str, year: str) -> str:
        if len(authors) == 0:
            author_str = "Unknown"
        elif len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = authors[0] + " et al."
        
        return f'{author_str}. "{title}." arXiv, {year}. https://arxiv.org/abs/{arxiv_id}.'
    
    def _format_bibtex(self, authors: List[str], title: str, year: str, arxiv_id: str) -> str:
        author_str = " and ".join(authors) if authors else "Unknown"
        key = arxiv_id.replace(".", "_")
        
        return f"""@article{{{key},
  title = {{{title}}},
  author = {{{author_str}}},
  year = {{{year}}},
  journal = {{arXiv preprint arXiv:{arxiv_id}}},
  url = {{https://arxiv.org/abs/{arxiv_id}}}
}}"""
    
    def _format_ieee(self, authors: List[str], title: str, year: str, arxiv_id: str) -> str:
        if len(authors) == 0:
            author_str = "Unknown"
        elif len(authors) <= 6:
            author_str = ", ".join(authors[:-1]) + (" and " if len(authors) > 1 else "") + authors[-1] if len(authors) > 1 else authors[0]
        else:
            author_str = ", ".join(authors[:6]) + ", et al."
        
        return f'{author_str}, "{title}," arXiv preprint arXiv:{arxiv_id}, {year}.'
