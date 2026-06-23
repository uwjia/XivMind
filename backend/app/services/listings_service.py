import httpx
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import asyncio

from app.db.factory import get_listings_repository, get_paper_repository, get_paper_code_repository
from app.db.subject_utils import DEFAULT_SUBJECT, SUPPORTED_SUBJECTS
from app.services.arxiv_client import ArxivClient
from app.core.utils import extract_code_urls

logger = logging.getLogger(__name__)


class ListingsService:
    """Service for fetching and storing arXiv new listings."""

    PAGE_SIZE = 2000

    def __init__(self):
        self.paper_code_repo = get_paper_code_repository()
        self.arxiv_client = ArxivClient()

    def _get_listings_repo(self, subject: str = DEFAULT_SUBJECT):
        """Get listings repository for specific subject."""
        return get_listings_repository(subject)

    def _get_paper_repo(self, subject: str = DEFAULT_SUBJECT):
        """Get paper repository for specific subject."""
        return get_paper_repository(subject)

    def _get_listings_url(self, subject: str = 'cs') -> str:
        """Get the arXiv new listings URL for a specific subject."""
        return f"https://arxiv.org/list/{subject}/new"
    
    async def fetch_listings_page(self, subject: str = 'cs', skip: int = 0) -> str:
        """
        Fetch the arXiv new listings page HTML.

        Args:
            subject: Subject category (cs, q-fin, stat)
            skip: Number of entries to skip (for pagination)
        """
        url = self._get_listings_url(subject)
        if skip > 0:
            url = f"{url}?skip={skip}&show={self.PAGE_SIZE}"

        logger.info(f"Fetching listings page: {url}")
        headers = self.arxiv_client._get_random_headers()
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched listings page: {url} (size: {len(response.text)} bytes)")
            return response.text
    
    def parse_listings_page(self, html: str) -> Dict[str, Any]:
        """
        Parse the arXiv new listings page and extract paper IDs.
        
        The page structure is:
        - h3 (date header) - contains the publication date
        - h3 + dl pairs for each listing type
        - paging div - contains total count for pagination
        
        Each dl is preceded by an h3 that indicates its type:
        - "New submissions for ..." -> new
        - "Cross submissions ..." -> cross  
        - "Replacement submissions ..." -> replacement
        
        Returns:
            Dict with keys: 'date', 'total_count', 'new', 'cross', 'replacement'
            - date: publication date string (YYYY-MM-DD)
            - total_count: total number of papers (for pagination)
            - new/cross/replacement: lists of arXiv IDs
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'date': None,
            'total_count': 0,
            'new': [],
            'cross': [],
            'replacement': []
        }
        
        content_div = soup.find('div', id='content')
        if not content_div:
            logger.warning("Could not find content div in listings page")
            return result
        
        first_h3 = content_div.find('h3')
        if first_h3:
            date_str = self._extract_date_from_h3(first_h3.get_text())
            if date_str:
                result['date'] = date_str
        
        paging_div = content_div.find('div', class_='paging')
        if paging_div:
            total = self._extract_total_count_from_paging(paging_div.get_text())
            if total:
                result['total_count'] = total
        
        dls = content_div.find_all('dl')
        logger.info(f"Found {len(dls)} dl elements in page")
        
        for dl in dls:
            h3_inside = dl.find('h3')
            if h3_inside:
                h3_text = h3_inside.get_text().lower()
                paper_ids = self._extract_paper_ids_from_dl(dl)
                
                if 'replacement' in h3_text:
                    result['replacement'].extend(paper_ids)
                    logger.info(f"Found replacement dl with {len(paper_ids)} papers, h3: {h3_text[:80]}")
                elif 'cross' in h3_text:
                    result['cross'].extend(paper_ids)
                    logger.info(f"Found cross dl with {len(paper_ids)} papers, h3: {h3_text[:80]}")
                elif 'new' in h3_text:
                    result['new'].extend(paper_ids)
                    logger.info(f"Found new dl with {len(paper_ids)} papers, h3: {h3_text[:80]}")
                else:
                    logger.warning(f"Unknown h3 type, skipping dl: {h3_text[:80]}")
            else:
                logger.warning("Found dl without h3, skipping")
        
        logger.info(f"Parsed listings: date={result['date']}, total={result['total_count']}, new={len(result['new'])}, cross={len(result['cross'])}, replacement={len(result['replacement'])}")
        
        return result
    
    def _extract_date_from_h3(self, h3_text: str) -> Optional[str]:
        """
        Extract date from h3 header text.
        
        Example h3 text: 
        - "Fri, 11 Apr 2025" 
        - "New submissions for Fri, 11 Apr 2025"
        - "Showing new listings for Monday, 13 April 2026"
        Returns date in YYYY-MM-DD format.
        """
        months = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12',
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        month_pattern = '|'.join(months.keys())
        pattern = rf'(\d{{1,2}})\s+({month_pattern})\s+(\d{{4}})'
        match = re.search(pattern, h3_text, re.IGNORECASE)
        
        if match:
            day = match.group(1).zfill(2)
            month = months.get(match.group(2).title(), '01')
            year = match.group(3)
            return f"{year}-{month}-{day}"
        
        return None
    
    def _extract_total_count_from_paging(self, paging_text: str) -> Optional[int]:
        """
        Extract total count from paging div text.
        
        Example paging text: "1-2000 of 760 entries" or "showing 1-50 of 100 entries"
        Returns the total count as integer.
        """
        pattern = r'of\s+(\d+)\s+entries'
        match = re.search(pattern, paging_text, re.IGNORECASE)
        
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_paper_ids_from_dl(self, dl_element) -> List[str]:
        """Extract arXiv paper IDs from a dl element."""
        paper_ids = []
        
        for dt in dl_element.find_all('dt'):
            for link in dt.find_all('a', href=True):
                href = link.get('href', '')
                if '/abs/' in href:
                    match = re.search(r'/abs/(\d+\.\d+)', href)
                    if match:
                        paper_ids.append(match.group(1))
                        break
        
        return paper_ids
    
    async def fetch_paper_details(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch paper details from arXiv API by paper IDs."""
        if not paper_ids:
            return []
        
        papers = []
        batch_size = 100
        
        for i in range(0, len(paper_ids), batch_size):
            batch_ids = paper_ids[i:i + batch_size]
            
            try:
                batch_papers = await self._fetch_papers_by_ids(batch_ids)
                papers.extend(batch_papers)
            except Exception as e:
                logger.error(f"Failed to fetch batch {i//batch_size}: {e}")
                raise
            await asyncio.sleep(5.2)
        return papers
    
    async def _fetch_papers_by_ids(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch papers by IDs using arXiv API."""
        if not paper_ids:
            return []
        
        id_list = ','.join(paper_ids)
        url = f"{self.arxiv_client.ARXIV_API_BASE}?id_list={id_list}&max_results={len(paper_ids)}"
        
        logger.info(f"Fetching papers from arXiv API: {url}")
        
        headers = self.arxiv_client._get_random_headers()
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            response_text = await self.arxiv_client._fetch_with_retry_url(client, url)
        
        papers, _ = self.arxiv_client._parse_response(response_text)
        return papers
    
    async def fetch_and_store_listings(self, subject: str = 'cs') -> Dict[str, Any]:
        """
        Fetch arXiv new listings page, parse it, and store the papers.

        Supports pagination when total_count > PAGE_SIZE.
        For each listing type, first checks if papers already exist in the papers table.
        Only fetches details for papers that don't exist.

        Args:
            subject: Subject category to fetch (cs, q-fin, stat). Default is 'cs'.

        Returns:
            Dict with counts and status information
        """
        if subject not in SUPPORTED_SUBJECTS:
            logger.warning(f"Unsupported subject '{subject}', falling back to 'cs'")
            subject = 'cs'

        try:
            html = await self.fetch_listings_page(subject=subject, skip=0)

            listings = self.parse_listings_page(html)

            listings_date = listings.get('date')
            if not listings_date:
                listings_date = datetime.utcnow().strftime('%Y-%m-%d')
                logger.warning(f"No date found in listings page, using today: {listings_date}")

            total_count = listings.get('total_count', 0)
            logger.info(f"Total papers on arXiv for {subject}: {total_count}")

            if total_count > self.PAGE_SIZE:
                num_pages = (total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE
                logger.info(f"Need to fetch {num_pages} pages for {total_count} papers")

                for page in range(1, num_pages):
                    skip = page * self.PAGE_SIZE
                    logger.info(f"Fetching page {page + 1}/{num_pages}, skip={skip}")

                    try:
                        page_html = await self.fetch_listings_page(subject=subject, skip=skip)
                        page_listings = self.parse_listings_page(page_html)

                        listings['new'].extend(page_listings.get('new', []))
                        listings['cross'].extend(page_listings.get('cross', []))
                        listings['replacement'].extend(page_listings.get('replacement', []))
                    except Exception as e:
                        logger.error(f"Failed to fetch page {page + 1}: {e}")

            logger.info(f"Total papers after pagination: new={len(listings['new'])}, cross={len(listings['cross'])}, replacement={len(listings['replacement'])}")

            new_papers = await self._process_listing_type(listings['new'], subject)
            cross_papers = await self._process_listing_type(listings['cross'], subject)
            replacement_papers = await self._process_listing_type_replacement(listings['replacement'], subject)

            listings_repo = self._get_listings_repo(subject)
            new_count = listings_repo.insert_new_submissions_batch(new_papers, listings_date)
            cross_count = listings_repo.insert_cross_submissions_batch(cross_papers, listings_date)
            replacement_count = listings_repo.insert_replacement_submissions_batch(replacement_papers, listings_date)

            if new_count > 0 or cross_count > 0 or replacement_count > 0:
                listings_repo.insert_listings_date_index(
                    date=listings_date,
                    new_count=new_count,
                    cross_count=cross_count,
                    replacement_count=replacement_count
                )

            return {
                "success": True,
                "date": listings_date,
                "subject": subject,
                "new_count": new_count,
                "cross_count": cross_count,
                "replacement_count": replacement_count,
                "total_count": new_count + cross_count + replacement_count,
            }

        except Exception as e:
            logger.error(f"Failed to fetch and store listings: {e}")
            return {
                "success": False,
                "error": str(e),
                "subject": subject,
                "new_count": 0,
                "cross_count": 0,
                "replacement_count": 0,
                "total_count": 0,
            }
    
    def _has_subject_category(self, paper: Dict[str, Any], subject: str = 'cs') -> bool:
        """Check if paper has any category for the given subject."""
        categories = paper.get('categories', [])
        if isinstance(categories, str):
            categories = categories.split()
        return any(cat.startswith(f'{subject}.') for cat in categories)

    def _filter_subject_papers(self, papers: List[Dict[str, Any]], subject: str = 'cs') -> List[Dict[str, Any]]:
        """Filter papers to only include those with the given subject category."""
        filtered = [p for p in papers if self._has_subject_category(p, subject)]
        if len(filtered) < len(papers):
            logger.info(f"Filtered out {len(papers) - len(filtered)} non-{subject} papers")
        return filtered
    
    async def _process_listing_type(self, paper_ids: List[str], subject: str = 'cs') -> List[Dict[str, Any]]:
        """
        Process a listing type (new/cross).

        1. Batch check which papers already exist in papers table
        2. Fetch details only for papers that don't exist
        3. Store new papers to papers table
        4. Update date_index for affected dates
        5. Return combined list of existing and new papers
        """
        if not paper_ids:
            return []

        paper_repo = self._get_paper_repo(subject)
        existing_papers = []
        existing_ids = set()

        try:
            existing_papers = paper_repo.get_papers_by_ids(paper_ids)
            existing_ids = {p.get('id') for p in existing_papers if p.get('id')}
            logger.info(f"Batch query found {len(existing_papers)} existing papers")
        except Exception as e:
            logger.warning(f"Failed to batch query papers: {e}, falling back to individual queries")
            for paper_id in paper_ids:
                try:
                    existing_paper = paper_repo.get_paper_by_id(paper_id)
                    if existing_paper:
                        existing_papers.append(existing_paper)
                        existing_ids.add(paper_id)
                except Exception:
                    pass

        new_paper_ids = [pid for pid in paper_ids if pid not in existing_ids]

        logger.info(f"Found {len(existing_papers)} existing papers from papers table, {len(new_paper_ids)} new papers to fetch")

        new_papers = await self.fetch_paper_details(new_paper_ids)

        if new_papers:
            try:
                subject_new_papers = self._filter_subject_papers(new_papers, subject)
                inserted = paper_repo.upsert_papers_batch(subject_new_papers)
                logger.info(f"Inserted {inserted} new papers to papers table")

                self._update_date_index_for_new_papers(subject_new_papers, subject)
                self._extract_and_store_code_urls(subject_new_papers)
            except Exception as e:
                logger.error(f"Failed to insert new papers to papers table: {e}")

        all_papers = existing_papers + new_papers

        return all_papers

    async def _process_listing_type_replacement(self, paper_ids: List[str], subject: str = 'cs') -> List[Dict[str, Any]]:
        """
        Process a listing type (replacement).

        1. Fetch details for replacement papers
        2. upsert replacement papers to papers table
        """
        if not paper_ids:
            return []

        paper_repo = self._get_paper_repo(subject)
        new_papers = await self.fetch_paper_details(paper_ids)

        if new_papers:
            try:
                subject_new_papers = self._filter_subject_papers(new_papers, subject)
                inserted = paper_repo.upsert_papers_batch(subject_new_papers)
                logger.info(f"Upserted {inserted} replacement papers to papers table")
                self._extract_and_store_code_urls(subject_new_papers)
            except Exception as e:
                logger.error(f"Failed to upsert replacement papers to papers table: {e}")
        
        return new_papers
    
    def _update_date_index_for_new_papers(self, new_papers: List[Dict[str, Any]], subject: str = DEFAULT_SUBJECT) -> None:
        """
        Update date_index for newly inserted papers.
        
        For each paper's submission date, if the date exists in date_index,
        increment the total_count.
        """
        paper_repo = self._get_paper_repo(subject)
        date_counts: Dict[str, int] = {}
        
        for paper in new_papers:
            published = paper.get('published', '')
            if not published:
                continue
            
            try:
                date_str = published.split('T')[0]
                date_counts[date_str] = date_counts.get(date_str, 0) + 1
            except Exception as e:
                logger.debug(f"Failed to parse published date: {published}, error: {e}")
        
        for date_str, count in date_counts.items():
            try:
                existing_index = paper_repo.get_date_index(date_str)
                
                if existing_index:
                    new_total = existing_index.get('total_count', 0) + count
                    paper_repo.insert_date_index(date_str, new_total)
                    logger.info(f"Updated date_index for {date_str}: +{count} papers, total={new_total}")
            except Exception as e:
                logger.error(f"Failed to update date_index for {date_str}: {e}")
    
    def get_listings_indexes(self, subject: str = DEFAULT_SUBJECT) -> List[Dict[str, Any]]:
        """Get all listings date indexes."""
        listings_repo = self._get_listings_repo(subject)
        return listings_repo.get_listings_date_indexes()
    
    def get_listings_by_date(
        self,
        date: str,
        listing_type: str = "new",
        start: int = 0,
        max_results: int = 50,
        subject: str = DEFAULT_SUBJECT
    ) -> Dict[str, Any]:
        """Get listings by date and type with pagination."""
        listings_repo = self._get_listings_repo(subject)
        if listing_type == "new":
            papers, total = listings_repo.get_new_submissions(date, start, max_results)
        elif listing_type == "cross":
            papers, total = listings_repo.get_cross_submissions(date, start, max_results)
        elif listing_type == "replacement":
            papers, total = listings_repo.get_replacement_submissions(date, start, max_results)
        else:
            papers, total = [], 0
        
        return {
            "papers": papers,
            "total": total,
            "date": date,
            "listing_type": listing_type,
            "start": start,
            "max_results": max_results,
            "subject": subject,
        }
    
    async def get_latest_listings(self, date: str = None, subject: str = 'cs') -> Dict[str, Any]:
        """
        Get the latest day's listings for all three types with auto-refresh.

        If date is specified, return papers for that date without auto-refresh.
        If date is not specified and listings_date_index is empty or the latest date
        is more than 12 hours old, automatically calls fetch_and_store_listings.

        Args:
            date: Optional date string (YYYY-MM-DD). If specified, query that date directly.
            subject: Subject category to fetch (cs, q-fin, stat). Default is 'cs'.

        Returns:
            {
                "date": "2026-04-13",
                "subject": "cs",
                "new": [...],
                "cross": [...],
                "replacement": [...],
                "auto_refreshed": true
            }
        """
        listings_repo = self._get_listings_repo(subject)
        logger.info(f"Getting latest listings for subject: {subject}, date: {date or 'latest'}")
        auto_refreshed = False

        if date:
            new_papers, _ = listings_repo.get_new_submissions(date, 0, 10000)
            cross_papers, _ = listings_repo.get_cross_submissions(date, 0, 10000)
            replacement_papers, _ = listings_repo.get_replacement_submissions(date, 0, 10000)

            return {
                "date": date,
                "subject": subject,
                "new": new_papers,
                "cross": cross_papers,
                "replacement": replacement_papers,
                "auto_refreshed": False,
            }

        latest_index = listings_repo.get_latest_listings_date_index()

        need_refresh = False
        if not latest_index:
            logger.info(f"No listings found for subject '{subject}', will fetch new data")
            need_refresh = True

        if need_refresh:
            logger.info(f"Fetching new listings for subject: {subject}")
            result = await self.fetch_and_store_listings(subject)
            if result.get('success'):
                auto_refreshed = True
                logger.info(f"Successfully fetched {result.get('total_count', 0)} papers for subject '{subject}'")
                latest_index = listings_repo.get_latest_listings_date_index()
            else:
                logger.error(f"Failed to fetch listings for subject '{subject}': {result.get('error')}")
                return {
                    "date": "",
                    "subject": subject,
                    "new": [],
                    "cross": [],
                    "replacement": [],
                    "auto_refreshed": False,
                    "error": result.get('error', 'Failed to fetch listings')
                }

        if not latest_index:
            logger.warning(f"No listings index found after refresh for subject '{subject}'")
            return {
                "date": "",
                "subject": subject,
                "new": [],
                "cross": [],
                "replacement": [],
                "auto_refreshed": auto_refreshed,
                "error": "Failed to fetch listings"
            }

        listings_date = latest_index.get('date', '')
        logger.info(f"Returning listings for date: {listings_date}, subject: {subject}")

        new_papers, _ = listings_repo.get_new_submissions(listings_date, 0, 10000)
        cross_papers, _ = listings_repo.get_cross_submissions(listings_date, 0, 10000)
        replacement_papers, _ = listings_repo.get_replacement_submissions(listings_date, 0, 10000)

        return {
            "date": listings_date,
            "subject": subject,
            "new": new_papers,
            "cross": cross_papers,
            "replacement": replacement_papers,
            "auto_refreshed": auto_refreshed,
        }
    
    def _extract_and_store_code_urls(self, papers: List[Dict[str, Any]]) -> None:
        """
        Extract code URLs from paper abstract and comment, then store them.
        
        Each paper only stores the first code URL found.
        
        Args:
            papers: List of paper dictionaries with abstract and comment fields
        """
        if not papers:
            return
        
        code_records = []
        
        for paper in papers:
            paper_id = paper.get('id')
            if not paper_id:
                continue
            
            abstract = paper.get('abstract', '') or ''
            comment = paper.get('comment', '') or ''
            combined_text = f"{abstract} {comment}"
            
            codes = extract_code_urls(combined_text)
            
            if codes:
                code = codes[0]
                code_records.append({
                    "paper_id": paper_id,
                    "url": code.url,
                    "platform": code.platform.value,
                    "owner": code.owner or "",
                    "repo": code.repo or "",
                    "is_official": True,
                    "stars": 0,
                    "language": "",
                    "fetched_at": datetime.utcnow().isoformat(),
                })
        
        if code_records:
            try:
                upserted = self.paper_code_repo.upsert_paper_codes(code_records)
                logger.info(f"Upserted {upserted} code URLs for {len(papers)} papers")
            except Exception as e:
                logger.error(f"Failed to upsert code URLs: {e}")
    
    def check_papers_with_code(self, paper_ids: List[str]) -> Dict[str, bool]:
        """
        Check which papers have code repositories.
        
        Args:
            paper_ids: List of paper IDs to check.
        
        Returns:
            Dictionary mapping paper_id to boolean (True if has code).
        """
        if not paper_ids:
            return {}
        return self.paper_code_repo.check_batch(paper_ids)
    
    def get_codes_for_papers(self, paper_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get code repositories for multiple papers.
        
        Args:
            paper_ids: List of paper IDs to get codes for.
        
        Returns:
            Dictionary mapping paper_id to code repository (or None if not found).
        """
        if not paper_ids:
            return {}
        return self.paper_code_repo.get_codes_by_paper_ids(paper_ids)
    
    def get_papers_with_code_by_date(self, date: str, subject: str = DEFAULT_SUBJECT) -> Dict[str, Any]:
        """
        Get papers with code repositories for a specific date.

        Args:
            date: Date string (YYYY-MM-DD).
            subject: Subject category (cs, q-fin, stat).

        Returns:
            {
                "date": "2026-04-22",
                "new": [...],
                "cross": [...],
                "replacement": [...]
            }
        """
        listings_repo = self._get_listings_repo(subject)
        new_papers, _ = listings_repo.get_new_submissions(date, 0, 10000)
        cross_papers, _ = listings_repo.get_cross_submissions(date, 0, 10000)
        replacement_papers, _ = listings_repo.get_replacement_submissions(date, 0, 10000)
        
        all_papers = new_papers + cross_papers + replacement_papers
        all_paper_ids = [p.get('id') for p in all_papers if p.get('id')]
        
        if not all_paper_ids:
            return {
                "date": date,
                "new": [],
                "cross": [],
                "replacement": [],
            }
        
        code_status = self.paper_code_repo.check_batch(all_paper_ids)
        paper_ids_with_code = set(pid for pid, has_code in code_status.items() if has_code)
        
        def filter_papers_with_code(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            return [p for p in papers if p.get('id') in paper_ids_with_code]
        
        return {
            "date": date,
            "new": filter_papers_with_code(new_papers),
            "cross": filter_papers_with_code(cross_papers),
            "replacement": filter_papers_with_code(replacement_papers),
        }
