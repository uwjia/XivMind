import pytest
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import TimeoutError as FuturesTimeoutError
import threading

from app.db.milvus.client import MilvusClient, milvus_client


class TestMilvusClientSingleton:
    def test_singleton_returns_same_instance(self):
        MilvusClient._instance = None
        MilvusClient._initialized = False
        
        instance1 = MilvusClient()
        instance2 = MilvusClient()
        
        assert instance1 is instance2

    def test_singleton_thread_safety(self):
        MilvusClient._instance = None
        MilvusClient._initialized = False
        
        instances = []
        
        def create_instance():
            instances.append(MilvusClient())
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert all(inst is instances[0] for inst in instances)

    def test_global_client_instance(self):
        assert milvus_client is not None
        assert isinstance(milvus_client, MilvusClient)


class TestMilvusClientConnect:
    def test_connect_success(self):
        with patch('app.db.milvus.client.connections') as mock_connections:
            with patch('app.db.milvus.client.db') as mock_db:
                with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                    mock_settings = Mock()
                    mock_settings.MILVUS_HOST = "localhost"
                    mock_settings.MILVUS_PORT = 19530
                    mock_settings.DATABASE_NAME = "test"
                    mock_get_settings.return_value = mock_settings
                    
                    mock_connections.connect = Mock()
                    mock_db.list_database = Mock(return_value=["test"])
                    mock_db.using_database = Mock()
                    
                    MilvusClient._instance = None
                    MilvusClient._initialized = False
                    
                    client = MilvusClient()
                    result = client.connect()
                    
                    assert result is True
                    assert client._connected is True
                    mock_connections.connect.assert_called_once()

    def test_connect_already_connected(self):
        with patch('app.db.milvus.client.connections') as mock_connections:
            with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                mock_settings = Mock()
                mock_settings.MILVUS_HOST = "localhost"
                mock_settings.MILVUS_PORT = 19530
                mock_settings.DATABASE_NAME = "test"
                mock_get_settings.return_value = mock_settings
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                client._connected = True
                
                result = client.connect()
                
                assert result is True
                mock_connections.connect.assert_not_called()

    def test_connect_creates_database_if_not_exists(self):
        with patch('app.db.milvus.client.connections') as mock_connections:
            with patch('app.db.milvus.client.db') as mock_db:
                with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                    mock_settings = Mock()
                    mock_settings.MILVUS_HOST = "localhost"
                    mock_settings.MILVUS_PORT = 19530
                    mock_settings.DATABASE_NAME = "new_db"
                    mock_get_settings.return_value = mock_settings
                    
                    mock_connections.connect = Mock()
                    mock_db.list_database = Mock(return_value=["existing_db"])
                    mock_db.create_database = Mock()
                    mock_db.using_database = Mock()
                    
                    MilvusClient._instance = None
                    MilvusClient._initialized = False
                    
                    client = MilvusClient()
                    client.connect()
                    
                    mock_db.create_database.assert_called_once_with("new_db")

    def test_connect_timeout(self):
        with patch('app.db.milvus.client.connections') as mock_connections:
            with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                mock_settings = Mock()
                mock_settings.MILVUS_HOST = "localhost"
                mock_settings.MILVUS_PORT = 19530
                mock_settings.DATABASE_NAME = "test"
                mock_get_settings.return_value = mock_settings
                
                def slow_connect(*args, **kwargs):
                    import time
                    time.sleep(15)
                
                mock_connections.connect = Mock(side_effect=slow_connect)
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                
                with pytest.raises(ConnectionError) as exc_info:
                    client.connect(timeout=1)
                
                assert "timed out" in str(exc_info.value)

    def test_connect_failure(self):
        with patch('app.db.milvus.client.connections') as mock_connections:
            with patch('app.db.milvus.client.get_settings') as mock_get_settings:
                mock_settings = Mock()
                mock_settings.MILVUS_HOST = "localhost"
                mock_settings.MILVUS_PORT = 19530
                mock_settings.DATABASE_NAME = "test"
                mock_get_settings.return_value = mock_settings
                
                mock_connections.connect = Mock(side_effect=Exception("Connection refused"))
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                
                with pytest.raises(ConnectionError) as exc_info:
                    client.connect()
                
                assert "Failed to connect" in str(exc_info.value)


class TestMilvusClientGetSchemaVersion:
    def test_get_schema_version_existing(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.Collection') as mock_collection_class:
                with patch('app.db.milvus.client.SchemaRegistry') as mock_registry:
                    mock_schema = Mock()
                    mock_schema.get_schema_version_collection_name = Mock(return_value="bookmarks_version")
                    mock_registry.get = Mock(return_value=mock_schema)
                    
                    mock_utility.has_collection = Mock(return_value=True)
                    
                    mock_version_collection = Mock()
                    mock_version_collection.load = Mock()
                    mock_version_collection.query = Mock(return_value=[{"id": "version", "version": 2}])
                    mock_collection_class.return_value = mock_version_collection
                    
                    MilvusClient._instance = None
                    MilvusClient._initialized = False
                    
                    client = MilvusClient()
                    result = client._get_schema_version("bookmarks")
                    
                    assert result == 2

    def test_get_schema_version_not_found(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.SchemaRegistry') as mock_registry:
                mock_schema = Mock()
                mock_schema.get_schema_version_collection_name = Mock(return_value="bookmarks_version")
                mock_registry.get = Mock(return_value=mock_schema)
                
                mock_utility.has_collection = Mock(return_value=False)
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                result = client._get_schema_version("bookmarks")
                
                assert result == 0

    def test_get_schema_version_exception(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.SchemaRegistry') as mock_registry:
                mock_schema = Mock()
                mock_schema.get_schema_version_collection_name = Mock(side_effect=Exception("Error"))
                mock_registry.get = Mock(return_value=mock_schema)
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                result = client._get_schema_version("bookmarks")
                
                assert result == 0


class TestMilvusClientInitCollection:
    def test_init_collection_creates_new(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.Collection') as mock_collection_class:
                with patch('app.db.milvus.client.CollectionSchema') as mock_schema_class:
                    mock_utility.has_collection = Mock(return_value=False)
                    
                    mock_collection = Mock()
                    mock_collection.create_index = Mock()
                    mock_collection_class.return_value = mock_collection
                    
                    mock_schema = Mock()
                    mock_schema.collection_name = "bookmarks"
                    mock_schema.embedding_dim = 1536
                    mock_schema.schema_version = 1
                    mock_schema.get_collection_schema = Mock(return_value=Mock())
                    mock_schema.get_index_params = Mock(return_value={})
                    mock_schema.get_schema_version_collection_name = Mock(return_value="bookmarks_version")
                    mock_schema.get_schema_version_fields = Mock(return_value=[])
                    
                    MilvusClient._instance = None
                    MilvusClient._initialized = False
                    
                    client = MilvusClient()
                    client._connected = True
                    result = client._init_collection(mock_schema)
                    
                    assert result is mock_collection
                    mock_collection_class.assert_called()

    def test_init_collection_uses_existing(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.Collection') as mock_collection_class:
                mock_utility.has_collection = Mock(return_value=True)
                
                mock_existing_collection = Mock()
                mock_existing_schema = Mock()
                mock_field = Mock()
                mock_field.name = "embedding"
                mock_field.dtype = 101  # DataType.FLOAT_VECTOR
                mock_field.params = {"dim": 1536}
                mock_existing_schema.fields = [mock_field]
                mock_existing_collection.schema = mock_existing_schema
                
                mock_collection_class.return_value = mock_existing_collection
                
                mock_schema = Mock()
                mock_schema.collection_name = "bookmarks"
                mock_schema.embedding_dim = 1536
                mock_schema.schema_version = 1
                mock_schema.get_schema_version_collection_name = Mock(return_value="bookmarks_version")
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                client._connected = True
                result = client._init_collection(mock_schema)
                
                assert result is mock_existing_collection

    def test_init_collection_recreates_on_dimension_mismatch(self):
        with patch('app.db.milvus.client.utility') as mock_utility:
            with patch('app.db.milvus.client.Collection') as mock_collection_class:
                with patch('app.db.milvus.client.CollectionSchema') as mock_schema_class:
                    with patch('app.db.milvus.client.DataType') as mock_dtype:
                        mock_dtype.FLOAT_VECTOR = 101
                        
                        mock_utility.has_collection = Mock(return_value=True)
                        
                        mock_field = MagicMock()
                        mock_field.name = "embedding"
                        mock_field.dtype = 101
                        mock_field.params = {"dim": 512}
                        
                        mock_existing_schema = MagicMock()
                        mock_existing_schema.fields = [mock_field]
                        
                        mock_existing_collection = MagicMock()
                        mock_existing_collection.schema = mock_existing_schema
                        
                        mock_new_collection = MagicMock()
                        mock_new_collection.create_index = Mock()
                        
                        call_count = [0]
                        def collection_side_effect(*args, **kwargs):
                            call_count[0] += 1
                            if call_count[0] == 1:
                                return mock_existing_collection
                            return mock_new_collection
                        
                        mock_collection_class.side_effect = collection_side_effect
                        
                        mock_schema = Mock()
                        mock_schema.collection_name = "bookmarks"
                        mock_schema.embedding_dim = 1536
                        mock_schema.schema_version = 1
                        mock_schema.get_collection_schema = Mock(return_value=Mock())
                        mock_schema.get_index_params = Mock(return_value={})
                        mock_schema.get_schema_version_collection_name = Mock(return_value="bookmarks_version")
                        mock_schema.get_schema_version_fields = Mock(return_value=[])
                        
                        MilvusClient._instance = None
                        MilvusClient._initialized = False
                        
                        client = MilvusClient()
                        client._connected = True
                        
                        with patch.object(client, '_get_schema_version', return_value=0):
                            result = client._init_collection(mock_schema)
                        
                        mock_utility.drop_collection.assert_called()


class TestMilvusClientGetCollection:
    def test_get_collection_from_cache(self):
        MilvusClient._instance = None
        MilvusClient._initialized = False
        
        client = MilvusClient()
        mock_collection = Mock()
        client._collections["bookmarks"] = mock_collection
        
        result = client.get_collection("bookmarks")
        
        assert result is mock_collection

    def test_get_collection_initializes_if_not_cached(self):
        with patch.object(MilvusClient, 'init_collections') as mock_init:
            MilvusClient._instance = None
            MilvusClient._initialized = False
            
            client = MilvusClient()
            mock_collection = Mock()
            client._collections["bookmarks"] = mock_collection
            
            mock_init.return_value = None
            
            result = client.get_collection("bookmarks")
            
            assert result is mock_collection


class TestMilvusClientInitCollections:
    def test_init_collections_calls_connect(self):
        with patch.object(MilvusClient, 'connect') as mock_connect:
            with patch('app.db.milvus.client.SchemaRegistry') as mock_registry:
                mock_registry.get_all = Mock(return_value=[])
                
                MilvusClient._instance = None
                MilvusClient._initialized = False
                
                client = MilvusClient()
                client.init_collections()
                
                mock_connect.assert_called_once()

    def test_init_collections_raises_on_connect_failure(self):
        with patch.object(MilvusClient, 'connect') as mock_connect:
            mock_connect.side_effect = ConnectionError("Cannot connect")
            
            MilvusClient._instance = None
            MilvusClient._initialized = False
            
            client = MilvusClient()
            
            with pytest.raises(ConnectionError):
                client.init_collections()
