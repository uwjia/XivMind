import pytest
from unittest.mock import Mock, patch, MagicMock
import threading

from app.db.lancedb.client import LanceDBClient, lancedb_client


class TestLanceDBClientSingleton:
    def test_singleton_returns_same_instance(self):
        LanceDBClient._instance = None
        LanceDBClient._initialized = False
        
        instance1 = LanceDBClient()
        instance2 = LanceDBClient()
        
        assert instance1 is instance2

    def test_singleton_thread_safety(self):
        LanceDBClient._instance = None
        LanceDBClient._initialized = False
        
        instances = []
        
        def create_instance():
            instances.append(LanceDBClient())
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert all(inst is instances[0] for inst in instances)

    def test_global_client_instance(self):
        assert lancedb_client is not None
        assert isinstance(lancedb_client, LanceDBClient)


class TestLanceDBClientConnect:
    def test_connect_success(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                result = client.connect("/tmp/test_db")
                
                assert result is True
                assert client._connected is True
                mock_lancedb.connect.assert_called_once_with("/tmp/test_db")

    def test_connect_already_connected(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                mock_lancedb.connect.reset_mock()
                
                result = client.connect("/tmp/test_db")
                
                assert result is True
                mock_lancedb.connect.assert_not_called()

    def test_connect_uses_settings_path(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect()
                
                mock_lancedb.connect.assert_called_once_with(
                    mock_settings.LANCEDB_PATH
                )

    def test_connect_failure_raises_error(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_lancedb.connect = Mock(side_effect=Exception("Connection failed"))
                
                client = LanceDBClient()
                
                with pytest.raises(ConnectionError) as exc_info:
                    client.connect("/tmp/test_db")
                
                assert "Connection failed" in str(exc_info.value)

    def test_connect_lancedb_not_available(self, mock_settings):
        with patch('app.db.lancedb.client.LANCEDB_AVAILABLE', False):
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                client = LanceDBClient()
                
                with pytest.raises(ImportError) as exc_info:
                    client.connect("/tmp/test_db")
                
                assert "LanceDB is not installed" in str(exc_info.value)


class TestLanceDBClientSchemaMatches:
    def test_schema_matches_identical(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_field1 = Mock()
                mock_field1.name = "id"
                mock_field1.type = "string"
                mock_field2 = Mock()
                mock_field2.name = "title"
                mock_field2.type = "string"
                
                mock_schema = [mock_field1, mock_field2]
                
                mock_table = Mock()
                mock_table.schema = mock_schema
                
                mock_expected_schema = Mock()
                mock_expected_schema.get_pyarrow_schema = Mock(return_value=mock_schema)
                
                mock_db = Mock()
                mock_db.open_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                result = client._schema_matches("test_table", mock_expected_schema)
                
                assert result is True

    def test_schema_matches_different_length(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_table = Mock()
                mock_current_schema = Mock()
                mock_field1 = Mock()
                mock_field1.name = "id"
                mock_current_schema.__iter__ = Mock(return_value=iter([mock_field1]))
                mock_table.schema = mock_current_schema
                
                mock_expected_schema = Mock()
                mock_expected_pa = Mock()
                mock_field2 = Mock()
                mock_field2.name = "id"
                mock_field3 = Mock()
                mock_field3.name = "title"
                mock_expected_pa.__iter__ = Mock(return_value=iter([mock_field2, mock_field3]))
                mock_expected_schema.get_pyarrow_schema = Mock(return_value=mock_expected_pa)
                
                mock_db = Mock()
                mock_db.open_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                result = client._schema_matches("test_table", mock_expected_schema)
                
                assert result is False

    def test_schema_matches_different_type(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_table = Mock()
                mock_current_schema = Mock()
                mock_field1 = Mock()
                mock_field1.name = "id"
                mock_field1.type = "string"
                mock_current_schema.__iter__ = Mock(return_value=iter([mock_field1]))
                mock_table.schema = mock_current_schema
                
                mock_expected_schema = Mock()
                mock_expected_pa = Mock()
                mock_field2 = Mock()
                mock_field2.name = "id"
                mock_field2.type = "int"
                mock_expected_pa.__iter__ = Mock(return_value=iter([mock_field2]))
                mock_expected_schema.get_pyarrow_schema = Mock(return_value=mock_expected_pa)
                
                mock_db = Mock()
                mock_db.open_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                result = client._schema_matches("test_table", mock_expected_schema)
                
                assert result is False

    def test_schema_matches_exception(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.open_table = Mock(side_effect=Exception("Table not found"))
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                mock_schema = Mock()
                result = client._schema_matches("test_table", mock_schema)
                
                assert result is False


class TestLanceDBClientInitTables:
    def test_init_tables_creates_missing_tables(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=[])
                mock_table = Mock()
                mock_db.create_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                mock_schema = Mock()
                mock_schema.table_name = "test_table"
                mock_schema.get_pyarrow_schema = Mock(return_value=Mock())
                
                with patch('app.db.lancedb.schemas.SchemaRegistry.get_all', return_value=[mock_schema]):
                    client = LanceDBClient()
                    client.connect("/tmp/test_db")
                    client.init_tables()
                    
                    mock_db.create_table.assert_called()

    def test_init_tables_already_initialized(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=[])
                mock_table = Mock()
                mock_db.create_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                mock_schema = Mock()
                mock_schema.table_name = "test_table"
                mock_schema.get_pyarrow_schema = Mock(return_value=Mock())
                
                with patch('app.db.lancedb.schemas.SchemaRegistry.get_all', return_value=[mock_schema]):
                    client = LanceDBClient()
                    client.connect("/tmp/test_db")
                    client.init_tables()
                    
                    call_count = mock_db.create_table.call_count
                    client.init_tables()
                    
                    assert mock_db.create_table.call_count == call_count

    def test_init_tables_force_recreate(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=["test_table"])
                mock_table = Mock()
                mock_db.create_table = Mock(return_value=mock_table)
                mock_db.open_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                mock_schema = Mock()
                mock_schema.table_name = "test_table"
                mock_schema.get_pyarrow_schema = Mock(return_value=Mock())
                
                with patch('app.db.lancedb.schemas.SchemaRegistry.get_all', return_value=[mock_schema]):
                    client = LanceDBClient()
                    client.connect("/tmp/test_db")
                    client.init_tables(force_recreate=True)
                    
                    mock_db.create_table.assert_called()


class TestLanceDBClientDropAllTables:
    def test_drop_all_tables(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=["table1", "table2"])
                mock_db.drop_table = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                client.drop_all_tables()
                
                assert mock_db.drop_table.call_count == 2
                assert client._tables_initialized is False

    def test_drop_all_tables_not_connected(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=["table1"])
                mock_db.drop_table = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.drop_all_tables()
                
                mock_lancedb.connect.assert_called()


class TestLanceDBClientGetTable:
    def test_get_table_from_cache(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                mock_table = Mock()
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                client._tables["test_table"] = mock_table
                
                result = client.get_table("test_table")
                
                assert result is mock_table

    def test_get_table_from_database(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_table = Mock()
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=["test_table"])
                mock_db.open_table = Mock(return_value=mock_table)
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                client._tables["test_table"] = mock_table
                client._tables_initialized = True
                
                result = client.get_table("test_table")
                
                assert result is mock_table

    def test_get_table_not_connected(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_db.table_names = Mock(return_value=[])
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                
                client.get_table("test_table")
                
                mock_lancedb.connect.assert_called()


class TestLanceDBClientGetDb:
    def test_get_db_when_connected(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                client.connect("/tmp/test_db")
                
                result = client.get_db()
                
                assert result is mock_db

    def test_get_db_when_not_connected(self, mock_settings):
        with patch('app.db.lancedb.client.lancedb') as mock_lancedb:
            with patch('app.db.lancedb.client.get_settings', return_value=mock_settings):
                LanceDBClient._instance = None
                LanceDBClient._initialized = False
                
                mock_db = Mock()
                mock_lancedb.connect = Mock(return_value=mock_db)
                
                client = LanceDBClient()
                
                result = client.get_db()
                
                assert result is mock_db
                mock_lancedb.connect.assert_called()
