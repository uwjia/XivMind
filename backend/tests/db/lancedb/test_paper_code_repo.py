import pytest
from unittest.mock import Mock, patch
import pandas as pd

from app.db.lancedb.paper_code_repo import LanceDBPaperCodeRepository


class TestLanceDBPaperCodeRepositoryUpsert:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperCodeRepository()

    def test_upsert_single_code(self, repo, sample_code_data):
        mock_table = Mock()
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.upsert_paper_codes([sample_code_data])
            
            assert result == 1
            mock_table.merge_insert.assert_called_once_with("id")

    def test_upsert_multiple_codes(self, repo, sample_code_data):
        codes = [
            {**sample_code_data, "paper_id": "2301.00001"},
            {**sample_code_data, "paper_id": "2301.00002"},
            {**sample_code_data, "paper_id": "2301.00003"},
        ]
        
        mock_table = Mock()
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
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
        
        mock_table = Mock()
        mock_merge_insert = Mock()
        mock_merge_insert.when_matched_update_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.when_not_matched_insert_all = Mock(return_value=mock_merge_insert)
        mock_merge_insert.execute = Mock()
        mock_table.merge_insert = Mock(return_value=mock_merge_insert)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.upsert_paper_codes([data])
            
            assert result == 1


class TestLanceDBPaperCodeRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperCodeRepository()

    def test_get_code_by_paper_id_found(self, repo, sample_code_entity):
        mock_table = Mock()
        df = pd.DataFrame([sample_code_entity])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_code_by_paper_id("2301.12345")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345"
            assert result["url"] == sample_code_entity["url"]

    def test_get_code_by_paper_id_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_code_by_paper_id("nonexistent")
            
            assert result is None

    def test_get_code_empty_table(self, repo):
        mock_table = Mock()
        mock_table.count_rows = Mock(return_value=0)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_code_by_paper_id("2301.12345")
            
            assert result is None


class TestLanceDBPaperCodeRepositoryGetPaperIdsWithCode:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperCodeRepository()

    def test_get_paper_ids_with_data(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.00001"},
            {"paper_id": "2301.00002"},
            {"paper_id": "2301.00001"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_paper_ids_with_code()
            
            assert len(result) == 2
            assert "2301.00001" in result
            assert "2301.00002" in result

    def test_get_paper_ids_empty_table(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_paper_ids_with_code()
            
            assert result == []


class TestLanceDBPaperCodeRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperCodeRepository()

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_all_have_code(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"id": "2301.00001"},
            {"id": "2301.00002"},
            {"id": "2301.00003"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=3)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": True,
                "2301.00003": True,
            }

    def test_check_batch_partial_have_code(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"id": "2301.00001"},
            {"id": "2301.00003"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=2)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": True,
                "2301.00002": False,
                "2301.00003": True,
                "2301.00004": False,
            }

    def test_check_batch_none_have_code(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=0)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            paper_ids = ["2301.00001", "2301.00002"]
            result = repo.check_batch(paper_ids)
            
            assert result == {
                "2301.00001": False,
                "2301.00002": False,
            }

    def test_check_batch_single_paper_has_code(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "2301.12345"}])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=1)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.check_batch(["2301.12345"])
            assert result == {"2301.12345": True}


class TestLanceDBPaperCodeRepositoryGetCodesByPaperIds:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperCodeRepository()

    def test_get_codes_by_paper_ids_found(self, repo, sample_code_entity):
        mock_table = Mock()
        df = pd.DataFrame([sample_code_entity])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=1)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_codes_by_paper_ids(["2301.12345"])
            
            assert result["2301.12345"] is not None
            assert result["2301.12345"]["url"] == sample_code_entity["url"]

    def test_get_codes_by_paper_ids_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=0)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_codes_by_paper_ids(["2301.99999"])
            
            assert result["2301.99999"] is None

    def test_get_codes_by_paper_ids_mixed(self, repo, sample_code_entity):
        mock_table = Mock()
        df = pd.DataFrame([sample_code_entity])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.count_rows = Mock(return_value=1)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_codes_by_paper_ids(["2301.12345", "2301.99999"])
            
            assert result["2301.12345"] is not None
            assert result["2301.99999"] is None

    def test_get_codes_empty_list(self, repo):
        result = repo.get_codes_by_paper_ids([])
        assert result == {}


class TestLanceDBPaperCodeRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = LanceDBPaperCodeRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = LanceDBPaperCodeRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = LanceDBPaperCodeRepository._safe_str("test string", max_len=4)
        assert result == "test"

    def test_safe_str_with_int(self):
        result = LanceDBPaperCodeRepository._safe_str(123)
        assert result == "123"
