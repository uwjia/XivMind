import logging
import os
import threading
from typing import TYPE_CHECKING, Any, Dict, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import lancedb
    import pyarrow as pa

try:
    import lancedb
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    lancedb = None
    pa = None
    logger.warning("LanceDB not available. Install with: pip install lancedb pyarrow")


class LanceDBClient:
    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LanceDBClient._initialized:
            return
        
        self.settings = get_settings()
        self._db: Optional[Any] = None
        self._tables: Dict[str, Optional[Any]] = {}
        self._connected = False
        self._tables_initialized = False
        self._initializing_tables = False
        LanceDBClient._initialized = True

    def connect(self, db_path: str = None) -> bool:
        if self._connected:
            return True
        
        if not LANCEDB_AVAILABLE:
            raise ImportError("LanceDB is not installed. Install with: pip install lancedb pyarrow")
        
        if db_path is None:
            db_path = getattr(self.settings, 'LANCEDB_PATH', './data/lancedb')
        
        os.makedirs(db_path, exist_ok=True)
        
        logger.info(f"Connecting to LanceDB at {db_path}...")
        
        try:
            self._db = lancedb.connect(db_path)
            self._connected = True
            logger.info("Connected to LanceDB successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to LanceDB: {e}")
            raise ConnectionError(f"Failed to connect to LanceDB: {e}")

    def _get_missing_fields(self, table_name: str, expected_schema) -> list:
        try:
            table = self._db.open_table(table_name)
            current_schema = table.schema
            expected = expected_schema.get_pyarrow_schema()
            
            current_field_names = {field.name for field in current_schema}
            missing_fields = []
            
            for field in expected:
                if field.name not in current_field_names:
                    missing_fields.append(field)
            
            return missing_fields
        except Exception as e:
            logger.warning(f"Failed to get missing fields for {table_name}: {e}")
            return []

    def _migrate_table(self, table_name: str, schema, missing_fields: list) -> bool:
        try:
            import pandas as pd
            logger.info(f"Migrating {table_name} table, adding fields: {[f.name for f in missing_fields]}")
            
            old_table = self._db.open_table(table_name)
            df = old_table.to_pandas()
            
            for field in missing_fields:
                if field.name not in df.columns:
                    if pa.types.is_integer(field.type):
                        df[field.name] = pd.NA
                    elif pa.types.is_float(field.type):
                        df[field.name] = None
                    elif pa.types.is_string(field.type):
                        df[field.name] = None
                    elif pa.types.is_list(field.type):
                        df[field.name] = None
                    else:
                        df[field.name] = None
            
            df = df.replace({float('nan'): None})
            df = df.where(pd.notnull(df), None)
            
            self._db.drop_table(table_name)
            
            new_table = self._db.create_table(
                table_name,
                data=df,
                schema=schema.get_pyarrow_schema()
            )
            
            if schema.primary_key:
                try:
                    new_table.create_scalar_index(schema.primary_key)
                except Exception as e:
                    logger.warning(f"Failed to create index on {schema.primary_key}: {e}")
            
            self._tables[table_name] = new_table
            logger.info(f"Migration completed for {table_name}, preserved {len(df)} records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate {table_name}: {e}")
            return False

    def _schema_matches(self, table_name: str, expected_schema) -> bool:
        try:
            table = self._db.open_table(table_name)
            current_schema = table.schema
            expected = expected_schema.get_pyarrow_schema()
            
            current_field_names = {field.name for field in current_schema}
            expected_field_names = {field.name for field in expected}
            
            if current_field_names != expected_field_names:
                logger.info(f"Schema mismatch for {table_name}: current fields={current_field_names}, expected fields={expected_field_names}")
                return False
            
            if len(current_schema) != len(expected):
                logger.info(f"Schema field count mismatch for {table_name}: current={len(current_schema)}, expected={len(expected)}")
                return False
            
            for field1, field2 in zip(current_schema, expected):
                if field1.name != field2.name:
                    logger.info(f"Field name mismatch: {field1.name} vs {field2.name}")
                    return False
                if field1.type != field2.type:
                    logger.info(f"Field type mismatch for {field1.name}: {field1.type} vs {field2.type}")
                    return False
            
            logger.info(f"Schema matches for {table_name}")
            return True
        except Exception as e:
            logger.warning(f"Schema comparison failed for {table_name}: {e}")
            return False

    def init_tables(self, force_recreate: bool = False):
        if self._tables_initialized and not force_recreate:
            return
        
        if self._initializing_tables:
            return
        
        self._initializing_tables = True
        
        try:
            if not self._connected:
                self.connect()
            
            from app.db.lancedb.schemas import SchemaRegistry
            
            for schema in SchemaRegistry.get_all():
                table_name = schema.table_name
                
                if table_name in self._tables and self._tables[table_name] is not None:
                    continue
                
                table_exists = table_name in self._db.table_names()
                
                if table_exists and not force_recreate:
                    if self._schema_matches(table_name, schema):
                        self._tables[table_name] = self._db.open_table(table_name)
                        logger.info(f"Using existing {table_name} table")
                        continue
                    
                    missing_fields = self._get_missing_fields(table_name, schema)
                    if missing_fields:
                        if self._migrate_table(table_name, schema, missing_fields):
                            continue
                        else:
                            logger.warning(f"Migration failed for {table_name}, recreating table...")
                    
                    try:
                        self._db.drop_table(table_name)
                    except Exception as e:
                        logger.warning(f"Failed to drop table {table_name}: {e}")
                    table_exists = False
                
                if not table_exists or force_recreate:
                    try:
                        table = self._db.create_table(
                            table_name, 
                            schema=schema.get_pyarrow_schema()
                        )
                        
                        if schema.primary_key:
                            table.create_scalar_index(schema.primary_key)
                            logger.info(f"Created scalar index on '{schema.primary_key}' for {table_name}")
                        
                        self._tables[table_name] = table
                        logger.info(f"{table_name} table created")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"Table {table_name} already exists, checking schema...")
                            if not self._schema_matches(table_name, schema):
                                missing_fields = self._get_missing_fields(table_name, schema)
                                if missing_fields and self._migrate_table(table_name, schema, missing_fields):
                                    continue
                            self._tables[table_name] = self._db.open_table(table_name)
                            logger.info(f"Using existing {table_name} table (race condition)")
                        else:
                            raise
            
            self._tables_initialized = True
        finally:
            self._initializing_tables = False

    def drop_all_tables(self):
        if not self._connected:
            self.connect()
        
        for table_name in list(self._db.table_names()):
            try:
                self._db.drop_table(table_name)
                logger.info(f"Dropped table: {table_name}")
            except Exception as e:
                logger.warning(f"Failed to drop table {table_name}: {e}")
        
        self._tables.clear()
        self._tables_initialized = False

    def get_table(self, table_name: str) -> Any:
        if not self._connected:
            self.connect()
        
        if table_name in self._tables and self._tables[table_name] is not None:
            return self._tables[table_name]
        
        self.init_tables()
        
        return self._tables.get(table_name)

    def get_db(self) -> Any:
        if not self._connected:
            self.connect()
        return self._db


lancedb_client = LanceDBClient()
