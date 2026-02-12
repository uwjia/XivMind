# Schema 升级说明

## 版本号位置

在 `backend/app/database.py` 中定义：

```python
# 第 52-53 行
BOOKMARK_SCHEMA_VERSION = 2   # bookmarks 表版本
DOWNLOAD_SCHEMA_VERSION = 2   # downloads 表版本
```

## 升级步骤

### 1. 修改版本号

将目标表的版本号 +1：

```python
# 例如：升级 bookmarks 表
BOOKMARK_SCHEMA_VERSION = 3   # 从 2 改为 3
```

### 2. 修改字段定义

在 `create_collections()` 方法中修改对应的字段列表：

```python
# bookmarks 字段定义（约第 92-105 行）
bookmark_fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
    # ... 其他现有字段 ...
    FieldSchema(name="new_field", dtype=DataType.VARCHAR, max_length=256),  # 新增字段
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
]
```

### 3. 重启后端服务

```powershell
cd d:\Workspaces\electron_WS\new_arxiv\XivMind\backend
.\start.bat stop
.\start.bat start
```

### 4. 查看日志确认

日志会显示升级信息：

```
Upgrading bookmarks schema from v2 to v3, dropping old collection...
Bookmarks collection created with new schema
Schema version set for bookmarks: v3
```

---

## 升级流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      启动后端服务                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  get_schema_version("bookmarks")                            │
│  查询 bookmarks_schema_version 表中的版本号                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        version = 0     version < TARGET  version >= TARGET
        (无版本记录)      (需要升级)        (无需升级)
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ collection  │   │ 删除旧      │   │ 正常使用    │
    │ 存在?       │   │ collection  │   │ 保留数据    │
    └─────────────┘   │ 创建新表    │   └─────────────┘
         │ │          │ 设置版本号  │
      是 │ │ 否       └─────────────┘
         │ │
         ▼ ▼
    ┌─────────────┐   ┌─────────────┐
    │ 设置版本号  │   │ 创建新表    │
    │ 保留数据    │   │ 设置版本号  │
    └─────────────┘   └─────────────┘
```

---

## 版本历史

| 版本 | 表 | 变更内容 | 日期 |
|------|-----|---------|------|
| v1 | bookmarks/downloads | 初始版本 | - |
| v2 | bookmarks | 添加 comment、abs_url 字段 | - |
| v2 | downloads | 添加 file_path、error_message 字段 | - |
| | | | |

---

## 数据迁移

升级会删除所有数据。如需保留数据，请先备份：

### 备份脚本

```python
# backup_data.py
from pymilvus import connections, Collection
import json

connections.connect(host='localhost', port='19530', db_name='xivmind')

# 备份 bookmarks
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

# 备份 downloads
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

### 恢复脚本

```python
# restore_data.py
from pymilvus import connections, Collection
import json

connections.connect(host='localhost', port='19530', db_name='xivmind')

# 恢复 bookmarks
coll = Collection('bookmarks')
with open('bookmarks_backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    # 转换数据格式以匹配新 schema
    coll.insert([
        [item['id']],
        [item['paper_id']],
        # ... 其他字段 ...
        [[0.0] * 1536]  # embedding
    ])
coll.flush()
print(f'Restored {len(data)} bookmarks')
```

---

## 注意事项

1. **升级会删除数据** - 确保先备份重要数据
2. **版本号只能增加** - 不要降低版本号
3. **测试环境先行** - 在生产环境升级前，先在测试环境验证
4. **前后端同步** - 如果字段变更影响前端，需同步更新前端代码
