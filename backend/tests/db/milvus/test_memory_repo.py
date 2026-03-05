import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from app.db.milvus.memory_repo import MilvusMemoryRepository
from app.services.memory.types import (
    CoreMemory,
    RecallMemory,
    ArchivalMemory,
    MemoryConfig,
    MemoryCategory,
)


class TestMilvusMemoryRepositoryCoreMemory:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_get_core_memory_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{
            "user_id": "test-user",
            "research_interests": '["ml", "nlp"]',
            "preferred_domains": '["cs.AI"]',
            "frequently_used_skills": '["summarize"]',
            "language_preference": "en-US",
            "summary_style": "detailed",
            "custom_instructions": "test",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }])
        
        with patch.object(repo, '_get_core_collection', return_value=mock_collection):
            result = await repo.get_core_memory("test-user")
            
            assert result is not None
            assert result.user_id == "test-user"
            assert result.research_interests == ["ml", "nlp"]

    @pytest.mark.asyncio
    async def test_get_core_memory_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_core_collection', return_value=mock_collection):
            result = await repo.get_core_memory("test-user")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_core_memory_from_cache(self, repo):
        cached_memory = CoreMemory(
            user_id="test-user",
            research_interests=["cached"],
            preferred_domains=[],
            frequently_used_skills=[],
            language_preference="en-US",
            summary_style="detailed",
            custom_instructions="",
        )
        repo._core_memory_cache["test-user"] = cached_memory
        
        result = await repo.get_core_memory("test-user")
        
        assert result is cached_memory

    @pytest.mark.asyncio
    async def test_save_core_memory(self, repo):
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        mock_collection.flush = Mock()
        
        memory = CoreMemory(
            user_id="test-user",
            research_interests=["ml"],
            preferred_domains=["cs.AI"],
            frequently_used_skills=["summarize"],
            language_preference="en-US",
            summary_style="detailed",
            custom_instructions="test",
        )
        
        with patch.object(repo, '_get_core_collection', return_value=mock_collection):
            result = await repo.save_core_memory(memory)
            
            assert result is True
            mock_collection.upsert.assert_called_once()
            assert "test-user" in repo._core_memory_cache

    @pytest.mark.asyncio
    async def test_save_core_memory_sets_created_at(self, repo):
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        mock_collection.flush = Mock()
        
        memory = CoreMemory(
            user_id="test-user",
            research_interests=[],
            preferred_domains=[],
            frequently_used_skills=[],
            language_preference="en-US",
            summary_style="detailed",
            custom_instructions="",
        )
        
        with patch.object(repo, '_get_core_collection', return_value=mock_collection):
            await repo.save_core_memory(memory)
            
            assert memory.created_at is not None
            assert memory.updated_at is not None

    @pytest.mark.asyncio
    async def test_clear_core_memory(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        repo._core_memory_cache["test-user"] = Mock()
        
        with patch.object(repo, '_get_core_collection', return_value=mock_collection):
            result = await repo.clear_core_memory("test-user")
            
            assert result is True
            assert "test-user" not in repo._core_memory_cache


class TestMilvusMemoryRepositoryRecallMemory:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_insert_recall_memory_success(self, repo):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        memory = RecallMemory(
            memory_id="test-memory",
            user_id="test-user",
            session_id="test-session",
            content="Test content",
            embedding=[0.1] * 1536,
            importance_score=0.8,
            access_count=0,
            timestamp=datetime.utcnow(),
            category=MemoryCategory.CONTEXT,
            auto_created=False,
        )
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.insert_recall_memory(memory)
            
            assert result is True
            mock_collection.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_recall_memory_without_embedding(self, repo):
        mock_collection = Mock()
        
        memory = RecallMemory(
            memory_id="test-memory",
            user_id="test-user",
            session_id="test-session",
            content="Test content",
            embedding=None,
            importance_score=0.8,
            access_count=0,
            timestamp=datetime.utcnow(),
            category=MemoryCategory.CONTEXT,
            auto_created=False,
        )
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.insert_recall_memory(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_insert_recall_memory_with_empty_embedding(self, repo):
        mock_collection = Mock()
        
        memory = RecallMemory(
            memory_id="test-memory",
            user_id="test-user",
            session_id="test-session",
            content="Test content",
            embedding=[],
            importance_score=0.8,
            access_count=0,
            timestamp=datetime.utcnow(),
            category=MemoryCategory.CONTEXT,
            auto_created=False,
        )
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.insert_recall_memory(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_get_recall_memories(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "memory_id": "mem-1",
                "user_id": "test-user",
                "session_id": "session-1",
                "content": "Content 1",
                "importance_score": 0.8,
                "access_count": 2,
                "timestamp": "2024-01-02T00:00:00",
                "category": "context",
                "auto_created": False,
                "ttl_days": 30,
                "metadata": "{}",
            },
            {
                "memory_id": "mem-2",
                "user_id": "test-user",
                "session_id": "session-2",
                "content": "Content 2",
                "importance_score": 0.5,
                "access_count": 1,
                "timestamp": "2024-01-01T00:00:00",
                "category": "preference",
                "auto_created": True,
                "ttl_days": 0,
                "metadata": "{}",
            },
        ])
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.get_recall_memories("test-user", limit=10)
            
            assert len(result) == 2
            assert all(isinstance(m, RecallMemory) for m in result)

    @pytest.mark.asyncio
    async def test_delete_recall_memory(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.delete_recall_memory("test-memory")
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_recall_memories_batch(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.delete_recall_memories_batch(["mem-1", "mem-2"])
            
            assert result == 2

    @pytest.mark.asyncio
    async def test_delete_recall_memories_batch_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.delete_recall_memories_batch([])
            
            assert result == 0

    @pytest.mark.asyncio
    async def test_search_recall_memories(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        mock_hit = Mock()
        mock_hit.score = 0.9
        mock_hit.entity = {
            "memory_id": "mem-1",
            "user_id": "test-user",
            "session_id": "session-1",
            "content": "Related content",
            "importance_score": 0.8,
            "access_count": 2,
            "timestamp": "2024-01-01T00:00:00",
            "category": "context",
            "auto_created": False,
            "ttl_days": 30,
            "metadata": "{}",
        }
        
        mock_collection.search = Mock(return_value=[[mock_hit]])
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.search_recall_memories(
                [0.1] * 1536, "test-user", top_k=5
            )
            
            assert len(result) == 1
            assert "similarity_score" in result[0]

    @pytest.mark.asyncio
    async def test_clear_recall_memories(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.clear_recall_memories("test-user")
            
            assert result is True


class TestMilvusMemoryRepositoryArchivalMemory:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_insert_archival_memory_success(self, repo):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        memory = ArchivalMemory(
            memory_id="test-archival",
            user_id="test-user",
            content_type="note",
            title="Test Note",
            content="Test content",
            embedding=[0.1] * 1536,
            source_papers=["2301.12345"],
            tags=["test"],
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.insert_archival_memory(memory)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_insert_archival_memory_without_embedding(self, repo):
        mock_collection = Mock()
        
        memory = ArchivalMemory(
            memory_id="test-archival",
            user_id="test-user",
            content_type="note",
            title="Test Note",
            content="Test content",
            embedding=None,
            source_papers=[],
            tags=[],
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.insert_archival_memory(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_get_archival_memories(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "memory_id": "arch-1",
                "user_id": "test-user",
                "content_type": "note",
                "title": "Note 1",
                "content": "Content 1",
                "source_papers": "[]",
                "tags": "[]",
                "created_at": "2024-01-02T00:00:00",
                "last_accessed": "2024-01-02T00:00:00",
            },
        ])
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.get_archival_memories("test-user", limit=10)
            
            assert len(result) == 1
            assert all(isinstance(m, ArchivalMemory) for m in result)

    @pytest.mark.asyncio
    async def test_delete_archival_memory(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.delete_archival_memory("test-archival")
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_archival_memories_batch(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.delete_archival_memories_batch(["arch-1", "arch-2"])
            
            assert result == 2

    @pytest.mark.asyncio
    async def test_search_archival_memories(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        mock_hit = Mock()
        mock_hit.score = 0.85
        mock_hit.entity = {
            "memory_id": "arch-1",
            "user_id": "test-user",
            "content_type": "note",
            "title": "Related Note",
            "content": "Content",
            "source_papers": "[]",
            "tags": "[]",
            "created_at": "2024-01-01T00:00:00",
            "last_accessed": "2024-01-01T00:00:00",
        }
        
        mock_collection.search = Mock(return_value=[[mock_hit]])
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.search_archival_memories(
                [0.1] * 1536, "test-user", top_k=5
            )
            
            assert len(result) == 1
            assert "similarity_score" in result[0]

    @pytest.mark.asyncio
    async def test_clear_archival_memories(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_archival_collection', return_value=mock_collection):
            result = await repo.clear_archival_memories("test-user")
            
            assert result is True


class TestMilvusMemoryRepositoryMemoryConfig:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_get_memory_config_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{
            "user_id": "test-user",
            "auto_capture": True,
            "auto_recall": True,
            "capture_max_chars": 500,
            "recall_top_k": 5,
            "recall_min_score": 0.7,
            "auto_forget_days": 30,
            "importance_threshold": 0.3,
            "extract": False,
        }])
        
        with patch.object(repo, '_get_config_collection', return_value=mock_collection):
            result = await repo.get_memory_config("test-user")
            
            assert result is not None
            assert result.auto_capture is True
            assert result.recall_top_k == 5

    @pytest.mark.asyncio
    async def test_get_memory_config_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_config_collection', return_value=mock_collection):
            result = await repo.get_memory_config("test-user")
            
            assert isinstance(result, MemoryConfig)

    @pytest.mark.asyncio
    async def test_save_memory_config(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        config = MemoryConfig(
            auto_capture=True,
            auto_recall=True,
            capture_max_chars=500,
            recall_top_k=5,
            recall_min_score=0.7,
            auto_forget_days=30,
            importance_threshold=0.3,
            extract=False,
        )
        
        with patch.object(repo, '_get_config_collection', return_value=mock_collection):
            with patch.object(repo, 'get_memory_config', return_value=None):
                result = await repo.save_memory_config("test-user", config)
                
                assert result is True


class TestMilvusMemoryRepositoryMemoryStats:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_get_memory_stats(self, repo):
        recall_collection = Mock()
        recall_collection.load = Mock()
        recall_collection.query = Mock(return_value=[
            {"memory_id": "mem-1"},
            {"memory_id": "mem-2"},
        ])
        
        archival_collection = Mock()
        archival_collection.load = Mock()
        archival_collection.query = Mock(return_value=[
            {"memory_id": "arch-1"},
        ])
        
        core_collection = Mock()
        core_collection.load = Mock()
        core_collection.query = Mock(return_value=[{"user_id": "test-user"}])
        
        def get_collection_side_effect(name):
            if name == "recall_memories":
                return recall_collection
            elif name == "archival_memories":
                return archival_collection
            elif name == "core_memories":
                return core_collection
            return Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=recall_collection):
            with patch.object(repo, '_get_archival_collection', return_value=archival_collection):
                with patch.object(repo, '_get_core_collection', return_value=core_collection):
                    result = await repo.get_memory_stats("test-user")
                    
                    assert result.recall_memory_count == 2
                    assert result.archival_memory_count == 1
                    assert result.total_memories == 3


class TestMilvusMemoryRepositoryClearAll:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_clear_all_memories(self, repo):
        recall_collection = Mock()
        recall_collection.delete = Mock()
        recall_collection.flush = Mock()
        
        archival_collection = Mock()
        archival_collection.delete = Mock()
        archival_collection.flush = Mock()
        
        core_collection = Mock()
        core_collection.delete = Mock()
        core_collection.flush = Mock()
        
        repo._core_memory_cache["test-user"] = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=recall_collection):
            with patch.object(repo, '_get_archival_collection', return_value=archival_collection):
                with patch.object(repo, '_get_core_collection', return_value=core_collection):
                    result = await repo.clear_all_memories("test-user")
                    
                    assert result is True
                    assert "test-user" not in repo._core_memory_cache


class TestMilvusMemoryRepositoryDeleteByCriteria:
    @pytest.fixture
    def repo(self):
        return MilvusMemoryRepository()

    @pytest.mark.asyncio
    async def test_delete_recall_memories_by_criteria_auto_created(self, repo):
        mock_collection = Mock()
        mock_collection.query = Mock(return_value=[
            {"memory_id": "mem-1"},
        ])
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.delete_recall_memories_by_criteria(
                "test-user", auto_created_only=True
            )
            
            assert result == 1

    @pytest.mark.asyncio
    async def test_delete_recall_memories_by_criteria_max_importance(self, repo):
        mock_collection = Mock()
        mock_collection.query = Mock(return_value=[
            {"memory_id": "mem-1"},
        ])
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_recall_collection', return_value=mock_collection):
            result = await repo.delete_recall_memories_by_criteria(
                "test-user", max_importance=0.5
            )
            
            assert result == 1
