#!/usr/bin/env python3
"""
Script to batch fetch papers from arXiv for a date range.

Usage:
    python scripts/fetch_papers.py --start 2026-01-01 --end 2026-02-05 --category "cs*"
    python scripts/fetch_papers.py --start 2026-01-01 --end 2026-01-31
    python scripts/fetch_papers.py --date 2026-01-15
"""

import argparse
import asyncio
import httpx
from datetime import datetime, timedelta
import time
import os
import json


API_BASE = "http://localhost:8000/api/arxiv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "logs")
FAILED_DATES_LOG = os.path.join(LOG_DIR, "failed_dates.json")
RATE_LIMIT_WAIT = 600  # 10 minutes in seconds


def ensure_log_dir():
    """Ensure log directory exists."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def load_failed_dates() -> dict:
    """Load failed dates from log file."""
    ensure_log_dir()
    if os.path.exists(FAILED_DATES_LOG):
        try:
            with open(FAILED_DATES_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"failed_dates": [], "last_updated": None}
    return {"failed_dates": [], "last_updated": None}


def save_failed_dates(data: dict):
    """Save failed dates to log file."""
    ensure_log_dir()
    data["last_updated"] = datetime.now().isoformat()
    with open(FAILED_DATES_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_failed_date(date: str, error: str, category: str):
    """Log a failed date with error details."""
    data = load_failed_dates()
    
    failed_entry = {
        "date": date,
        "error": error,
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "retry_count": 0
    }
    
    existing_dates = [entry["date"] for entry in data["failed_dates"]]
    if date not in existing_dates:
        data["failed_dates"].append(failed_entry)
        save_failed_dates(data)
        print(f"    Logged failed date to {FAILED_DATES_LOG}")
    else:
        for entry in data["failed_dates"]:
            if entry["date"] == date:
                entry["retry_count"] += 1
                entry["error"] = error
                entry["timestamp"] = datetime.now().isoformat()
                break
        save_failed_dates(data)


def remove_failed_date(date: str):
    """Remove a date from failed log after successful fetch."""
    data = load_failed_dates()
    data["failed_dates"] = [entry for entry in data["failed_dates"] if entry["date"] != date]
    save_failed_dates(data)


async def fetch_papers_for_date(client: httpx.AsyncClient, date: str, category: str) -> dict:
    """Fetch papers for a single date."""
    url = f"{API_BASE}/fetch/{date}?category={category}"
    response = await client.post(url)
    return response.json()


async def get_date_indexes(client: httpx.AsyncClient) -> dict:
    """Get all date indexes."""
    url = f"{API_BASE}/date-indexes"
    response = await client.get(url)
    return response.json()


def date_range(start_date: str, end_date: str):
    """Generate dates from start_date to end_date (inclusive)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    while current <= end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)


async def fetch_date_range(
    start_date: str, 
    end_date: str, 
    category: str = "cs*", 
    delay: float = 1.0,
    retry_wait: int = RATE_LIMIT_WAIT
):
    """Fetch papers for a date range."""
    dates = list(date_range(start_date, end_date))
    total_dates = len(dates)
    
    print(f"\n{'='*60}")
    print(f"Fetching papers from {start_date} to {end_date}")
    print(f"Category: {category}")
    print(f"Total dates: {total_dates}")
    print(f"Rate limit wait: {retry_wait}s on failure")
    print(f"{'='*60}\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        success_count = 0
        fail_count = 0
        total_papers = 0
        failed_dates = []
        
        for i, date in enumerate(dates, 1):
            print(f"[{i}/{total_dates}] Fetching {date}...", end=" ", flush=True)
            
            try:
                result = await fetch_papers_for_date(client, date, category)
                
                if result.get("success"):
                    count = result.get("count", 0)
                    total_papers += count
                    success_count += 1
                    print(f"✓ {count} papers")
                    remove_failed_date(date)
                else:
                    error = result.get("error", "Unknown error")
                    fail_count += 1
                    print(f"✗ Error: {error}")
                    log_failed_date(date, error, category)
                    failed_dates.append(date)
                    
                    if fail_count < total_dates:
                        print(f"    Waiting {retry_wait}s to avoid rate limit...")
                        await asyncio.sleep(retry_wait)
                    
            except Exception as e:
                fail_count += 1
                error_msg = str(e)
                print(f"✗ Exception: {error_msg}")
                log_failed_date(date, error_msg, category)
                failed_dates.append(date)
                
                if fail_count < total_dates:
                    print(f"    Waiting {retry_wait}s to avoid rate limit...")
                    await asyncio.sleep(retry_wait)
            
            if i < total_dates and date not in failed_dates:
                await asyncio.sleep(delay)
        
        print(f"\n{'='*60}")
        print("Fetching complete. Getting date indexes...")
        print(f"{'='*60}\n")
        
        indexes = await get_date_indexes(client)
        date_indexes = indexes.get("indexes", [])
        
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")
        print(f"Total dates processed: {total_dates}")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")
        print(f"Total papers fetched: {total_papers}")
        print(f"Date indexes stored: {len(date_indexes)}")
        
        stored_dates = [idx for idx in date_indexes if idx.get("total_count", 0) > 0]
        print(f"Dates with papers: {len(stored_dates)}")
        
        if failed_dates:
            print(f"\nFailed dates (logged to {FAILED_DATES_LOG}):")
            for d in failed_dates:
                print(f"  - {d}")
        
        if stored_dates:
            print(f"\nRecent stored dates:")
            for idx in sorted(stored_dates, key=lambda x: x["date"], reverse=True)[:10]:
                print(f"  {idx['date']}: {idx['total_count']} papers")


async def fetch_single_date(date: str, category: str = "cs*"):
    """Fetch papers for a single date."""
    print(f"\n{'='*60}")
    print(f"Fetching papers for {date}")
    print(f"Category: {category}")
    print(f"{'='*60}\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        result = await fetch_papers_for_date(client, date, category)
        
        if result.get("success"):
            count = result.get("count", 0)
            print(f"✓ Successfully fetched {count} papers for {date}")
            remove_failed_date(date)
        else:
            error = result.get("error", "Unknown error")
            print(f"✗ Failed: {error}")
            log_failed_date(date, error, category)
        
        print(f"\nGetting date indexes...")
        indexes = await get_date_indexes(client)
        date_indexes = indexes.get("indexes", [])
        
        stored_dates = [idx for idx in date_indexes if idx.get("total_count", 0) > 0]
        print(f"Total dates with papers: {len(stored_dates)}")


async def retry_failed_dates(category: str = "cs*", delay: float = 1.0, retry_wait: int = RATE_LIMIT_WAIT):
    """Retry all failed dates from log."""
    data = load_failed_dates()
    failed_dates = data.get("failed_dates", [])
    
    if not failed_dates:
        print("No failed dates to retry.")
        return
    
    print(f"\n{'='*60}")
    print(f"Retrying {len(failed_dates)} failed dates")
    print(f"{'='*60}\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        success_count = 0
        still_failed = []
        
        for i, entry in enumerate(failed_dates, 1):
            date = entry["date"]
            cat = entry.get("category", category)
            
            print(f"[{i}/{len(failed_dates)}] Retrying {date}...", end=" ", flush=True)
            
            try:
                result = await fetch_papers_for_date(client, date, cat)
                
                if result.get("success"):
                    count = result.get("count", 0)
                    print(f"✓ {count} papers")
                    remove_failed_date(date)
                    success_count += 1
                else:
                    error = result.get("error", "Unknown error")
                    print(f"✗ Error: {error}")
                    log_failed_date(date, error, cat)
                    still_failed.append(date)
                    
                    if i < len(failed_dates):
                        print(f"    Waiting {retry_wait}s to avoid rate limit...")
                        await asyncio.sleep(retry_wait)
                    
            except Exception as e:
                print(f"✗ Exception: {e}")
                log_failed_date(date, str(e), cat)
                still_failed.append(date)
                
                if i < len(failed_dates):
                    print(f"    Waiting {retry_wait}s to avoid rate limit...")
                    await asyncio.sleep(retry_wait)
            
            if i < len(failed_dates) and date not in still_failed:
                await asyncio.sleep(delay)
        
        print(f"\n{'='*60}")
        print("Retry Summary")
        print(f"{'='*60}")
        print(f"Total retried: {len(failed_dates)}")
        print(f"Successful: {success_count}")
        print(f"Still failed: {len(still_failed)}")


def show_failed_dates():
    """Show all failed dates from log."""
    data = load_failed_dates()
    failed_dates = data.get("failed_dates", [])
    
    if not failed_dates:
        print("No failed dates logged.")
        return
    
    print(f"\n{'='*60}")
    print(f"Failed Dates ({len(failed_dates)} total)")
    print(f"Last updated: {data.get('last_updated', 'N/A')}")
    print(f"{'='*60}\n")
    
    for entry in failed_dates:
        print(f"  Date: {entry['date']}")
        print(f"    Error: {entry.get('error', 'Unknown')}")
        print(f"    Category: {entry.get('category', 'N/A')}")
        print(f"    Retry count: {entry.get('retry_count', 0)}")
        print(f"    Timestamp: {entry.get('timestamp', 'N/A')}")
        print()


def clear_failed_dates():
    """Clear all failed dates from log."""
    save_failed_dates({"failed_dates": []})
    print("Failed dates log cleared.")


def main():
    parser = argparse.ArgumentParser(
        description="Batch fetch papers from arXiv for a date range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/fetch_papers.py --start 2026-01-01 --end 2026-02-05
    python scripts/fetch_papers.py --start 2026-01-01 --end 2026-01-31 --category "cs.LG"
    python scripts/fetch_papers.py --date 2026-01-15
    python scripts/fetch_papers.py --date 2026-01-15 --category ""
    python scripts/fetch_papers.py --retry
    python scripts/fetch_papers.py --show-failed
    python scripts/fetch_papers.py --clear-failed
        """
    )
    
    parser.add_argument(
        "--start",
        type=str,
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Single date to fetch (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--category",
        type=str,
        default="cs*",
        help='Category to fetch (default: "cs*"). Use "" for all categories.'
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between successful requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--retry-wait",
        type=int,
        default=RATE_LIMIT_WAIT,
        help=f"Wait time in seconds after failure (default: {RATE_LIMIT_WAIT})"
    )
    parser.add_argument(
        "--retry",
        action="store_true",
        help="Retry all failed dates from log"
    )
    parser.add_argument(
        "--show-failed",
        action="store_true",
        help="Show all failed dates from log"
    )
    parser.add_argument(
        "--clear-failed",
        action="store_true",
        help="Clear failed dates log"
    )
    
    args = parser.parse_args()
    
    if args.show_failed:
        show_failed_dates()
    elif args.clear_failed:
        clear_failed_dates()
    elif args.retry:
        asyncio.run(retry_failed_dates(args.category, args.delay, args.retry_wait))
    elif args.date:
        asyncio.run(fetch_single_date(args.date, args.category))
    elif args.start and args.end:
        asyncio.run(fetch_date_range(args.start, args.end, args.category, args.delay, args.retry_wait))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
