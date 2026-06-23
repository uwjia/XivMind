import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
import random

from app.config import get_settings

logger = logging.getLogger(__name__)


class ArxivRateLimitError(Exception):
    """Exception raised when arXiv API rate limit is exceeded."""
    
    def __init__(self, message: str, suggested_wait: int = 300):
        super().__init__(message)
        self.suggested_wait = suggested_wait


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


class ArxivClient:
    ARXIV_API_BASE = "https://export.arxiv.org/api/query"
    ARXIV_NS = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def __init__(self):
        self.settings = get_settings()
        self.max_retries = getattr(self.settings, "ARXIV_MAX_RETRIES", 5)
        self.retry_base_delay = getattr(self.settings, "ARXIV_RETRY_BASE_DELAY", 2.0)
        self.batch_size = getattr(self.settings, "ARXIV_BATCH_SIZE", 100)
        self.fetch_delay = getattr(self.settings, "ARXIV_FETCH_DELAY", 15.0)

    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random request headers to avoid rate limiting patterns."""
        user_agent = random.choice(USER_AGENTS)
        accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "en-US,en;q=0.8,zh-CN;q=0.7,zh;q=0.6",
            "en,en-US;q=0.9",
        ]
        return {
            "User-Agent": user_agent,
            "Accept": "application/xml, text/xml, */*",
            "Accept-Language": random.choice(accept_languages),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": random.choice(["no-cache", "max-age=0"]),
        }

    def _get_random_delay(self) -> float:
        """Get a random delay to avoid predictable request patterns."""
        base = self.fetch_delay
        return base + random.uniform(0, 5)

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
                if e.response.status_code == 429:
                    retry_after = e.response.headers.get("Retry-After")
                    suggested_wait = int(retry_after) if retry_after and retry_after.isdigit() else 300
                    
                    logger.error(
                        f"arXiv API rate limited (429). "
                        f"Suggested wait: {suggested_wait}s. "
                        f"Please retry later or reduce request frequency."
                    )
                    raise ArxivRateLimitError(
                        "arXiv API rate limit exceeded. "
                        f"Please wait {suggested_wait} seconds before retrying.",
                        suggested_wait=suggested_wait
                    ) from e
                elif e.response.status_code in (500, 503):
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
                if e.response.status_code == 429:
                    retry_after = e.response.headers.get("Retry-After")
                    suggested_wait = int(retry_after) if retry_after and retry_after.isdigit() else 300
                    
                    logger.error(
                        f"arXiv API rate limited (429). "
                        f"Suggested wait: {suggested_wait}s. "
                        f"Please retry later or reduce request frequency."
                    )
                    raise ArxivRateLimitError(
                        "arXiv API rate limit exceeded. "
                        f"Please wait {suggested_wait} seconds before retrying.",
                        suggested_wait=suggested_wait
                    ) from e
                elif e.response.status_code in (500, 503):
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
        
        headers = self._get_random_headers()
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
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
                
                logger.info(f"Fetching {category or 'all'} papers for {date}, start={start}, url={url}")
                
                try:
                    xml_text = await self._fetch_with_retry_url(client, url)
                except ArxivRateLimitError as e:
                    if all_papers:
                        logger.warning(
                            f"Rate limited after fetching {len(all_papers)} papers. "
                            f"Returning partial results. {e}"
                        )
                        return all_papers
                    raise
                
                papers, total = self._parse_response(xml_text)
                
                if not papers:
                    break
                
                all_papers.extend(papers)
                logger.info(f"Fetched {len(papers)} papers, total so far: {len(all_papers)}")
                
                if len(papers) < self.batch_size:
                    break
                
                start += self.batch_size
                
                delay = self._get_random_delay()
                await asyncio.sleep(delay)
        
        logger.info(f"Total {category or 'all'} papers fetched for {date}: {len(all_papers)}")
        return all_papers
