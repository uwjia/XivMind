#!/usr/bin/env python3
"""
Script to extract code URLs from existing papers in listings and store them.

This script scans all papers in the listings tables (new, cross, replacement)
and extracts code repository URLs from their abstract and comment fields.

Usage:
    python scripts/extract_code_urls.py                    # Process all dates
    python scripts/extract_code_urls.py --date 2026-01-15  # Process specific date
    python scripts/extract_code_urls.py --start 2026-01-01 --end 2026-01-31  # Date range
    python scripts/extract_code_urls.py --dry-run          # Show what would be done
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set

from app.db.factory import get_listings_repository, get_paper_code_repository
from app.core.utils import extract_code_urls


def get_all_dates(listings_repo) -> List[str]:
    """Get all dates that have listings."""
    indexes = listings_repo.get_listings_date_indexes()
    return [idx.get('date') for idx in indexes if idx.get('date')]


def get_papers_for_date(listings_repo, date: str) -> List[Dict[str, Any]]:
    """Get all papers for a specific date from all three tables."""
    all_papers = []
    
    new_papers, _ = listings_repo.get_new_submissions(date, 0, 10000)
    cross_papers, _ = listings_repo.get_cross_submissions(date, 0, 10000)
    replacement_papers, _ = listings_repo.get_replacement_submissions(date, 0, 10000)
    
    all_papers.extend(new_papers)
    all_papers.extend(cross_papers)
    all_papers.extend(replacement_papers)
    
    return all_papers


def extract_code_records(papers: List[Dict[str, Any]], processed_ids: Set[str]) -> List[Dict[str, Any]]:
    """Extract code records from papers, skipping already processed IDs."""
    code_records = []
    
    for paper in papers:
        paper_id = paper.get('id')
        if not paper_id:
            continue
        
        if paper_id in processed_ids:
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
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
            processed_ids.add(paper_id)
    
    return code_records


def process_date(listings_repo, paper_code_repo, date: str, processed_ids: Set[str], dry_run: bool = False) -> Dict[str, int]:
    """Process a single date and return stats."""
    papers = get_papers_for_date(listings_repo, date)
    
    stats = {
        "total_papers": len(papers),
        "unique_papers": 0,
        "papers_with_code": 0,
        "code_records": 0,
    }
    
    unique_ids = set(p.get('id') for p in papers if p.get('id'))
    stats["unique_papers"] = len(unique_ids)
    
    code_records = extract_code_records(papers, processed_ids)
    stats["papers_with_code"] = len(code_records)
    
    if code_records and not dry_run:
        try:
            inserted = paper_code_repo.upsert_paper_codes(code_records)
            stats["code_records"] = inserted
        except Exception as e:
            print(f"    Error inserting code records: {e}")
            stats["code_records"] = 0
    elif code_records and dry_run:
        stats["code_records"] = len(code_records)
    
    return stats


def date_range(start_date: str, end_date: str):
    """Generate dates from start_date to end_date (inclusive)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    while current <= end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)


def main():
    parser = argparse.ArgumentParser(
        description="Extract code URLs from existing papers in listings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/extract_code_urls.py
    python scripts/extract_code_urls.py --date 2026-01-15
    python scripts/extract_code_urls.py --start 2026-01-01 --end 2026-01-31
    python scripts/extract_code_urls.py --dry-run
        """
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="Process a specific date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date for range processing (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date for range processing (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of dates to process before showing progress (default: 100)"
    )
    
    args = parser.parse_args()
    
    listings_repo = get_listings_repository()
    paper_code_repo = get_paper_code_repository()
    
    if args.dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 60 + "\n")
    
    if args.date:
        dates = [args.date]
    elif args.start and args.end:
        all_dates = get_all_dates(listings_repo)
        range_dates = set(date_range(args.start, args.end))
        dates = [d for d in all_dates if d in range_dates]
    else:
        dates = get_all_dates(listings_repo)
    
    if not dates:
        print("No dates found to process.")
        return
    
    print("\n" + "=" * 60)
    print("Code URL Extraction Script")
    print("=" * 60)
    print(f"Total dates to process: {len(dates)}")
    if args.date:
        print(f"Single date mode: {args.date}")
    elif args.start and args.end:
        print(f"Date range: {args.start} to {args.end}")
    print("=" * 60 + "\n")
    
    processed_ids: Set[str] = set()
    total_stats = {
        "total_papers": 0,
        "unique_papers": 0,
        "papers_with_code": 0,
        "code_records": 0,
    }
    
    for i, date in enumerate(dates, 1):
        stats = process_date(listings_repo, paper_code_repo, date, processed_ids, args.dry_run)
        
        total_stats["total_papers"] += stats["total_papers"]
        total_stats["unique_papers"] += stats["unique_papers"]
        total_stats["papers_with_code"] += stats["papers_with_code"]
        total_stats["code_records"] += stats["code_records"]
        
        if stats["papers_with_code"] > 0:
            status = "DRY RUN" if args.dry_run else "saved"
            print(f"[{i}/{len(dates)}] {date}: {stats['papers_with_code']} papers with code ({status})")
        elif i % args.batch_size == 0:
            print(f"[{i}/{len(dates)}] Processed {i} dates...")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total dates processed: {len(dates)}")
    print(f"Total papers scanned: {total_stats['total_papers']}")
    print(f"Unique papers: {total_stats['unique_papers']}")
    print(f"Papers with code URLs: {total_stats['papers_with_code']}")
    
    if args.dry_run:
        print(f"Code records (would be saved): {total_stats['code_records']}")
    else:
        print(f"Code records saved: {total_stats['code_records']}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
