#!/usr/bin/env python
"""
SQLite to Milvus Migration Script

Migrate paper data from SQLite database to Milvus database by date.

Usage:
    python scripts/migrate_sqlite_to_milvus.py --date 2024-01-15
    python scripts/migrate_sqlite_to_milvus.py --date-from 2024-01-01 --date-to 2024-01-31
    python scripts/migrate_sqlite_to_milvus.py --all
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.sqlite.paper_repo import SQLitePaperRepository
from app.db.milvus.paper_repo import MilvusPaperRepository
from app.db.milvus.client import milvus_client
from app.config import get_settings


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


def get_all_dates_from_sqlite(sqlite_repo: SQLitePaperRepository) -> List[str]:
    """Get all dates that have papers in SQLite."""
    date_indexes = sqlite_repo.get_all_date_indexes()
    return [di["date"] for di in date_indexes if di.get("total_count", 0) > 0]


def check_milvus_date_exists(milvus_repo: MilvusPaperRepository, date: str) -> bool:
    """Check if a date already has data in Milvus."""
    date_info = milvus_repo.get_date_index(date)
    return date_info is not None and date_info.get("total_count", 0) > 0


def migrate_single_date(
    sqlite_repo: SQLitePaperRepository,
    milvus_repo: MilvusPaperRepository,
    date: str,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 100,
    show_batch_progress: bool = False,
) -> Dict[str, Any]:
    """
    Migrate papers for a single date from SQLite to Milvus.
    
    Args:
        sqlite_repo: SQLite paper repository
        milvus_repo: Milvus paper repository
        date: Date to migrate (YYYY-MM-DD)
        force: Force overwrite existing data
        dry_run: Only show what would be done, don't actually migrate
        batch_size: Batch size for insertion
        show_batch_progress: Show progress bar for batch insertion
    
    Returns:
        Dict with migration statistics
    """
    result = {
        "date": date,
        "papers_count": 0,
        "inserted": 0,
        "skipped": 0,
        "error": None,
    }
    
    try:
        papers, total = sqlite_repo.query_papers_by_date(
            date=date,
            start=0,
            max_results=100000,
        )
        
        result["papers_count"] = total
        
        if total == 0:
            result["skipped"] = 1
            return result
        
        if dry_run:
            result["inserted"] = total
            return result
        
        if not force and check_milvus_date_exists(milvus_repo, date):
            result["skipped"] = total
            result["error"] = "Already exists (use --force to overwrite)"
            return result
        
        if force:
            milvus_repo.delete_date_index(date)
        
        inserted = 0
        total_batches = (len(papers) + batch_size - 1) // batch_size
        
        batch_iterator = range(0, len(papers), batch_size)
        if show_batch_progress and total_batches > 1:
            try:
                from tqdm import tqdm
                batch_iterator = tqdm(
                    list(batch_iterator),
                    desc=f"  Batches for {date}",
                    unit="batch",
                    leave=False,
                )
            except ImportError:
                pass
        
        for i in batch_iterator:
            batch = papers[i:i + batch_size]
            inserted += milvus_repo.insert_papers_batch(batch)
        
        milvus_repo.insert_date_index(date, total)
        
        result["inserted"] = inserted
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def migrate_date_range(
    sqlite_repo: SQLitePaperRepository,
    milvus_repo: MilvusPaperRepository,
    dates: List[str],
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 100,
    show_progress: bool = True,
) -> Dict[str, Any]:
    """
    Migrate papers for multiple dates.
    
    Args:
        sqlite_repo: SQLite paper repository
        milvus_repo: Milvus paper repository
        dates: List of dates to migrate
        force: Force overwrite existing data
        dry_run: Only show what would be done
        batch_size: Batch size for insertion
        show_progress: Show progress bar
    
    Returns:
        Dict with overall migration statistics
    """
    stats = {
        "total_dates": len(dates),
        "total_papers": 0,
        "total_inserted": 0,
        "total_skipped": 0,
        "errors": [],
    }
    
    iterator = dates
    if show_progress and len(dates) > 1:
        try:
            from tqdm import tqdm
            iterator = tqdm(dates, desc="Migrating", unit="date", ncols=80)
        except ImportError:
            print("Note: Install 'tqdm' for progress bar: pip install tqdm")
            print()
    
    show_batch_progress = len(dates) == 1
    
    for date in iterator:
        result = migrate_single_date(
            sqlite_repo=sqlite_repo,
            milvus_repo=milvus_repo,
            date=date,
            force=force,
            dry_run=dry_run,
            batch_size=batch_size,
            show_batch_progress=show_batch_progress,
        )
        
        stats["total_papers"] += result["papers_count"]
        stats["total_inserted"] += result["inserted"]
        stats["total_skipped"] += result["skipped"]
        
        if result.get("error"):
            stats["errors"].append({
                "date": date,
                "error": result["error"],
            })
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Migrate paper data from SQLite to Milvus by date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate a single date
  python scripts/migrate_sqlite_to_milvus.py --date 2024-01-15
  
  # Migrate a date range
  python scripts/migrate_sqlite_to_milvus.py --date-from 2024-01-01 --date-to 2024-01-31
  
  # Migrate all data from SQLite
  python scripts/migrate_sqlite_to_milvus.py --all
  
  # Dry run to see what would be migrated
  python scripts/migrate_sqlite_to_milvus.py --all --dry-run
  
  # Force overwrite existing data
  python scripts/migrate_sqlite_to_milvus.py --date 2024-01-15 --force
        """,
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="Migrate papers for a specific date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-from",
        type=str,
        help="Start date for range migration (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-to",
        type=str,
        help="End date for range migration (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all data from SQLite",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for insertion (default: 100)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without actually doing it",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing data in Milvus",
    )
    parser.add_argument(
        "--sqlite-db",
        type=str,
        default=None,
        help="Path to SQLite database (default: from config)",
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
    
    settings = get_settings()
    
    sqlite_db_path = args.sqlite_db or settings.SQLITE_DB_PATH
    
    if not os.path.exists(sqlite_db_path):
        print(f"Error: SQLite database not found at {sqlite_db_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("SQLite to Milvus Migration")
    print("=" * 60)
    print(f"SQLite database: {sqlite_db_path}")
    print(f"Dry run: {args.dry_run}")
    print(f"Force overwrite: {args.force}")
    print(f"Batch size: {args.batch_size}")
    print()
    
    sqlite_repo = SQLitePaperRepository(sqlite_db_path)
    
    print("Connecting to Milvus...")
    try:
        milvus_client.connect()
        print("Connected to Milvus successfully")
    except Exception as e:
        print(f"Error: Failed to connect to Milvus: {e}")
        sys.exit(1)
    
    milvus_repo = MilvusPaperRepository()
    
    dates = []
    if args.date:
        dates = [args.date]
        print(f"Mode: Single date - {args.date}")
    elif args.date_from and args.date_to:
        dates = get_dates_in_range(args.date_from, args.date_to)
        print(f"Mode: Date range - {args.date_from} to {args.date_to}")
    elif args.all:
        dates = get_all_dates_from_sqlite(sqlite_repo)
        print(f"Mode: All dates - {len(dates)} dates found in SQLite")
    
    if not dates:
        print("No dates to migrate")
        sys.exit(0)
    
    print(f"Total dates to process: {len(dates)}")
    print()
    
    if args.dry_run:
        print("DRY RUN - No data will be modified")
        print()
    
    if len(dates) == 1:
        print(f"Processing date: {dates[0]}")
    
    stats = migrate_date_range(
        sqlite_repo=sqlite_repo,
        milvus_repo=milvus_repo,
        dates=dates,
        force=args.force,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
    )
    
    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Total dates processed: {stats['total_dates']}")
    print(f"Total papers found: {stats['total_papers']}")
    print(f"Total papers {'would be ' if args.dry_run else ''}inserted: {stats['total_inserted']}")
    print(f"Total skipped: {stats['total_skipped']}")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for err in stats['errors']:
            print(f"  - {err['date']}: {err['error']}")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to actually migrate data.")


if __name__ == "__main__":
    main()
