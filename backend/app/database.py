from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
    db,
    MilvusException,
)
from app.config import get_settings
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)


class MilvusService:
    def __init__(self):
        self.settings = get_settings()
        self.bookmarks_collection = None
        self.downloads_collection = None
        self._connected = False

    def _do_connect(self):
        connections.connect(
            alias="default",
            host=self.settings.MILVUS_HOST,
            port=self.settings.MILVUS_PORT,
        )

    def connect(self, timeout: int = 10):
        if self._connected:
            return
        
        logger.info(f"Connecting to Milvus at {self.settings.MILVUS_HOST}:{self.settings.MILVUS_PORT}...")
        
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(self._do_connect)
            try:
                future.result(timeout=timeout)
                self._connected = True
                logger.info("Connected to Milvus successfully")
            except FuturesTimeoutError:
                error_msg = f"Connection to Milvus timed out after {timeout} seconds. "
                error_msg += f"Please ensure Milvus is running at {self.settings.MILVUS_HOST}:{self.settings.MILVUS_PORT}."
                logger.error(error_msg)
                executor.shutdown(wait=False, cancel_futures=True)
                raise ConnectionError(error_msg)
        except ConnectionError:
            raise
        except Exception as e:
            error_msg = f"Failed to connect to Milvus: {e}. "
            error_msg += f"Please ensure Milvus is running at {self.settings.MILVUS_HOST}:{self.settings.MILVUS_PORT}."
            logger.error(error_msg)
            executor.shutdown(wait=False, cancel_futures=True)
            raise ConnectionError(error_msg)
        finally:
            executor.shutdown(wait=False)

        db_name = self.settings.DATABASE_NAME
        try:
            db.create_database(db_name)
            logger.info(f"Created database: {db_name}")
        except MilvusException as e:
            if "already exist" in str(e):
                logger.debug(f"Database '{db_name}' already exists, using existing database")
            else:
                raise
        db.using_database(db_name)

    def create_collections(self):
        logger.info("Starting create_collections...")
        try:
            self.connect()
            logger.info("Milvus connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

        BOOKMARK_SCHEMA_VERSION = 2
        DOWNLOAD_SCHEMA_VERSION = 2

        def get_schema_version(collection_name: str) -> int:
            try:
                logger.debug(f"Checking schema version for {collection_name}...")
                if utility.has_collection(f"{collection_name}_schema_version"):
                    version_collection = Collection(f"{collection_name}_schema_version")
                    version_collection.load()
                    results = version_collection.query(expr='id == "version"', output_fields=["version"])
                    if results:
                        version = int(results[0].get("version", 0))
                        logger.info(f"Schema version for {collection_name}: v{version}")
                        return version
            except Exception as e:
                logger.warning(f"Failed to get schema version for {collection_name}: {e}")
            logger.info(f"No schema version found for {collection_name}, returning 0")
            return 0

        def set_schema_version(collection_name: str, version: int):
            try:
                logger.debug(f"Setting schema version for {collection_name} to v{version}...")
                if utility.has_collection(f"{collection_name}_schema_version"):
                    utility.drop_collection(f"{collection_name}_schema_version")
                version_fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                    FieldSchema(name="version", dtype=DataType.INT64),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=8),
                ]
                version_schema = CollectionSchema(fields=version_fields, description=f"Schema version for {collection_name}")
                version_collection = Collection(name=f"{collection_name}_schema_version", schema=version_schema)
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 8},
                }
                version_collection.create_index(field_name="embedding", index_params=index_params)
                version_collection.insert([["version"], [version], [[0.0] * 8]])
                version_collection.flush()
                logger.info(f"Schema version set for {collection_name}: v{version}")
            except Exception as e:
                logger.error(f"Failed to set schema version for {collection_name}: {e}")

        logger.info("Checking bookmarks collection...")
        bookmark_version = get_schema_version("bookmarks")
        if bookmark_version == 0 and utility.has_collection("bookmarks"):
            bookmark_version = BOOKMARK_SCHEMA_VERSION
            set_schema_version("bookmarks", BOOKMARK_SCHEMA_VERSION)
            logger.info("Existing bookmarks collection found, setting schema version")
        elif bookmark_version > 0 and bookmark_version < BOOKMARK_SCHEMA_VERSION:
            if utility.has_collection("bookmarks"):
                logger.info(f"Upgrading bookmarks schema from v{bookmark_version} to v{BOOKMARK_SCHEMA_VERSION}, dropping old collection...")
                utility.drop_collection("bookmarks")

        if not utility.has_collection("bookmarks"):
            logger.info("Creating bookmarks collection...")
            bookmark_fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="arxiv_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=16384),
                FieldSchema(name="comment", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="primary_category", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="categories", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="pdf_url", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="abs_url", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="published", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="updated", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            ]
            bookmark_schema = CollectionSchema(fields=bookmark_fields, description="Bookmarked papers")
            self.bookmarks_collection = Collection(name="bookmarks", schema=bookmark_schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            }
            self.bookmarks_collection.create_index(field_name="embedding", index_params=index_params)
            set_schema_version("bookmarks", BOOKMARK_SCHEMA_VERSION)
            logger.info("Bookmarks collection created with new schema")
        else:
            logger.info("Using existing bookmarks collection")
            self.bookmarks_collection = Collection("bookmarks")

        logger.info("Checking downloads collection...")
        download_version = get_schema_version("downloads")
        if download_version == 0 and utility.has_collection("downloads"):
            download_version = DOWNLOAD_SCHEMA_VERSION
            set_schema_version("downloads", DOWNLOAD_SCHEMA_VERSION)
            logger.info("Existing downloads collection found, setting schema version")
        elif download_version > 0 and download_version < DOWNLOAD_SCHEMA_VERSION:
            if utility.has_collection("downloads"):
                logger.info(f"Upgrading downloads schema from v{download_version} to v{DOWNLOAD_SCHEMA_VERSION}, dropping old collection...")
                utility.drop_collection("downloads")

        if not utility.has_collection("downloads"):
            logger.info("Creating downloads collection...")
            download_fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="arxiv_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="pdf_url", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=32),
                FieldSchema(name="progress", dtype=DataType.INT64),
                FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="file_size", dtype=DataType.INT64),
                FieldSchema(name="error_message", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=8),
            ]
            download_schema = CollectionSchema(fields=download_fields, description="Download tasks")
            self.downloads_collection = Collection(name="downloads", schema=download_schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            }
            self.downloads_collection.create_index(field_name="embedding", index_params=index_params)
            set_schema_version("downloads", DOWNLOAD_SCHEMA_VERSION)
            logger.info("Downloads collection created with new schema")
        else:
            logger.info("Using existing downloads collection")
            self.downloads_collection = Collection("downloads")

        logger.info("create_collections completed successfully")

    def get_bookmarks_collection(self) -> Collection:
        if not self.bookmarks_collection:
            self.create_collections()
        return self.bookmarks_collection

    def get_downloads_collection(self) -> Collection:
        if not self.downloads_collection:
            self.create_collections()
        return self.downloads_collection


milvus_service = MilvusService()


class BookmarkService:
    def __init__(self):
        self.collection = None

    def _get_collection(self) -> Collection:
        if not self.collection:
            self.collection = milvus_service.get_bookmarks_collection()
        return self.collection

    def add_bookmark(self, bookmark_data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        bookmark_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        def safe_str(value, max_len=None):
            if value is None:
                return ""
            s = str(value)
            return s[:max_len] if max_len else s

        title = safe_str(bookmark_data.get("title"), 1024)
        abstract = safe_str(bookmark_data.get("abstract"), 16384)
        comment = safe_str(bookmark_data.get("comment"), 4096)

        data = [
            [bookmark_id],
            [safe_str(bookmark_data.get("paper_id"))],
            [safe_str(bookmark_data.get("arxiv_id"))],
            [title],
            [json.dumps(bookmark_data.get("authors") or [])],
            [abstract],
            [comment],
            [safe_str(bookmark_data.get("primary_category"))],
            [json.dumps(bookmark_data.get("categories") or [])],
            [safe_str(bookmark_data.get("pdf_url"))],
            [safe_str(bookmark_data.get("abs_url"))],
            [safe_str(bookmark_data.get("published"))],
            [safe_str(bookmark_data.get("updated"))],
            [now],
            [[0.0] * 1536],
        ]

        collection.insert(data)
        
        return {
            "id": bookmark_id,
            "paper_id": safe_str(bookmark_data.get("paper_id")),
            "arxiv_id": safe_str(bookmark_data.get("arxiv_id")),
            "title": title,
            "authors": bookmark_data.get("authors") or [],
            "abstract": abstract,
            "comment": comment,
            "primary_category": safe_str(bookmark_data.get("primary_category")),
            "categories": bookmark_data.get("categories") or [],
            "pdf_url": safe_str(bookmark_data.get("pdf_url")),
            "abs_url": safe_str(bookmark_data.get("abs_url")),
            "published": safe_str(bookmark_data.get("published")),
            "updated": safe_str(bookmark_data.get("updated")),
            "created_at": now,
        }

    def remove_bookmark(self, paper_id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        collection.delete(f'paper_id == "{paper_id}"')
        return True

    def is_bookmarked(self, paper_id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'paper_id == "{paper_id}"', output_fields=["id"])
        return len(results) > 0

    def get_all_bookmarks(self, limit: int = 100, offset: int = 0) -> tuple:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr='id != ""',
            output_fields=["id", "paper_id", "arxiv_id", "title", "authors", "abstract",
                          "comment", "primary_category", "categories", "pdf_url", "abs_url",
                          "published", "updated", "created_at"],
            limit=limit,
            offset=offset,
        )
        total = len(collection.query(expr='id != ""', output_fields=["id"]))
        return [self._entity_to_response(r) for r in results], total

    def search_bookmarks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'title like "%{query}%" or abstract like "%{query}%"',
            output_fields=["id", "paper_id", "arxiv_id", "title", "authors", "abstract",
                          "comment", "primary_category", "categories", "pdf_url", "abs_url",
                          "published", "updated", "created_at"],
            limit=limit,
        )
        return [self._entity_to_response(r) for r in results]

    def _entity_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "id": entity.get("id", ""),
            "paper_id": entity.get("paper_id", ""),
            "arxiv_id": entity.get("arxiv_id", ""),
            "title": entity.get("title", ""),
            "authors": json.loads(entity.get("authors", "[]")),
            "abstract": entity.get("abstract", ""),
            "comment": entity.get("comment", ""),
            "primary_category": entity.get("primary_category", ""),
            "categories": json.loads(entity.get("categories", "[]")),
            "pdf_url": entity.get("pdf_url", ""),
            "abs_url": entity.get("abs_url", ""),
            "published": entity.get("published", ""),
            "updated": entity.get("updated", ""),
            "created_at": entity.get("created_at", ""),
        }


class DownloadService:
    def __init__(self):
        self.collection = None

    def _get_collection(self) -> Collection:
        if not self.collection:
            self.collection = milvus_service.get_downloads_collection()
        return self.collection

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        def safe_str(value, max_len=None):
            if value is None:
                return ""
            s = str(value)
            return s[:max_len] if max_len else s

        title = safe_str(task_data.get("title"), 1024)

        data = [
            [task_id],
            [safe_str(task_data.get("paper_id"))],
            [safe_str(task_data.get("arxiv_id"))],
            [title],
            [safe_str(task_data.get("pdf_url"))],
            ["pending"],
            [0],
            [""],
            [0],
            [""],
            [now],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(data)

        return {
            "id": task_id,
            "paper_id": safe_str(task_data.get("paper_id")),
            "arxiv_id": safe_str(task_data.get("arxiv_id")),
            "title": title,
            "pdf_url": safe_str(task_data.get("pdf_url")),
            "status": "pending",
            "progress": 0,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": now,
            "updated_at": now,
        }

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{task_id}"', output_fields=["*"])
        if not results:
            return None

        entity = results[0]
        entity.update(updates)
        entity["updated_at"] = datetime.utcnow().isoformat()

        def safe_str(value, max_len=None):
            if value is None:
                return ""
            s = str(value)
            return s[:max_len] if max_len else s

        title = safe_str(entity.get("title"), 1024)

        data = [
            [safe_str(entity.get("id"))],
            [safe_str(entity.get("paper_id"))],
            [safe_str(entity.get("arxiv_id"))],
            [title],
            [safe_str(entity.get("pdf_url"))],
            [safe_str(entity.get("status"))],
            [entity.get("progress", 0) or 0],
            [safe_str(entity.get("file_path"))],
            [entity.get("file_size", 0) or 0],
            [safe_str(entity.get("error_message"))],
            [safe_str(entity.get("created_at"))],
            [safe_str(entity.get("updated_at"))],
            [[0.0] * 8],
        ]

        collection.delete(f'id == "{task_id}"')
        collection.insert(data)
        return self._entity_to_response(entity)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{task_id}"', output_fields=["*"])
        if results:
            return self._entity_to_response(results[0])
        return None

    def get_all_tasks(self, limit: int = 100, offset: int = 0) -> tuple:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr='id != ""',
            output_fields=["*"],
            limit=limit,
            offset=offset,
        )
        total = len(collection.query(expr='id != ""', output_fields=["id"]))
        return [self._entity_to_response(r) for r in results], total

    def delete_task(self, task_id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        collection.delete(f'id == "{task_id}"')
        return True

    def reset_incomplete_tasks(self) -> int:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr='status == "downloading" or status == "pending"',
            output_fields=["*"],
        )
        
        if not results:
            return 0
        
        count = 0
        for entity in results:
            entity["status"] = "failed"
            entity["error_message"] = "Download interrupted - please retry"
            entity["updated_at"] = datetime.utcnow().isoformat()
            
            def safe_str(value, max_len=None):
                if value is None:
                    return ""
                s = str(value)
                return s[:max_len] if max_len else s

            title = safe_str(entity.get("title"), 1024)

            data = [
                [safe_str(entity.get("id"))],
                [safe_str(entity.get("paper_id"))],
                [safe_str(entity.get("arxiv_id"))],
                [title],
                [safe_str(entity.get("pdf_url"))],
                ["failed"],
                [entity.get("progress", 0) or 0],
                [safe_str(entity.get("file_path"))],
                [entity.get("file_size", 0) or 0],
                ["Download interrupted - please retry"],
                [safe_str(entity.get("created_at"))],
                [safe_str(entity.get("updated_at"))],
                [[0.0] * 8],
            ]

            collection.delete(f'id == "{entity.get("id")}"')
            collection.insert(data)
            count += 1
        
        return count

    def _entity_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "id": entity.get("id", ""),
            "paper_id": entity.get("paper_id", ""),
            "arxiv_id": entity.get("arxiv_id", ""),
            "title": entity.get("title", ""),
            "pdf_url": entity.get("pdf_url", ""),
            "status": entity.get("status", "pending"),
            "progress": entity.get("progress", 0),
            "file_path": entity.get("file_path", ""),
            "file_size": entity.get("file_size", 0),
            "error_message": entity.get("error_message", ""),
            "created_at": entity.get("created_at", ""),
            "updated_at": entity.get("updated_at", ""),
        }


bookmark_service = BookmarkService()
download_service = DownloadService()
