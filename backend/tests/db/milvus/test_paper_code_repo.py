import pytest
from unittest.mock import Mock, patch

from app.db.milvus.paper_code_repo import MilvusPaperCodeRepository


class TestMilvusPaperCodeRepositoryUpsert:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_upsert_single_code(self, repo, sample_code_data):
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        mock_collection.load = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.upsert_paper_codes([sample_code_data])
            
            assert result == 1
            mock_collection.upsert.assert_called_once()

    def test_upsert_multiple_codes(self, repo, sample_code_data):
        codes = [
            {**sample_code_data, "paper_id": "2301.00001"},
            {**sample_code_data, "paper_id": "2301.00002"},
            {**sample_code_data, "paper_id": "2301.00003"},
        ]
        
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        mock_collection.load = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.upsert_paper_codes(codes)
            
            assert result == 3

    def test_upsert_empty_list(self, repo):
        result = repo.upsert_paper_codes([])
        assert result == 0

    def test_upsert_with_none_values(self, repo):
        data = {
            "paper_id": "2301.12345",
            "url": "https://github.com/test/repo",
            "platform": None,
            "owner": None,
            "repo": None,
        }
        
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        mock_collection.load = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.upsert_paper_codes([data])
            
            assert result == 1


class TestMilvusPaperCodeRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_get_code_by_paper_id_found(self, repo, sample_code_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_code_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_code_by_paper_id("2301.12345")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345"
            assert result["url"] == sample_code_entity["url"]

    def test_get_code_by_paper_id_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_code_by_paper_id("nonexistent")
            
            assert result is None

    def test_get_code_handles_exception(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(side_effect=Exception("Query failed"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_code_by_paper_id("2301.12345")
            
            assert result is None


class TestMilvusPaperCodeRepositoryGetPaperIdsWithCode:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_get_paper_ids_with_data(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00002"},
            {"paper_id": "2301.00001"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_paper_ids_with_code()
            
            assert len(result) == 2
            assert "2301.00001" in result
            assert "2301.00002" in result

    def test_get_paper_ids_empty_collection(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_paper_ids_with_code()
            
            assert result == []

    def test_get_paper_ids_handles_exception(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(side_effect=Exception("Query failed"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_paper_ids_with_code()
            
            assert result == []


class TestMilvusPaperCodeRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_all_have_code(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"id": "2301.00001"},
            {"id": "2301.00002"},
            {"id": "2301.00003"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": True,
                "2301.00003": True,
            }

    def test_check_batch_partial_have_code(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"id": "2301.00001"},
            {"id": "2301.00003"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": False,
                "2301.00003": True,
                "2301.00004": False,
            }

    def test_check_batch_none_have_code(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
            }

    def test_check_batch_single_paper_has_code(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{"id": "2301.12345"}])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.check_batch(["2301.12345"])
            assert result == {"2301.12345": True}

    def test_check_batch_handles_exception(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(side_effect=Exception("Query failed"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            paper_ids = ["2301.00001", "2301.00002"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
            }


class TestMilvusPaperCodeRepositoryGetCodesByPaperIds:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_get_codes_by_paper_ids_found(self, repo, sample_code_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_code_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_codes_by_paper_ids(["2301.12345"])
            
            assert result["2301.12345"] is not None
            assert result["2301.12345"]["url"] == sample_code_entity["url"]

    def test_get_codes_by_paper_ids_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_codes_by_paper_ids(["2301.99999"])
            
            assert result["2301.99999"] is None

    def test_get_codes_by_paper_ids_mixed(self, repo, sample_code_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_code_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_codes_by_paper_ids(["2301.12345", "2301.99999"])
            
            assert result["2301.12345"] is not None
            assert result["2301.99999"] is None

    def test_get_codes_empty_list(self, repo):
        result = repo.get_codes_by_paper_ids([])
        assert result == {}

    def test_get_codes_handles_exception(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(side_effect=Exception("Query failed"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_codes_by_paper_ids(["2301.12345"])
            
            assert result["2301.12345"] is None


class TestMilvusPaperCodeRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = MilvusPaperCodeRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = MilvusPaperCodeRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = MilvusPaperCodeRepository._safe_str("test string", max_len=4)
        assert result == "test"

    def test_safe_str_with_int(self):
        result = MilvusPaperCodeRepository._safe_str(123)
        assert result == "123"


class TestMilvusPaperCodeRepositoryEntityToResponse:
    @pytest.fixture
    def repo(self):
        return MilvusPaperCodeRepository()

    def test_entity_to_response(self, repo, sample_code_entity):
        result = repo._entity_to_response(sample_code_entity)
        
        assert result["id"] == sample_code_entity["id"]
        assert result["paper_id"] == sample_code_entity["paper_id"]
        assert result["url"] == sample_code_entity["url"]
        assert result["platform"] == sample_code_entity["platform"]

    def test_entity_to_response_with_missing_fields(self, repo):
        entity = {"id": "test-id"}
        result = repo._entity_to_response(entity)
        
        assert result["id"] == "test-id"
        assert result["url"] == ""
        assert result["platform"] == ""
