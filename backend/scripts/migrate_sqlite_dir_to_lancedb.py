#!/usr/bin/env python
"""
SQLite Directory to LanceDB Migration Script

Scan a directory for SQLite database files and migrate all paper data to LanceDB.
Each SQLite database should have 'date_index' and 'papers' tables.

Usage:
    python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir
    python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir --force
    python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir --dry-run
"""

import argparse
import sys
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.sqlite.paper_repo import SQLitePaperRepository
from app.db.lancedb.paper_repo import LanceDBPaperRepository
from app.db.lancedb.client import lancedb_client
from app.config import get_settings


def find_sqlite_files(directory: str, pattern: str = "*.db") -> List[str]:
    """
    Find all SQLite database files in a directory.
    
    Args:
        directory: Path to directory containing SQLite files
        pattern: Glob pattern to match SQLite files (default: *.db)
    
    Returns:
        List of SQLite file paths
    """
    search_pattern = os.path.join(directory, pattern)
    files = glob.glob(search_pattern)
    return sorted(files)


def get_date_range_from_sqlite(
    sqlite_repo: SQLitePaperRepository,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the minimum and maximum dates from SQLite database.
    
    First tries to get dates from date_index table.
    Falls back to papers table if date_index is empty.
    
    Args:
        sqlite_repo: SQLite paper repository instance
    
    Returns:
        Tuple of (min_date, max_date) or (None, None) if no dates found
    """
    date_indexes = sqlite_repo.get_all_date_indexes()
    
    if date_indexes:
        dates = [di["date"] for di in date_indexes if di.get("date")]
        if dates:
            return min(dates), max(dates)
    
    try:
        import sqlite3
        with sqlite3.connect(sqlite_repo._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date(MIN(published)), date(MAX(published)) 
                FROM papers 
                WHERE published IS NOT NULL
            ''')
            result = cursor.fetchone()
            if result and result[0] and result[1]:
                return result[0], result[1]
    except Exception:
        pass
    
    return None, None


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


def check_lancedb_date_exists(lancedb_repo: LanceDBPaperRepository, date: str) -> bool:
    """Check if a date already has data in LanceDB."""
    date_info = lancedb_repo.get_date_index(date)
    return date_info is not None and date_info.get("total_count", 0) > 0


def migrate_single_date(
    sqlite_repo: SQLitePaperRepository,
    lancedb_repo: LanceDBPaperRepository,
    date: str,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 100,
    show_batch_progress: bool = False,
) -> Dict[str, Any]:
    """
    Migrate papers for a single date from SQLite to LanceDB.
    
    Args:
        sqlite_repo: SQLite paper repository
        lancedb_repo: LanceDB paper repository
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
        
        if not force and check_lancedb_date_exists(lancedb_repo, date):
            result["skipped"] = total
            result["error"] = "Already exists (use --force to overwrite)"
            return result
        
        if force:
            lancedb_repo.delete_date_index(date)
        
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
            inserted += lancedb_repo.upsert_papers_batch(batch)
        
        lancedb_repo.insert_date_index(date, total)
        
        result["inserted"] = inserted
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def migrate_date_range(
    sqlite_repo: SQLitePaperRepository,
    lancedb_repo: LanceDBPaperRepository,
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
        lancedb_repo: LanceDB paper repository
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
            iterator = tqdm(dates, desc="  Migrating", unit="date", ncols=80)
        except ImportError:
            pass
    
    show_batch_progress = len(dates) == 1
    
    for date in iterator:
        result = migrate_single_date(
            sqlite_repo=sqlite_repo,
            lancedb_repo=lancedb_repo,
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


def migrate_single_sqlite_db(
    sqlite_path: str,
    lancedb_repo: LanceDBPaperRepository,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 100,
) -> Dict[str, Any]:
    """
    Migrate a single SQLite database to LanceDB.
    
    Args:
        sqlite_path: Path to SQLite database file
        lancedb_repo: LanceDB paper repository
        force: Force overwrite existing data
        dry_run: Only show what would be done
        batch_size: Batch size for insertion
    
    Returns:
        Dict with migration statistics
    """
    result = {
        "sqlite_path": sqlite_path,
        "sqlite_name": os.path.basename(sqlite_path),
        "date_from": None,
        "date_to": None,
        "total_dates": 0,
        "total_papers": 0,
        "total_inserted": 0,
        "total_skipped": 0,
        "errors": [],
        "success": False,
    }
    
    try:
        sqlite_repo = SQLitePaperRepository(sqlite_path)
        
        date_from, date_to = get_date_range_from_sqlite(sqlite_repo)
        
        if not date_from or not date_to:
            result["errors"].append({"error": "No dates found in database"})
            return result
        
        result["date_from"] = date_from
        result["date_to"] = date_to
        
        dates = get_dates_in_range(date_from, date_to)
        result["total_dates"] = len(dates)
        
        stats = migrate_date_range(
            sqlite_repo=sqlite_repo,
            lancedb_repo=lancedb_repo,
            dates=dates,
            force=force,
            dry_run=dry_run,
            batch_size=batch_size,
            show_progress=True,
        )
        
        result["total_papers"] = stats["total_papers"]
        result["total_inserted"] = stats["total_inserted"]
        result["total_skipped"] = stats["total_skipped"]
        result["errors"].extend(stats["errors"])
        result["success"] = True
        
    except Exception as e:
        result["errors"].append({"error": str(e)})
    
    return result


def migrate_all_sqlite_dbs(
    directory: str,
    lancedb_repo: LanceDBPaperRepository,
    pattern: str = "*.db",
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 100,
) -> Dict[str, Any]:
    """
    Migrate all SQLite databases in a directory to LanceDB.
    
    Args:
        directory: Path to directory containing SQLite files
        lancedb_repo: LanceDB paper repository
        pattern: Glob pattern to match SQLite files
        force: Force overwrite existing data
        dry_run: Only show what would be done
        batch_size: Batch size for insertion
    
    Returns:
        Dict with overall migration statistics
    """
    stats = {
        "directory": directory,
        "total_dbs": 0,
        "processed_dbs": 0,
        "total_papers": 0,
        "total_inserted": 0,
        "total_skipped": 0,
        "db_results": [],
        "errors": [],
    }
    
    sqlite_files = find_sqlite_files(directory, pattern)
    stats["total_dbs"] = len(sqlite_files)
    
    if not sqlite_files:
        return stats
    
    iterator = sqlite_files
    if len(sqlite_files) > 1:
        try:
            from tqdm import tqdm
            iterator = tqdm(sqlite_files, desc="Databases", unit="db", ncols=80)
        except ImportError:
            print("Note: Install 'tqdm' for progress bar: pip install tqdm")
            print()
    
    for sqlite_path in iterator:
        db_name = os.path.basename(sqlite_path)
        
        if len(sqlite_files) > 1:
            print(f"\nProcessing: {db_name}")
        
        result = migrate_single_sqlite_db(
            sqlite_path=sqlite_path,
            lancedb_repo=lancedb_repo,
            force=force,
            dry_run=dry_run,
            batch_size=batch_size,
        )
        
        stats["db_results"].append(result)
        stats["processed_dbs"] += 1
        stats["total_papers"] += result["total_papers"]
        stats["total_inserted"] += result["total_inserted"]
        stats["total_skipped"] += result["total_skipped"]
        
        if result["errors"]:
            stats["errors"].append({
                "db": db_name,
                "errors": result["errors"],
            })
        
        if len(sqlite_files) > 1:
            print(f"  Date range: {result['date_from']} to {result['date_to']}")
            print(f"  Papers inserted: {result['total_inserted']}")
            if result["errors"]:
                print(f"  Errors: {len(result['errors'])}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Migrate all SQLite databases in a directory to LanceDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate all SQLite databases in a directory
  python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir
  
  # Force overwrite existing data
  python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir --force
  
  # Dry run to see what would be migrated
  python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir --dry-run
  
  # Use custom file pattern
  python scripts/migrate_sqlite_dir_to_lancedb.py --dir /path/to/sqlite/dir --pattern "*.sqlite"
        """,
    )
    
    parser.add_argument(
        "--dir", "-d",
        type=str,
        required=True,
        help="Directory containing SQLite database files",
    )
    parser.add_argument(
        "--lancedb-path",
        type=str,
        default=None,
        help="Path to LanceDB database (default: from config)",
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
        help="Force overwrite existing data in LanceDB",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.db",
        help="Glob pattern to match SQLite files (default: *.db)",
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"Error: Directory not found: {args.dir}")
        sys.exit(1)
    
    settings = get_settings()
    lancedb_path = args.lancedb_path or getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print("=" * 60)
    print("SQLite Directory to LanceDB Migration")
    print("=" * 60)
    print(f"Source directory: {args.dir}")
    print(f"File pattern: {args.pattern}")
    print(f"LanceDB path: {lancedb_path}")
    print(f"Dry run: {args.dry_run}")
    print(f"Force overwrite: {args.force}")
    print(f"Batch size: {args.batch_size}")
    print()
    
    print("Connecting to LanceDB...")
    try:
        lancedb_client.connect(lancedb_path)
        lancedb_client.init_tables()
        print("Connected to LanceDB successfully")
    except Exception as e:
        print(f"Error: Failed to connect to LanceDB: {e}")
        sys.exit(1)
    
    lancedb_repo = LanceDBPaperRepository()
    
    print()
    print("Scanning for SQLite databases...")
    sqlite_files = find_sqlite_files(args.dir, args.pattern)
    
    if not sqlite_files:
        print(f"No SQLite files found matching pattern '{args.pattern}' in {args.dir}")
        sys.exit(0)
    
    print(f"Found {len(sqlite_files)} SQLite database file(s)")
    print()
    
    print("Date ranges in each database:")
    for sqlite_path in sqlite_files:
        db_name = os.path.basename(sqlite_path)
        try:
            sqlite_repo = SQLitePaperRepository(sqlite_path)
            date_from, date_to = get_date_range_from_sqlite(sqlite_repo)
            if date_from and date_to:
                print(f"  {db_name}: {date_from} to {date_to}")
            else:
                print(f"  {db_name}: No dates found")
        except Exception as e:
            print(f"  {db_name}: Error - {e}")
    print()
    
    if args.dry_run:
        print("DRY RUN - No data will be modified")
        print()
    
    stats = migrate_all_sqlite_dbs(
        directory=args.dir,
        lancedb_repo=lancedb_repo,
        pattern=args.pattern,
        force=args.force,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
    )
    
    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Total databases processed: {stats['processed_dbs']}/{stats['total_dbs']}")
    print(f"Total papers found: {stats['total_papers']}")
    print(f"Total papers {'would be ' if args.dry_run else ''}inserted: {stats['total_inserted']}")
    print(f"Total skipped: {stats['total_skipped']}")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])} databases with errors):")
        for err in stats['errors']:
            print(f"  - {err['db']}:")
            for e in err['errors']:
                if 'date' in e:
                    print(f"      {e['date']}: {e['error']}")
                else:
                    print(f"      {e['error']}")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to actually migrate data.")


if __name__ == "__main__":
    main()
