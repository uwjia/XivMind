import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.db.milvus.conversation_repo import MilvusConversationRepository
from app.services.conversation.types import ConversationMeta


class TestMilvusConversationRepositoryGetConversation:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversation_found(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_conversation_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversation("test-session-123")
            
            assert result is not None
            assert result.session_id == "test-session-123"
            assert result.title == "Test Conversation"
            assert result.mode == "search"

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversation("nonexistent")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_with_none_mode(self, repo, sample_conversation_entity):
        entity = {**sample_conversation_entity, "mode": None}
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversation("test-session-123")
            
            assert result.mode == "search"


class TestMilvusConversationRepositorySaveConversation:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_save_conversation_success(self, repo):
        mock_collection = Mock()
        mock_collection.upsert = Mock()
        
        conversation = ConversationMeta(
            session_id="test-session-123",
            user_id="test-user",
            title="Test Conversation",
            mode="search",
            starred=False,
            pinned=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0,
        )
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.save_conversation(conversation)
            
            assert result is True
            mock_collection.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_conversation_creates_valid_data(self, repo):
        mock_collection = Mock()
        upserted_data = None
        
        def capture_upsert(data):
            nonlocal upserted_data
            upserted_data = data
        
        mock_collection.upsert = Mock(side_effect=capture_upsert)
        
        conversation = ConversationMeta(
            session_id="test-session-123",
            user_id="test-user",
            title="Test",
            mode="assistant",
            starred=True,
            pinned=True,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 2, 0, 0, 0),
            message_count=10,
        )
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            await repo.save_conversation(conversation)
            
            assert upserted_data is not None
            assert upserted_data[0][0] == "test-session-123"
            assert upserted_data[1][0] == "test-user"
            assert upserted_data[2][0] == "Test"
            assert upserted_data[3][0] == "assistant"
            assert upserted_data[4][0] is True
            assert upserted_data[5][0] is True
            assert upserted_data[8][0] == 10


class TestMilvusConversationRepositoryGetConversations:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversations_by_user(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "session_id": "session-1"},
            {**sample_conversation_entity, "session_id": "session-2"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversations("test-user", limit=50)
            
            assert len(result) == 2
            assert all(isinstance(c, ConversationMeta) for c in result)

    @pytest.mark.asyncio
    async def test_get_conversations_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversations("test-user")
            
            assert result == []


class TestMilvusConversationRepositoryGetConversationsByMode:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversations_by_mode(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "mode": "search"},
            {**sample_conversation_entity, "mode": "search"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversations_by_mode("test-user", "search")
            
            assert len(result) == 2
            assert all(c.mode == "search" for c in result)

    @pytest.mark.asyncio
    async def test_get_conversations_by_mode_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_conversations_by_mode("test-user", "search")
            
            assert result == []


class TestMilvusConversationRepositoryGetLatestConversationByMode:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_get_latest_conversation_by_mode(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "updated_at": "2024-01-01T00:00:00"},
            {**sample_conversation_entity, "updated_at": "2024-01-03T00:00:00"},
            {**sample_conversation_entity, "updated_at": "2024-01-02T00:00:00"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_latest_conversation_by_mode("test-user", "search")
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_latest_conversation_by_mode_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.get_latest_conversation_by_mode("test-user", "assistant")
            
            assert result is None


class TestMilvusConversationRepositoryDeleteConversation:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_delete_conversation(self, repo):
        mock_collection = Mock()
        mock_collection.delete = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.delete_conversation("test-session-123")
            
            assert result is True
            mock_collection.delete.assert_called_once()


class TestMilvusConversationRepositorySearchConversations:
    @pytest.fixture
    def repo(self):
        return MilvusConversationRepository()

    @pytest.mark.asyncio
    async def test_search_conversations_by_title(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "title": "Machine Learning Discussion"},
            {**sample_conversation_entity, "title": "Other Topic"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.search_conversations("machine", "test-user")
            
            assert len(result) == 1
            assert "Machine" in result[0].title

    @pytest.mark.asyncio
    async def test_search_conversations_case_insensitive(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "title": "MACHINE LEARNING"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.search_conversations("machine", "test-user")
            
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_conversations_no_results(self, repo, sample_conversation_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_conversation_entity, "title": "Some Topic"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.search_conversations("nonexistent", "test-user")
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_conversations_empty_collection(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = await repo.search_conversations("query", "test-user")
            
            assert result == []
