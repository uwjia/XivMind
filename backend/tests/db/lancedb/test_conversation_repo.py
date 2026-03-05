import pytest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from app.db.lancedb.conversation_repo import LanceDBConversationRepository
from app.services.conversation.types import ConversationMeta


class TestLanceDBConversationRepositoryGetConversation:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversation_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "session_id": "test-session-123",
            "user_id": "test-user",
            "title": "Test Conversation",
            "mode": "search",
            "starred": False,
            "pinned": False,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "message_count": 5,
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversation("test-session-123")
            
            assert result is not None
            assert result.session_id == "test-session-123"
            assert result.title == "Test Conversation"
            assert result.mode == "search"

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversation("nonexistent")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_with_none_mode(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "session_id": "test-session-123",
            "user_id": "test-user",
            "title": "Test",
            "mode": None,
            "starred": False,
            "pinned": False,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "message_count": 0,
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversation("test-session-123")
            
            assert result.mode == "search"


class TestLanceDBConversationRepositorySaveConversation:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_save_conversation_new(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
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
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.save_conversation(conversation)
            
            assert result is True
            mock_table.delete.assert_called_once()
            mock_table.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_conversation_creates_valid_record(self, repo):
        mock_table = Mock()
        added_record = None
        
        def capture_add(records):
            nonlocal added_record
            added_record = records[0]
        
        mock_table.delete = Mock()
        mock_table.add = Mock(side_effect=capture_add)
        
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
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            await repo.save_conversation(conversation)
            
            assert added_record["session_id"] == "test-session-123"
            assert added_record["user_id"] == "test-user"
            assert added_record["title"] == "Test"
            assert added_record["mode"] == "assistant"
            assert added_record["starred"] is True
            assert added_record["pinned"] is True
            assert added_record["message_count"] == 10
            assert "embedding" in added_record


class TestLanceDBConversationRepositoryGetConversations:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversations_by_user(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Conv 1",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
            {
                "session_id": "session-2",
                "user_id": "test-user",
                "title": "Conv 2",
                "mode": "assistant",
                "starred": True,
                "pinned": False,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "message_count": 10,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversations("test-user", limit=50)
            
            assert len(result) == 2
            assert all(isinstance(c, ConversationMeta) for c in result)

    @pytest.mark.asyncio
    async def test_get_conversations_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversations("test-user")
            
            assert result == []


class TestLanceDBConversationRepositoryGetConversationsByMode:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_get_conversations_by_mode(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Search Conv",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
            {
                "session_id": "session-2",
                "user_id": "test-user",
                "title": "Assistant Conv",
                "mode": "assistant",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "message_count": 10,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversations_by_mode("test-user", "search")
            
            assert len(result) == 1
            assert result[0].mode == "search"

    @pytest.mark.asyncio
    async def test_get_conversations_by_mode_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_conversations_by_mode("test-user", "search")
            
            assert result == []


class TestLanceDBConversationRepositoryGetLatestConversationByMode:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_get_latest_conversation_by_mode(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Old Conv",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
            {
                "session_id": "session-2",
                "user_id": "test-user",
                "title": "New Conv",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-03T00:00:00",
                "message_count": 10,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_latest_conversation_by_mode("test-user", "search")
            
            assert result is not None
            assert result.title == "New Conv"

    @pytest.mark.asyncio
    async def test_get_latest_conversation_by_mode_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Search Conv",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_latest_conversation_by_mode("test-user", "assistant")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_latest_conversation_empty_table(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.get_latest_conversation_by_mode("test-user", "search")
            
            assert result is None


class TestLanceDBConversationRepositoryDeleteConversation:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_delete_conversation(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.delete_conversation("test-session-123")
            
            assert result is True
            mock_table.delete.assert_called_once_with("session_id = 'test-session-123'")


class TestLanceDBConversationRepositorySearchConversations:
    @pytest.fixture
    def repo(self):
        return LanceDBConversationRepository()

    @pytest.mark.asyncio
    async def test_search_conversations_by_title(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Machine Learning Discussion",
                "mode": "assistant",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
            {
                "session_id": "session-2",
                "user_id": "test-user",
                "title": "Other Topic",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "message_count": 3,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.search_conversations("machine", "test-user")
            
            assert len(result) == 1
            assert "Machine" in result[0].title

    @pytest.mark.asyncio
    async def test_search_conversations_case_insensitive(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "MACHINE LEARNING",
                "mode": "assistant",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.search_conversations("machine", "test-user")
            
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_conversations_no_results(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "session_id": "session-1",
                "user_id": "test-user",
                "title": "Some Topic",
                "mode": "search",
                "starred": False,
                "pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "message_count": 5,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.search_conversations("nonexistent", "test-user")
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_conversations_empty_table(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = await repo.search_conversations("query", "test-user")
            
            assert result == []
