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
from typing import Optional
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)


class MilvusClient:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if MilvusClient._initialized:
            return
        
        self.settings = get_settings()
        self.bookmarks_collection: Optional[Collection] = None
        self.downloads_collection: Optional[Collection] = None
        self._connected = False
        MilvusClient._initialized = True

    def _do_connect(self):
        connections.connect(
            alias="default",
            host=self.settings.MILVUS_HOST,
            port=self.settings.MILVUS_PORT,
        )

    def connect(self, timeout: int = 10) -> bool:
        if self._connected:
            return True
        
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
        return True

    def init_collections(self):
        logger.info("Starting init_collections...")
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

        logger.info("init_collections completed successfully")

    def get_bookmarks_collection(self) -> Collection:
        if not self.bookmarks_collection:
            self.init_collections()
        return self.bookmarks_collection

    def get_downloads_collection(self) -> Collection:
        if not self.downloads_collection:
            self.init_collections()
        return self.downloads_collection


milvus_client = MilvusClient()
