# Schema Upgrade Guide

## Version Number Location

Defined in `backend/app/database.py`:

```python
# Line 52-53
BOOKMARK_SCHEMA_VERSION = 2   # bookmarks table version
DOWNLOAD_SCHEMA_VERSION = 2   # downloads table version
```

## Upgrade Steps

### 1. Update Version Number

Increment the version number for the target table:

```python
# Example: upgrading bookmarks table
BOOKMARK_SCHEMA_VERSION = 3   # change from 2 to 3
```

### 2. Modify Field Definitions

Update the corresponding field list in the `create_collections()` method:

```python
# bookmarks field definitions (around line 92-105)
bookmark_fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
    # ... other existing fields ...
    FieldSchema(name="new_field", dtype=DataType.VARCHAR, max_length=256),  # new field
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
]
```

### 3. Restart Backend Service

```powershell
cd d:\Workspaces\electron_WS\new_arxiv\XivMind\backend
.\start.bat stop
.\start.bat start
```

### 4. Verify Upgrade in Logs

The logs will show upgrade information:

```
Upgrading bookmarks schema from v2 to v3, dropping old collection...
Bookmarks collection created with new schema
Schema version set for bookmarks: v3
```

---

## Upgrade Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Start Backend Service                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  get_schema_version("bookmarks")                            │
│  Query version from bookmarks_schema_version table           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        version = 0     version < TARGET  version >= TARGET
        (no record)      (upgrade needed)  (no upgrade)
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ collection  │   │ Drop old    │   │ Normal use  │
    │ exists?     │   │ collection  │   │ Keep data   │
    └─────────────┘   │ Create new  │   └─────────────┘
         │ │          │ Set version │
      yes │ │ no       └─────────────┘
         │ │
         ▼ ▼
    ┌─────────────┐   ┌─────────────┐
    │ Set version │   │ Create new  │
    │ Keep data   │   │ Set version │
    └─────────────┘   └─────────────┘
```

---

## Version History

| Version | Table               | Changes                               | Date |
| ------- | ------------------- | ------------------------------------- | ---- |
| v1      | bookmarks/downloads | Initial version                       | -    |
| v2      | bookmarks           | Added comment, abs_url fields         | -    |
| v2      | downloads           | Added file_path, error_message fields | -    |
|         |                     |                                       |      |

---

## Data Migration

Upgrading will delete all data. Backup first if you need to preserve data:

### Backup Script

```python
# backup_data.py
from pymilvus import connections, Collection
import json

connections.connect(host='localhost', port='19530', db_name='xivmind')

# Backup bookmarks
coll = Collection('bookmarks')
coll.load()
results = coll.query(expr='id != ""', output_fields=[
    'id', 'paper_id', 'arxiv_id', 'title', 'authors', 'abstract',
    'comment', 'primary_category', 'categories', 'pdf_url', 'abs_url',
    'published', 'updated', 'created_at'
])
with open('bookmarks_backup.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'Backed up {len(results)} bookmarks')

# Backup downloads
coll = Collection('downloads')
coll.load()
results = coll.query(expr='id != ""', output_fields=[
    'id', 'paper_id', 'arxiv_id', 'title', 'pdf_url', 'status',
    'progress', 'file_path', 'error_message', 'created_at', 'updated_at'
])
with open('downloads_backup.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'Backed up {len(results)} downloads')
```

### Restore Script

```python
# restore_data.py
from pymilvus import connections, Collection
import json

connections.connect(host='localhost', port='19530', db_name='xivmind')

# Restore bookmarks
coll = Collection('bookmarks')
with open('bookmarks_backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    # Convert data format to match new schema
    coll.insert([
        [item['id']],
        [item['paper_id']],
        # ... other fields ...
        [[0.0] * 1536]  # embedding
    ])
coll.flush()
print(f'Restored {len(data)} bookmarks')
```

---

## Important Notes

1. **Upgrading deletes all data** - Always backup important data first
2. **Version numbers only increase** - Never decrease version numbers
3. **Test in development first** - Validate in a test environment before production
4. **Sync frontend changes** - Update frontend code if field changes affect the UI

---

## Quick Reference

| Operation                | Location                   |
| ------------------------ | -------------------------- |
| Modify bookmarks version | `database.py` line 52      |
| Modify downloads version | `database.py` line 53      |
| Modify bookmarks fields  | `database.py` line 92-105  |
| Modify downloads fields  | `database.py` line 130-145 |
