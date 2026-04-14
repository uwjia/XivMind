import httpx
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import asyncio

from app.db.factory import get_listings_repository, get_paper_repository
from app.services.arxiv_client import ArxivClient

logger = logging.getLogger(__name__)


class ListingsService:
    """Service for fetching and storing arXiv new listings."""
    
    LISTINGS_URL = "https://arxiv.org/list/cs/new"
    PAGE_SIZE = 2000
    
    def __init__(self):
        self.listings_repo = get_listings_repository()
        self.paper_repo = get_paper_repository()
        self.arxiv_client = ArxivClient()
    
    async def fetch_listings_page(self, skip: int = 0) -> str:
        """
        Fetch the arXiv new listings page HTML.
        
        Args:
            skip: Number of entries to skip (for pagination)
        """
        url = self.LISTINGS_URL
        if skip > 0:
            url = f"{self.LISTINGS_URL}?skip={skip}&show={self.PAGE_SIZE}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
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
            await asyncio.sleep(5.2)
        return papers
    
    async def _fetch_papers_by_ids(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch papers by IDs using arXiv API."""
        if not paper_ids:
            return []
        
        id_list = ','.join(paper_ids)
        url = f"{self.arxiv_client.ARXIV_API_BASE}?id_list={id_list}&max_results={len(paper_ids)}"
        
        logger.info(f"Fetching papers from arXiv API: {url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response_text = await self.arxiv_client._fetch_with_retry_url(client, url)
        
        papers, _ = self.arxiv_client._parse_response(response_text)
        return papers
    
    async def fetch_and_store_listings(self) -> Dict[str, Any]:
        """
        Fetch arXiv new listings page, parse it, and store the papers.
        
        Supports pagination when total_count > PAGE_SIZE.
        For each listing type, first checks if papers already exist in the papers table.
        Only fetches details for papers that don't exist.
        
        Returns:
            Dict with counts and status information
        """
        try:
            html = await self.fetch_listings_page(skip=0)
            
            listings = self.parse_listings_page(html)
            
            listings_date = listings.get('date')
            if not listings_date:
                listings_date = datetime.utcnow().strftime('%Y-%m-%d')
                logger.warning(f"No date found in listings page, using today: {listings_date}")
            
            total_count = listings.get('total_count', 0)
            logger.info(f"Total papers on arXiv: {total_count}")
            
            if total_count > self.PAGE_SIZE:
                num_pages = (total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE
                logger.info(f"Need to fetch {num_pages} pages for {total_count} papers")
                
                for page in range(1, num_pages):
                    skip = page * self.PAGE_SIZE
                    logger.info(f"Fetching page {page + 1}/{num_pages}, skip={skip}")
                    
                    try:
                        page_html = await self.fetch_listings_page(skip=skip)
                        page_listings = self.parse_listings_page(page_html)
                        
                        listings['new'].extend(page_listings.get('new', []))
                        listings['cross'].extend(page_listings.get('cross', []))
                        listings['replacement'].extend(page_listings.get('replacement', []))
                    except Exception as e:
                        logger.error(f"Failed to fetch page {page + 1}: {e}")
            
            logger.info(f"Total papers after pagination: new={len(listings['new'])}, cross={len(listings['cross'])}, replacement={len(listings['replacement'])}")
            
            new_papers = await self._process_listing_type(listings['new'])
            cross_papers = await self._process_listing_type(listings['cross'])
            replacement_papers = await self._process_listing_type_replacement(listings['replacement'])
            
            new_count = self.listings_repo.insert_new_submissions_batch(new_papers, listings_date)
            cross_count = self.listings_repo.insert_cross_submissions_batch(cross_papers, listings_date)
            replacement_count = self.listings_repo.insert_replacement_submissions_batch(replacement_papers, listings_date)
            
            if new_count > 0 or cross_count > 0 or replacement_count > 0:
                self.listings_repo.insert_listings_date_index(
                    date=listings_date,
                    new_count=new_count,
                    cross_count=cross_count,
                    replacement_count=replacement_count
                )
            
            return {
                "success": True,
                "date": listings_date,
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
                "new_count": 0,
                "cross_count": 0,
                "replacement_count": 0,
                "total_count": 0,
            }
    
    def _has_cs_category(self, paper: Dict[str, Any]) -> bool:
        """Check if paper has any CS category."""
        categories = paper.get('categories', [])
        if isinstance(categories, str):
            categories = categories.split()
        return any(cat.startswith('cs.') for cat in categories)
    
    def _filter_cs_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter papers to only include those with CS category."""
        filtered = [p for p in papers if self._has_cs_category(p)]
        if len(filtered) < len(papers):
            logger.info(f"Filtered out {len(papers) - len(filtered)} non-CS papers")
        return filtered
    
    async def _process_listing_type(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
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
        
        existing_papers = []
        existing_ids = set()
        
        try:
            existing_papers = self.paper_repo.get_papers_by_ids(paper_ids)
            existing_ids = {p.get('id') for p in existing_papers if p.get('id')}
            logger.info(f"Batch query found {len(existing_papers)} existing papers")
        except Exception as e:
            logger.warning(f"Failed to batch query papers: {e}, falling back to individual queries")
            for paper_id in paper_ids:
                try:
                    existing_paper = self.paper_repo.get_paper_by_id(paper_id)
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
                cs_new_papers = self._filter_cs_papers(new_papers)
                inserted = self.paper_repo.upsert_papers_batch(cs_new_papers)
                logger.info(f"Inserted {inserted} new papers to papers table")
                
                self._update_date_index_for_new_papers(cs_new_papers)
            except Exception as e:
                logger.error(f"Failed to insert new papers to papers table: {e}")
        
        all_papers = existing_papers + new_papers
        
        return all_papers
    
    def _update_date_index_for_new_papers(self, new_papers: List[Dict[str, Any]]) -> None:
        """
        Update date_index for newly inserted papers.
        
        For each paper's submission date, if the date exists in date_index,
        increment the total_count.
        """
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
                existing_index = self.paper_repo.get_date_index(date_str)
                
                if existing_index:
                    new_total = existing_index.get('total_count', 0) + count
                    self.paper_repo.insert_date_index(date_str, new_total)
                    logger.info(f"Updated date_index for {date_str}: +{count} papers, total={new_total}")
            except Exception as e:
                logger.error(f"Failed to update date_index for {date_str}: {e}")
    
    async def _process_listing_type_replacement(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Process a listing type (replacement).
        
        1. Fetch details for replacement papers
        2. upsert replacement papers to papers table
        """
        if not paper_ids:
            return []
        
        new_papers = await self.fetch_paper_details(paper_ids)
        
        if new_papers:
            try:
                cs_new_papers = self._filter_cs_papers(new_papers)
                inserted = self.paper_repo.upsert_papers_batch(cs_new_papers)
                logger.info(f"Upserted {inserted} replacement papers to papers table")
            except Exception as e:
                logger.error(f"Failed to upsert replacement papers to papers table: {e}")
        
        return new_papers
    
    def get_listings_indexes(self) -> List[Dict[str, Any]]:
        """Get all listings date indexes."""
        return self.listings_repo.get_listings_date_indexes()
    
    def get_listings_by_date(
        self,
        date: str,
        listing_type: str = "new",
        start: int = 0,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Get listings by date and type with pagination."""
        if listing_type == "new":
            papers, total = self.listings_repo.get_new_submissions(date, start, max_results)
        elif listing_type == "cross":
            papers, total = self.listings_repo.get_cross_submissions(date, start, max_results)
        elif listing_type == "replacement":
            papers, total = self.listings_repo.get_replacement_submissions(date, start, max_results)
        else:
            papers, total = [], 0
        
        return {
            "papers": papers,
            "total": total,
            "date": date,
            "listing_type": listing_type,
            "start": start,
            "max_results": max_results,
        }
    
    async def get_latest_listings(self, date: str = None) -> Dict[str, Any]:
        """
        Get the latest day's listings for all three types with auto-refresh.
        
        If date is specified, return papers for that date without auto-refresh.
        If date is not specified and listings_date_index is empty or the latest date 
        is more than 12 hours old, automatically calls fetch_and_store_listings.
        
        Args:
            date: Optional date string (YYYY-MM-DD). If specified, query that date directly.
        
        Returns:
            {
                "date": "2026-04-13",
                "new": [...],
                "cross": [...],
                "replacement": [...],
                "auto_refreshed": true
            }
        """
        auto_refreshed = False
        
        if date:
            new_papers, _ = self.listings_repo.get_new_submissions(date, 0, 10000)
            cross_papers, _ = self.listings_repo.get_cross_submissions(date, 0, 10000)
            replacement_papers, _ = self.listings_repo.get_replacement_submissions(date, 0, 10000)
            
            return {
                "date": date,
                "new": new_papers,
                "cross": cross_papers,
                "replacement": replacement_papers,
                "auto_refreshed": False,
            }
        
        latest_index = self.listings_repo.get_latest_listings_date_index()
        
        need_refresh = False
        if not latest_index:
            logger.info("No listings found, will fetch new data")
            need_refresh = True
        
        if need_refresh:
            result = await self.fetch_and_store_listings()
            if result.get('success'):
                auto_refreshed = True
                latest_index = self.listings_repo.get_latest_listings_date_index()
        
        if not latest_index:
            return {
                "date": "",
                "new": [],
                "cross": [],
                "replacement": [],
                "auto_refreshed": auto_refreshed,
                "error": "Failed to fetch listings"
            }
        
        listings_date = latest_index.get('date', '')
        
        new_papers, _ = self.listings_repo.get_new_submissions(listings_date, 0, 10000)
        cross_papers, _ = self.listings_repo.get_cross_submissions(listings_date, 0, 10000)
        replacement_papers, _ = self.listings_repo.get_replacement_submissions(listings_date, 0, 10000)
        
        return {
            "date": listings_date,
            "new": new_papers,
            "cross": cross_papers,
            "replacement": replacement_papers,
            "auto_refreshed": auto_refreshed,
        }
