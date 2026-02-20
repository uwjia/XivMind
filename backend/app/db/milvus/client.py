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
from app.db.milvus.schemas import SchemaRegistry, BaseCollectionSchema
from typing import Optional, Dict
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
        self._collections: Dict[str, Optional[Collection]] = {}
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

    def _get_schema_version(self, collection_name: str) -> int:
        """Get schema version for a collection."""
        try:
            logger.debug(f"Checking schema version for {collection_name}...")
            schema = SchemaRegistry.get(collection_name)
            version_collection_name = schema.get_schema_version_collection_name()
            
            if utility.has_collection(version_collection_name):
                version_collection = Collection(version_collection_name)
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

    def _set_schema_version(self, collection_name: str, version: int):
        """Set schema version for a collection."""
        try:
            logger.debug(f"Setting schema version for {collection_name} to v{version}...")
            schema = SchemaRegistry.get(collection_name)
            version_collection_name = schema.get_schema_version_collection_name()
            
            if utility.has_collection(version_collection_name):
                utility.drop_collection(version_collection_name)
            
            version_fields = schema.get_schema_version_fields()
            version_schema = CollectionSchema(
                fields=version_fields, 
                description=f"Schema version for {collection_name}"
            )
            version_collection = Collection(name=version_collection_name, schema=version_schema)
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

    def _init_collection(self, schema: BaseCollectionSchema) -> Collection:
        """Initialize a single collection based on schema."""
        collection_name = schema.collection_name
        logger.info(f"Checking {collection_name} collection...")
        
        current_version = self._get_schema_version(collection_name)
        
        if current_version == 0 and utility.has_collection(collection_name):
            current_version = schema.schema_version
            self._set_schema_version(collection_name, schema.schema_version)
            logger.info(f"Existing {collection_name} collection found, setting schema version")
        elif current_version > 0 and current_version < schema.schema_version:
            if utility.has_collection(collection_name):
                logger.info(
                    f"Upgrading {collection_name} schema from v{current_version} "
                    f"to v{schema.schema_version}, dropping old collection..."
                )
                utility.drop_collection(collection_name)

        if not utility.has_collection(collection_name):
            logger.info(f"Creating {collection_name} collection...")
            collection_schema = schema.get_collection_schema()
            collection = Collection(name=collection_name, schema=collection_schema)
            collection.create_index(field_name="embedding", index_params=schema.get_index_params())
            self._set_schema_version(collection_name, schema.schema_version)
            logger.info(f"{collection_name} collection created with new schema")
            return collection
        else:
            logger.info(f"Using existing {collection_name} collection")
            return Collection(collection_name)

    def init_collections(self):
        """Initialize all registered collections."""
        logger.info("Starting init_collections...")
        try:
            self.connect()
            logger.info("Milvus connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

        for schema in SchemaRegistry.get_all():
            collection = self._init_collection(schema)
            self._collections[schema.collection_name] = collection

        logger.info("init_collections completed successfully")

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection by name."""
        if collection_name not in self._collections or not self._collections[collection_name]:
            self.init_collections()
        return self._collections[collection_name]


milvus_client = MilvusClient()
