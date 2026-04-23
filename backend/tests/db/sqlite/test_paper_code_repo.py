import pytest
import tempfile
import os

from app.db.sqlite.paper_code_repo import SQLitePaperCodeRepository


class TestSQLitePaperCodeRepositoryUpsert:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_paper_codes.db")
            repo = SQLitePaperCodeRepository(db_path)
            yield repo

    def test_upsert_single_code(self, repo, sample_code_data):
        result = repo.upsert_paper_codes([sample_code_data])
        
        assert result == 1
        
        code = repo.get_code_by_paper_id(sample_code_data["paper_id"])
        assert code is not None
        assert code["url"] == sample_code_data["url"]
        assert code["platform"] == sample_code_data["platform"]

    def test_upsert_multiple_codes(self, repo, sample_code_data):
        codes = [
            {**sample_code_data, "paper_id": "2301.00001"},
            {**sample_code_data, "paper_id": "2301.00002"},
            {**sample_code_data, "paper_id": "2301.00003"},
        ]
        
        result = repo.upsert_paper_codes(codes)
        
        assert result == 3
        
        for code in codes:
            saved = repo.get_code_by_paper_id(code["paper_id"])
            assert saved is not None

    def test_upsert_empty_list(self, repo):
        result = repo.upsert_paper_codes([])
        assert result == 0

    def test_upsert_updates_existing(self, repo, sample_code_data):
        repo.upsert_paper_codes([sample_code_data])
        
        updated_data = {**sample_code_data, "url": "https://github.com/updated/repo"}
        result = repo.upsert_paper_codes([updated_data])
        
        assert result == 1
        
        code = repo.get_code_by_paper_id(sample_code_data["paper_id"])
        assert code["url"] == "https://github.com/updated/repo"

    def test_upsert_with_none_values(self, repo):
        data = {
            "paper_id": "2301.12345",
            "url": "https://github.com/test/repo",
            "platform": None,
            "owner": None,
            "repo": None,
        }
        
        result = repo.upsert_paper_codes([data])
        
        assert result == 1
        
        code = repo.get_code_by_paper_id("2301.12345")
        assert code is not None
        assert code["platform"] == ""
        assert code["owner"] == ""


class TestSQLitePaperCodeRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_paper_codes.db")
            repo = SQLitePaperCodeRepository(db_path)
            yield repo

    def test_get_code_by_paper_id_found(self, repo, sample_code_data):
        repo.upsert_paper_codes([sample_code_data])
        
        result = repo.get_code_by_paper_id(sample_code_data["paper_id"])
        
        assert result is not None
        assert result["paper_id"] == sample_code_data["paper_id"]
        assert result["url"] == sample_code_data["url"]

    def test_get_code_by_paper_id_not_found(self, repo):
        result = repo.get_code_by_paper_id("nonexistent")
        
        assert result is None


class TestSQLitePaperCodeRepositoryGetPaperIdsWithCode:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_paper_codes.db")
            repo = SQLitePaperCodeRepository(db_path)
            yield repo

    def test_get_paper_ids_with_data(self, repo, sample_code_data):
        for i in range(3):
            repo.upsert_paper_codes([{**sample_code_data, "paper_id": f"2301.0000{i}"}])
        
        result = repo.get_paper_ids_with_code()
        
        assert len(result) == 3
        assert "2301.00000" in result
        assert "2301.00001" in result
        assert "2301.00002" in result

    def test_get_paper_ids_empty_table(self, repo):
        result = repo.get_paper_ids_with_code()
        
        assert result == []


class TestSQLitePaperCodeRepositoryCheckBatch:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_paper_codes.db")
            repo = SQLitePaperCodeRepository(db_path)
            yield repo

    def test_check_batch_empty_list(self, repo):
        result = repo.check_batch([])
        assert result == {}

    def test_check_batch_all_have_code(self, repo, sample_code_data):
        for i in range(1, 4):
            repo.upsert_paper_codes([{**sample_code_data, "paper_id": f"2301.0000{i}"}])
        
        paper_ids = ["2301.00001", "2301.00002", "2301.00003"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": True,
            "2301.00002": True,
            "2301.00003": True,
        }

    def test_check_batch_partial_have_code(self, repo, sample_code_data):
        repo.upsert_paper_codes([{**sample_code_data, "paper_id": "2301.00001"}])
        repo.upsert_paper_codes([{**sample_code_data, "paper_id": "2301.00003"}])
        
        paper_ids = ["2301.00001", "2301.00002", "2301.00003", "2301.00004"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": True,
            "2301.00002": False,
            "2301.00003": True,
            "2301.00004": False,
        }

    def test_check_batch_none_have_code(self, repo):
        paper_ids = ["2301.00001", "2301.00002"]
        result = repo.check_batch(paper_ids)
        
        assert result == {
            "2301.00001": False,
            "2301.00002": False,
        }

    def test_check_batch_single_paper_has_code(self, repo, sample_code_data):
        repo.upsert_paper_codes([sample_code_data])
        
        result = repo.check_batch([sample_code_data["paper_id"]])
        assert result == {sample_code_data["paper_id"]: True}

    def test_check_batch_single_paper_no_code(self, repo):
        result = repo.check_batch(["2301.99999"])
        assert result == {"2301.99999": False}


class TestSQLitePaperCodeRepositoryGetCodesByPaperIds:
    @pytest.fixture
    def repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_paper_codes.db")
            repo = SQLitePaperCodeRepository(db_path)
            yield repo

    def test_get_codes_by_paper_ids_found(self, repo, sample_code_data):
        repo.upsert_paper_codes([sample_code_data])
        
        result = repo.get_codes_by_paper_ids([sample_code_data["paper_id"]])
        
        assert result[sample_code_data["paper_id"]] is not None
        assert result[sample_code_data["paper_id"]]["url"] == sample_code_data["url"]

    def test_get_codes_by_paper_ids_not_found(self, repo):
        result = repo.get_codes_by_paper_ids(["2301.99999"])
        
        assert result["2301.99999"] is None

    def test_get_codes_by_paper_ids_mixed(self, repo, sample_code_data):
        repo.upsert_paper_codes([sample_code_data])
        
        result = repo.get_codes_by_paper_ids([sample_code_data["paper_id"], "2301.99999"])
        
        assert result[sample_code_data["paper_id"]] is not None
        assert result["2301.99999"] is None

    def test_get_codes_empty_list(self, repo):
        result = repo.get_codes_by_paper_ids([])
        assert result == {}

    def test_get_codes_multiple_papers(self, repo, sample_code_data):
        codes = [
            {**sample_code_data, "paper_id": "2301.00001", "url": "https://github.com/test/repo1"},
            {**sample_code_data, "paper_id": "2301.00002", "url": "https://github.com/test/repo2"},
        ]
        repo.upsert_paper_codes(codes)
        
        result = repo.get_codes_by_paper_ids(["2301.00001", "2301.00002", "2301.00003"])
        
        assert result["2301.00001"]["url"] == "https://github.com/test/repo1"
        assert result["2301.00002"]["url"] == "https://github.com/test/repo2"
        assert result["2301.00003"] is None


class TestSQLitePaperCodeRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = SQLitePaperCodeRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = SQLitePaperCodeRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = SQLitePaperCodeRepository._safe_str("test string", max_len=4)
        assert result == "test"

    def test_safe_str_with_int(self):
        result = SQLitePaperCodeRepository._safe_str(123)
        assert result == "123"
