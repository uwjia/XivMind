#!/usr/bin/env python3
"""
LanceDB maintenance script for optimizing storage and cleaning up old versions.

Usage:
    python scripts/maintain_lancedb.py --status
    python scripts/maintain_lancedb.py --optimize
    python scripts/maintain_lancedb.py --optimize --tables papers,date_index
    python scripts/maintain_lancedb.py --cleanup --days 0
    python scripts/maintain_lancedb.py --compact
"""

import argparse
import os
import sys
from datetime import timedelta
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.db.lancedb.client import lancedb_client


def get_table_sizes(db_path: str) -> dict:
    """Get the size of each LanceDB table on disk."""
    sizes = {}
    
    if not os.path.exists(db_path):
        return sizes
    
    for table_name in os.listdir(db_path):
        table_path = os.path.join(db_path, table_name)
        if os.path.isdir(table_path) and table_name.endswith('.lance'):
            total_size = 0
            for root, dirs, files in os.walk(table_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            sizes[table_name] = {
                'bytes': total_size,
                'mb': round(total_size / (1024 * 1024), 2),
                'gb': round(total_size / (1024 * 1024 * 1024), 2),
            }
    
    return sizes


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable string."""
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} bytes"


def show_status():
    """Show the current status of LanceDB tables."""
    settings = get_settings()
    db_path = getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print(f"\n{'='*60}")
    print("LanceDB Status")
    print(f"{'='*60}")
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print("\nDatabase directory does not exist.")
        return
    
    lancedb_client.connect(db_path)
    
    table_names = lancedb_client.get_db().table_names()
    
    if not table_names:
        print("\nNo tables found.")
        return
    
    print(f"\nTables found: {len(table_names)}")
    print()
    
    sizes = get_table_sizes(db_path)
    total_size = 0
    
    print(f"{'Table':<25} {'Rows':>12} {'Size':>15}")
    print("-" * 55)
    
    for table_name in sorted(table_names):
        try:
            table = lancedb_client.get_table(table_name)
            row_count = table.count_rows()
        except Exception as e:
            row_count = f"Error: {e}"
        
        size_info = sizes.get(f"{table_name}.lance", {})
        size_str = format_size(size_info.get('bytes', 0))
        total_size += size_info.get('bytes', 0)
        
        print(f"{table_name:<25} {str(row_count):>12} {size_str:>15}")
    
    print("-" * 55)
    print(f"{'Total':<25} {'':<12} {format_size(total_size):>15}")
    print()


def optimize_tables(
    tables: Optional[List[str]] = None,
    cleanup_days: int = 7,
    delete_unverified: bool = False
):
    """
    Optimize LanceDB tables by compacting files and cleaning up old versions.
    
    Args:
        tables: List of table names to optimize. If None, optimize all tables.
        cleanup_days: Delete versions older than this many days. Use 0 to keep only latest.
        delete_unverified: Delete unverified files (files from potentially failed transactions).
    """
    settings = get_settings()
    db_path = getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print(f"\n{'='*60}")
    print("LanceDB Optimization")
    print(f"{'='*60}")
    print(f"Database path: {db_path}")
    print(f"Cleanup versions older than: {cleanup_days} days")
    print(f"Delete unverified: {delete_unverified}")
    print()
    
    lancedb_client.connect(db_path)
    
    if tables:
        table_names = tables
    else:
        table_names = lancedb_client.get_db().table_names()
    
    if not table_names:
        print("No tables to optimize.")
        return
    
    sizes_before = get_table_sizes(db_path)
    total_before = sum(s.get('bytes', 0) for s in sizes_before.values())
    
    print(f"Tables to optimize: {', '.join(table_names)}")
    print(f"Total size before: {format_size(total_before)}")
    print()
    
    for table_name in table_names:
        print(f"\nOptimizing '{table_name}'...")
        
        try:
            table = lancedb_client.get_table(table_name)
            row_count = table.count_rows()
            print(f"  Rows: {row_count}")
            
            print("  Running optimize...")
            result = table.optimize(
                cleanup_older_than=timedelta(days=cleanup_days),
                delete_unverified=delete_unverified
            )
            
            if hasattr(result, 'bytes_removed'):
                print(f"  Bytes removed: {format_size(result.bytes_removed)}")
            if hasattr(result, 'old_versions'):
                print(f"  Old versions removed: {result.old_versions}")
            
            print(f"  ✓ '{table_name}' optimized")
            
        except Exception as e:
            print(f"  ✗ Error optimizing '{table_name}': {e}")
    
    sizes_after = get_table_sizes(db_path)
    total_after = sum(s.get('bytes', 0) for s in sizes_after.values())
    
    print(f"\n{'='*60}")
    print("Optimization Summary")
    print(f"{'='*60}")
    print(f"Total size before: {format_size(total_before)}")
    print(f"Total size after:  {format_size(total_after)}")
    print(f"Space freed:       {format_size(total_before - total_after)}")
    print()


def cleanup_old_versions(
    tables: Optional[List[str]] = None,
    days: int = 7,
    delete_unverified: bool = False
):
    """
    Clean up old versions of LanceDB tables without compacting.
    
    Args:
        tables: List of table names to clean. If None, clean all tables.
        days: Delete versions older than this many days. Use 0 to keep only latest.
        delete_unverified: Delete unverified files.
    """
    settings = get_settings()
    db_path = getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print(f"\n{'='*60}")
    print("LanceDB Cleanup Old Versions")
    print(f"{'='*60}")
    print(f"Database path: {db_path}")
    print(f"Delete versions older than: {days} days")
    print(f"Delete unverified: {delete_unverified}")
    print()
    
    lancedb_client.connect(db_path)
    
    if tables:
        table_names = tables
    else:
        table_names = lancedb_client.get_db().table_names()
    
    if not table_names:
        print("No tables to clean.")
        return
    
    sizes_before = get_table_sizes(db_path)
    total_before = sum(s.get('bytes', 0) for s in sizes_before.values())
    
    print(f"Tables to clean: {', '.join(table_names)}")
    print(f"Total size before: {format_size(total_before)}")
    print()
    
    for table_name in table_names:
        print(f"\nCleaning '{table_name}'...")
        
        try:
            table = lancedb_client.get_table(table_name)
            
            result = table.cleanup_old_versions(
                older_than=timedelta(days=days),
                delete_unverified=delete_unverified
            )
            
            if hasattr(result, 'bytes_removed'):
                print(f"  Bytes removed: {format_size(result.bytes_removed)}")
            if hasattr(result, 'old_versions'):
                print(f"  Old versions removed: {result.old_versions}")
            
            print(f"  ✓ '{table_name}' cleaned")
            
        except Exception as e:
            print(f"  ✗ Error cleaning '{table_name}': {e}")
    
    sizes_after = get_table_sizes(db_path)
    total_after = sum(s.get('bytes', 0) for s in sizes_after.values())
    
    print(f"\n{'='*60}")
    print("Cleanup Summary")
    print(f"{'='*60}")
    print(f"Total size before: {format_size(total_before)}")
    print(f"Total size after:  {format_size(total_after)}")
    print(f"Space freed:       {format_size(total_before - total_after)}")
    print()


def compact_files(tables: Optional[List[str]] = None):
    """
    Compact files in LanceDB tables without cleaning up old versions.
    
    Args:
        tables: List of table names to compact. If None, compact all tables.
    """
    settings = get_settings()
    db_path = getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print(f"\n{'='*60}")
    print("LanceDB File Compaction")
    print(f"{'='*60}")
    print(f"Database path: {db_path}")
    print()
    
    lancedb_client.connect(db_path)
    
    if tables:
        table_names = tables
    else:
        table_names = lancedb_client.get_db().table_names()
    
    if not table_names:
        print("No tables to compact.")
        return
    
    print(f"Tables to compact: {', '.join(table_names)}")
    print()
    
    for table_name in table_names:
        print(f"\nCompacting '{table_name}'...")
        
        try:
            table = lancedb_client.get_table(table_name)
            
            result = table.compact_files()
            
            if hasattr(result, 'fragments_removed'):
                print(f"  Fragments removed: {result.fragments_removed}")
            if hasattr(result, 'fragments_added'):
                print(f"  Fragments added: {result.fragments_added}")
            
            print(f"  ✓ '{table_name}' compacted")
            
        except Exception as e:
            print(f"  ✗ Error compacting '{table_name}': {e}")
    
    print("\nCompaction complete.")


def create_indexes():
    """Create scalar indexes on primary key columns for tables that need them."""
    from app.db.lancedb.schemas import SchemaRegistry
    
    settings = get_settings()
    db_path = getattr(settings, 'LANCEDB_PATH', './data/lancedb')
    
    print(f"\n{'='*60}")
    print("LanceDB Create Indexes")
    print(f"{'='*60}")
    print(f"Database path: {db_path}")
    print()
    
    lancedb_client.connect(db_path)
    
    for schema in SchemaRegistry.get_all():
        table_name = schema.table_name
        primary_key = schema.primary_key
        
        if not primary_key:
            continue
        
        print(f"\nChecking '{table_name}' for index on '{primary_key}'...")
        
        try:
            table = lancedb_client.get_table(table_name)
            
            try:
                existing_indexes = table.list_indices()
                index_names = [idx.name for idx in existing_indexes]
                
                if primary_key in index_names or f"{primary_key}_idx" in index_names:
                    print(f"  Index on '{primary_key}' already exists")
                    continue
            except Exception:
                pass
            
            print(f"  Creating scalar index on '{primary_key}'...")
            table.create_scalar_index(primary_key)
            print(f"  ✓ Index created on '{primary_key}' for '{table_name}'")
            
        except Exception as e:
            print(f"  ✗ Error creating index for '{table_name}': {e}")
    
    print("\nIndex creation complete.")


def main():
    parser = argparse.ArgumentParser(
        description="LanceDB maintenance script for optimizing storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/maintain_lancedb.py --status
    python scripts/maintain_lancedb.py --optimize
    python scripts/maintain_lancedb.py --optimize --days 0
    python scripts/maintain_lancedb.py --optimize --tables papers,date_index
    python scripts/maintain_lancedb.py --cleanup --days 0
    python scripts/maintain_lancedb.py --compact
    python scripts/maintain_lancedb.py --create-indexes

Note:
    --days 0 will keep only the latest version, freeing maximum space.
    Use --delete-unverified with caution, as it may delete files from
    in-progress transactions.
        """
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status of LanceDB tables"
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Optimize tables (compact files + cleanup old versions)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old versions only (no compaction)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact files only (no cleanup)"
    )
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of tables to process (default: all tables)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Delete versions older than this many days (default: 7, use 0 for latest only)"
    )
    parser.add_argument(
        "--delete-unverified",
        action="store_true",
        help="Delete unverified files (use with caution)"
    )
    parser.add_argument(
        "--create-indexes",
        action="store_true",
        help="Create scalar indexes on primary key columns"
    )
    
    args = parser.parse_args()
    
    tables = None
    if args.tables:
        tables = [t.strip() for t in args.tables.split(",")]
    
    if args.status:
        show_status()
    elif args.optimize:
        optimize_tables(tables, args.days, args.delete_unverified)
    elif args.cleanup:
        cleanup_old_versions(tables, args.days, args.delete_unverified)
    elif args.compact:
        compact_files(tables)
    elif args.create_indexes:
        create_indexes()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
