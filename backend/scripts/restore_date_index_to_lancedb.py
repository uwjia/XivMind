#!/usr/bin/env python
"""
Restore date_index from LanceDB papers table.

This script recovers date_index data from the papers table in LanceDB.
It extracts dates from the 'published' field of papers and rebuilds the date_index.

Usage:
    python scripts/restore_date_index.py --date 2024-01-15
    python scripts/restore_date_index.py --date-from 2024-01-01 --date-to 2024-01-31
    python scripts/restore_date_index.py --all
    python scripts/restore_date_index.py --all --force
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.lancedb.client import lancedb_client
from app.db.lancedb.paper_repo import LanceDBPaperRepository


def get_dates_in_range(date_from: str, date_to: str) -> List[str]:
    """Generate list of dates between date_from and date_to (inclusive)."""
    start = datetime.strptime(date_from, "%Y-%m-%d")
    end = datetime.strptime(date_to, "%Y-%m-%d")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    return dates


def get_date_count(lancedb_repo: LanceDBPaperRepository, date: str) -> int:
    """
    Get the count of papers for a specific date.
    
    Args:
        lancedb_repo: LanceDB paper repository
        date: Date to query (YYYY-MM-DD)
    
    Returns:
        Count of papers published on the date.
    """
    try:
        _, total = lancedb_repo.query_papers_by_date(
            date=date,
            start=0,
            max_results=1,
        )
        return total
    except Exception as e:
        print(f"Error querying date {date}: {e}")
        return 0


def get_all_dates_from_papers(lancedb_repo: LanceDBPaperRepository) -> List[str]:
    """
    Get all unique dates from papers table using Lance scanner.
    
    This uses a more efficient approach than loading all data into pandas.
    """
    print("Scanning papers table for unique dates...")
    
    try:
        table = lancedb_repo._get_papers_table()
        lance_ds = table.to_lance()
        
        scanner = lance_ds.scanner(columns=["published"])
        df = scanner.to_table().to_pandas()
        
        dates = set()
        for published in df["published"]:
            if published:
                date_str = published.split("T")[0] if "T" in published else published
                if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
                    dates.add(date_str)
        
        return sorted(dates)
    except Exception as e:
        print(f"Error scanning dates: {e}")
        raise


def check_date_index_exists(lancedb_repo: LanceDBPaperRepository, date: str) -> bool:
    """Check if a date already has data in date_index."""
    date_info = lancedb_repo.get_date_index(date)
    return date_info is not None and date_info.get("total_count", 0) > 0


def restore_single_date(
    lancedb_repo: LanceDBPaperRepository,
    date: str,
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Restore a single date index entry.
    
    Args:
        lancedb_repo: LanceDB paper repository
        date: Date to restore (YYYY-MM-DD)
        force: Force overwrite existing data
        dry_run: Only show what would be done
    
    Returns:
        Dict with restoration statistics
    """
    result = {
        "date": date,
        "count": 0,
        "restored": False,
        "skipped": False,
        "error": None,
    }
    
    try:
        count = get_date_count(lancedb_repo, date)
        result["count"] = count
        
        if count == 0:
            result["skipped"] = True
            result["error"] = "No papers for this date"
            return result
        
        if dry_run:
            result["restored"] = True
            return result
        
        if not force and check_date_index_exists(lancedb_repo, date):
            result["skipped"] = True
            result["error"] = "Already exists (use --force to overwrite)"
            return result
        
        if force:
            lancedb_repo.delete_date_index(date)
        
        lancedb_repo.insert_date_index(date, count)
        result["restored"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def restore_date_range(
    lancedb_repo: LanceDBPaperRepository,
    dates: List[str],
    force: bool = False,
    dry_run: bool = False,
    show_progress: bool = True,
) -> Dict[str, Any]:
    """
    Restore date_index for multiple dates.
    
    Args:
        lancedb_repo: LanceDB paper repository
        dates: List of dates to restore
        force: Force overwrite existing data
        dry_run: Only show what would be done
        show_progress: Show progress bar
    
    Returns:
        Dict with overall restoration statistics
    """
    stats = {
        "total_dates": len(dates),
        "total_restored": 0,
        "total_skipped": 0,
        "total_papers": 0,
        "errors": [],
    }
    
    iterator = dates
    if show_progress and len(dates) > 1:
        try:
            from tqdm import tqdm
            iterator = tqdm(dates, desc="Restoring", unit="date", ncols=80)
        except ImportError:
            print("Note: Install 'tqdm' for progress bar: pip install tqdm")
            print()
    
    for date in iterator:
        result = restore_single_date(
            lancedb_repo=lancedb_repo,
            date=date,
            force=force,
            dry_run=dry_run,
        )
        
        if result["restored"]:
            stats["total_restored"] += 1
            stats["total_papers"] += result["count"]
        elif result["skipped"]:
            stats["total_skipped"] += 1
        
        if result.get("error"):
            stats["errors"].append({
                "date": date,
                "error": result["error"],
            })
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Restore date_index from LanceDB papers table",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Restore a single date
  python scripts/restore_date_index.py --date 2024-01-15
  
  # Restore a date range
  python scripts/restore_date_index.py --date-from 2024-01-01 --date-to 2024-01-31
  
  # Restore all dates from papers table
  python scripts/restore_date_index.py --all
  
  # Dry run to see what would be restored
  python scripts/restore_date_index.py --all --dry-run
  
  # Force overwrite existing date_index entries
  python scripts/restore_date_index.py --all --force
        """,
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="Restore a specific date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-from",
        type=str,
        help="Start date for range restoration (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-to",
        type=str,
        help="End date for range restoration (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Restore all dates from papers table",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without actually doing it",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing date_index entries",
    )
    parser.add_argument(
        "--lancedb-path",
        type=str,
        default=None,
        help="Path to LanceDB database (default: from config)",
    )
    
    args = parser.parse_args()
    
    if not args.date and not args.date_from and not args.date_to and not args.all:
        parser.print_help()
        print("\nError: Must specify --date, --date-from/--date-to, or --all")
        sys.exit(1)
    
    if args.date_from and not args.date_to:
        print("Error: --date-to is required when using --date-from")
        sys.exit(1)
    
    if args.date_to and not args.date_from:
        print("Error: --date-from is required when using --date-to")
        sys.exit(1)
    
    print("=" * 60)
    print("Restore date_index from papers table")
    print("=" * 60)
    print(f"Dry run: {args.dry_run}")
    print(f"Force overwrite: {args.force}")
    print()
    
    print("Connecting to LanceDB...")
    try:
        lancedb_client.connect(args.lancedb_path)
        lancedb_client.init_tables()
        print("Connected to LanceDB successfully")
    except Exception as e:
        print(f"Error: Failed to connect to LanceDB: {e}")
        sys.exit(1)
    
    lancedb_repo = LanceDBPaperRepository()
    
    dates = []
    if args.date:
        dates = [args.date]
        print(f"Mode: Single date - {args.date}")
    elif args.date_from and args.date_to:
        dates = get_dates_in_range(args.date_from, args.date_to)
        print(f"Mode: Date range - {args.date_from} to {args.date_to}")
    elif args.all:
        dates = get_all_dates_from_papers(lancedb_repo)
        print(f"Mode: All dates - {len(dates)} dates found in papers table")
    
    if not dates:
        print("No dates to restore")
        sys.exit(0)
    
    print(f"Total dates to process: {len(dates)}")
    print()
    
    if args.dry_run:
        print("DRY RUN - No data will be modified")
        print()
    
    stats = restore_date_range(
        lancedb_repo=lancedb_repo,
        dates=dates,
        force=args.force,
        dry_run=args.dry_run,
    )
    
    print()
    print("=" * 60)
    print("Restoration Summary")
    print("=" * 60)
    print(f"Total dates processed: {stats['total_dates']}")
    print(f"Total dates {'would be ' if args.dry_run else ''}restored: {stats['total_restored']}")
    print(f"Total skipped: {stats['total_skipped']}")
    print(f"Total papers covered: {stats['total_papers']}")
    
    if stats['errors']:
        print(f"\nErrors/Warnings ({len(stats['errors'])}):")
        for err in stats['errors'][:10]:
            print(f"  - {err['date']}: {err['error']}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to actually restore data.")


if __name__ == "__main__":
    main()
