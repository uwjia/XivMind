import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class ArxivClient:
    ARXIV_API_BASE = "https://export.arxiv.org/api/query"
    ARXIV_NS = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def __init__(self):
        self.settings = get_settings()
        self.max_retries = getattr(self.settings, "ARXIV_MAX_RETRIES", 3)
        self.retry_base_delay = getattr(self.settings, "ARXIV_RETRY_BASE_DELAY", 1.0)
        self.batch_size = getattr(self.settings, "ARXIV_BATCH_SIZE", 500)

    def _date_to_arxiv_format(self, date_str: str) -> tuple[str, str]:
        """
        Convert '2026-01-24' to arXiv API format.
        Returns: ('20260124000000', '20260124235959')
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        start = date_obj.strftime("%Y%m%d000000")
        end = date_obj.strftime("%Y%m%d235959")
        return start, end

    async def _fetch_with_retry(
        self, 
        client: httpx.AsyncClient, 
        params: Dict[str, Any]
    ) -> str:
        """Fetch with exponential backoff retry."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = await client.get(self.ARXIV_API_BASE, params=params)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (500, 503):
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.warning(
                        f"arXiv API returned {e.response.status_code}, retrying in {delay}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                    last_error = e
                else:
                    raise
            except httpx.RequestError as e:
                delay = self.retry_base_delay * (2 ** attempt)
                logger.warning(
                    f"Request error: {e}, retrying in {delay}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                await asyncio.sleep(delay)
                last_error = e
        
        raise last_error or Exception("Max retries exceeded")

    async def _fetch_with_retry_url(
        self, 
        client: httpx.AsyncClient, 
        url: str
    ) -> str:
        """Fetch with exponential backoff retry using direct URL (no encoding)."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (500, 503):
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.warning(
                        f"arXiv API returned {e.response.status_code}, retrying in {delay}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                    last_error = e
                else:
                    raise
            except httpx.RequestError as e:
                delay = self.retry_base_delay * (2 ** attempt)
                logger.warning(
                    f"Request error: {e}, retrying in {delay}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                await asyncio.sleep(delay)
                last_error = e
        
        raise last_error or Exception("Max retries exceeded")

    def _parse_entry(self, entry: ET.Element) -> Dict[str, Any]:
        """Parse a single arXiv entry to dict."""
        def get_text(parent: ET.Element, tag: str, ns: str = "atom") -> str:
            elem = parent.find(f"{{{self.ARXIV_NS[ns]}}}{tag}")
            return elem.text.strip() if elem is not None and elem.text else ""
        
        def get_attr(parent: ET.Element, tag: str, attr: str, ns: str = "atom") -> str:
            elem = parent.find(f"{{{self.ARXIV_NS[ns]}}}{tag}")
            return elem.get(attr, "") if elem is not None else ""
        
        id_elem = entry.find(f"{{{self.ARXIV_NS['atom']}}}id")
        full_id = id_elem.text if id_elem is not None else ""
        arxiv_id = full_id.split("/")[-1] if full_id else ""
        arxiv_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
        
        title = get_text(entry, "title")
        summary = get_text(entry, "summary")
        published = get_text(entry, "published")
        updated = get_text(entry, "updated")
        comment = get_text(entry, "comment", "arxiv")
        journal_ref = get_text(entry, "journal_ref", "arxiv")
        doi = get_text(entry, "doi", "arxiv")
        
        authors = []
        for author in entry.findall(f"{{{self.ARXIV_NS['atom']}}}author"):
            name_elem = author.find(f"{{{self.ARXIV_NS['atom']}}}name")
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())
        
        categories = []
        primary_category = ""
        for cat in entry.findall(f"{{{self.ARXIV_NS['atom']}}}category"):
            term = cat.get("term", "")
            if term:
                categories.append(term)
        
        primary_cat_elem = entry.find(f"{{{self.ARXIV_NS['arxiv']}}}primary_category")
        if primary_cat_elem is not None:
            primary_category = primary_cat_elem.get("term", "")
        elif categories:
            primary_category = categories[0]
        
        pdf_url = ""
        abs_url = ""
        for link in entry.findall(f"{{{self.ARXIV_NS['atom']}}}link"):
            rel = link.get("rel", "")
            href = link.get("href", "")
            title_attr = link.get("title", "")
            
            if title_attr == "pdf":
                pdf_url = href
            elif rel == "alternate" and "arxiv.org/abs" in href:
                abs_url = href
        
        if not abs_url and arxiv_id:
            abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        if not pdf_url and arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        
        return {
            "id": arxiv_id,
            "title": title,
            "abstract": summary,
            "authors": authors,
            "primary_category": primary_category,
            "categories": categories,
            "published": published,
            "updated": updated,
            "pdf_url": pdf_url,
            "abs_url": abs_url,
            "comment": comment,
            "journal_ref": journal_ref,
            "doi": doi,
        }

    def _parse_response(self, xml_text: str) -> tuple[List[Dict[str, Any]], int]:
        """Parse arXiv API XML response."""
        root = ET.fromstring(xml_text)
        
        total_results = 0
        total_elem = root.find(".//atom:totalResults", self.ARXIV_NS)
        if total_elem is not None and total_elem.text:
            total_results = int(total_elem.text)
        
        papers = []
        for entry in root.findall(f"{{{self.ARXIV_NS['atom']}}}entry"):
            try:
                paper = self._parse_entry(entry)
                if paper.get("id") and paper.get("title"):
                    papers.append(paper)
            except Exception as e:
                logger.warning(f"Error parsing entry: {e}")
        
        return papers, total_results

    async def fetch_all_papers_for_date(self, date: str, category: str = "cs*") -> List[Dict[str, Any]]:
        """
        Fetch ALL papers for a specific date from arXiv.
        Filter by category (default: cs* for all Computer Science).
        """
        start_time, end_time = self._date_to_arxiv_format(date)
        
        all_papers = []
        start = 0
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                if category:
                    url = (
                        f"{self.ARXIV_API_BASE}?"
                        f"search_query=cat:{category}+AND+submittedDate:[{start_time}+TO+{end_time}]&"
                        f"start={start}&"
                        f"max_results={self.batch_size}&"
                        f"sortBy=submittedDate&"
                        f"sortOrder=descending"
                    )
                else:
                    url = (
                        f"{self.ARXIV_API_BASE}?"
                        f"search_query=submittedDate:[{start_time}+TO+{end_time}]&"
                        f"start={start}&"
                        f"max_results={self.batch_size}&"
                        f"sortBy=submittedDate&"
                        f"sortOrder=descending"
                    )
                
                logger.info(f"Fetching {category or 'all'} papers for {date}, start={start}")
                xml_text = await self._fetch_with_retry_url(client, url)
                papers, total = self._parse_response(xml_text)
                
                if not papers:
                    break
                
                all_papers.extend(papers)
                logger.info(f"Fetched {len(papers)} papers, total so far: {len(all_papers)}")
                
                if len(papers) < self.batch_size:
                    break
                
                start += self.batch_size
                
                await asyncio.sleep(0.5)
        
        logger.info(f"Total {category or 'all'} papers fetched for {date}: {len(all_papers)}")
        return all_papers
