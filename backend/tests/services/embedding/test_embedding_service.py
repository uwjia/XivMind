import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.embedding_service import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    LocalEmbeddingProvider,
    EmbeddingService,
)


class TestOpenAIEmbeddingProvider:
    def test_init(self):
        provider = OpenAIEmbeddingProvider(
            api_key="test-key",
            model="text-embedding-ada-002"
        )
        assert provider.api_key == "test-key"
        assert provider.model == "text-embedding-ada-002"
        assert provider._dimension == 1536

    def test_get_dimension(self):
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.get_dimension() == 1536

    def test_get_model_name(self):
        provider = OpenAIEmbeddingProvider(
            api_key="test-key",
            model="text-embedding-3-small"
        )
        assert provider.get_model_name() == "text-embedding-3-small"

    def test_encode_success(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response

        provider = OpenAIEmbeddingProvider(api_key="test-key")
        provider._client = mock_client
        
        result = provider.encode("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once_with(
            input="test text",
            model="text-embedding-ada-002"
        )

    def test_encode_batch_success(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        provider = OpenAIEmbeddingProvider(api_key="test-key")
        provider._client = mock_client
        
        result = provider.encode_batch(["text1", "text2"])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]

    def test_encode_batch_empty(self):
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        result = provider.encode_batch([])
        assert result == []

    def test_encode_error(self):
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API Error")

        provider = OpenAIEmbeddingProvider(api_key="test-key")
        provider._client = mock_client
        
        with pytest.raises(Exception, match="API Error"):
            provider.encode("test text")


class TestLocalEmbeddingProvider:
    def test_init(self):
        provider = LocalEmbeddingProvider(model_name="all-MiniLM-L6-v2")
        assert provider.model_name == "all-MiniLM-L6-v2"
        assert provider._dimension == 384

    def test_get_dimension(self):
        provider = LocalEmbeddingProvider()
        assert provider.get_dimension() == 384

    def test_get_model_name(self):
        provider = LocalEmbeddingProvider(model_name="test-model")
        assert provider.get_model_name() == "local:test-model"

    def test_encode_success(self):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        mock_model.get_sentence_embedding_dimension.return_value = 384

        provider = LocalEmbeddingProvider()
        provider._model = mock_model
        
        result = provider.encode("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_model.encode.assert_called_once()

    def test_encode_batch_success(self):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])

        provider = LocalEmbeddingProvider()
        provider._model = mock_model
        
        result = provider.encode_batch(["text1", "text2"])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]

    def test_encode_batch_empty(self):
        provider = LocalEmbeddingProvider()
        result = provider.encode_batch([])
        assert result == []

    def test_import_error(self):
        provider = LocalEmbeddingProvider()
        provider._model = None
        
        with patch.dict('sys.modules', {'sentence_transformers': None}):
            with pytest.raises(ImportError):
                provider._get_model()


class TestEmbeddingService:
    @patch('app.services.embedding_service.get_settings')
    def test_init_use_local_embedding(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialize()

        assert isinstance(service._primary_provider, LocalEmbeddingProvider)
        assert service._fallback_provider is None

    @patch('app.services.embedding_service.get_settings')
    def test_init_with_openai_key(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = False
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialize()

        assert isinstance(service._primary_provider, OpenAIEmbeddingProvider)
        assert isinstance(service._fallback_provider, LocalEmbeddingProvider)

    @patch('app.services.embedding_service.get_settings')
    def test_init_no_openai_key(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = False
        mock_settings.OPENAI_API_KEY = ""
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialize()

        assert isinstance(service._primary_provider, LocalEmbeddingProvider)
        assert service._fallback_provider is None

    @patch('app.services.embedding_service.get_settings')
    def test_encode_success(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialized = True
        
        mock_provider = Mock()
        mock_provider.encode.return_value = [0.1, 0.2]
        mock_provider.get_model_name.return_value = "local:all-MiniLM-L6-v2"
        service._primary_provider = mock_provider
        
        embedding, model = service.encode("test text")

        assert embedding == [0.1, 0.2]
        assert model == "local:all-MiniLM-L6-v2"

    @patch('app.services.embedding_service.get_settings')
    def test_encode_with_fallback(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = False
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialized = True
        
        mock_primary = Mock()
        mock_primary.encode.side_effect = Exception("API Error")
        mock_primary.get_model_name.return_value = "text-embedding-ada-002"
        
        mock_fallback = Mock()
        mock_fallback.encode.return_value = [0.1, 0.2]
        mock_fallback.get_model_name.return_value = "local:all-MiniLM-L6-v2"
        
        service._primary_provider = mock_primary
        service._fallback_provider = mock_fallback
        
        embedding, model = service.encode("test text")

        assert embedding == [0.1, 0.2]
        assert model == "local:all-MiniLM-L6-v2"

    @patch('app.services.embedding_service.get_settings')
    def test_encode_batch_success(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        service._initialized = True
        
        mock_provider = Mock()
        mock_provider.encode_batch.return_value = [[0.1], [0.2]]
        mock_provider.get_model_name.return_value = "local:all-MiniLM-L6-v2"
        service._primary_provider = mock_provider
        
        embeddings, model = service.encode_batch(["text1", "text2"])

        assert len(embeddings) == 2

    @patch('app.services.embedding_service.get_settings')
    def test_encode_batch_empty(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        embeddings, model = service.encode_batch([])

        assert embeddings == []
        assert model == ""

    @patch('app.services.embedding_service.get_settings')
    def test_get_dimension(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        
        mock_provider = Mock()
        mock_provider.get_dimension.return_value = 384
        service._primary_provider = mock_provider
        
        dimension = service.get_dimension()

        assert dimension == 384

    @patch('app.services.embedding_service.get_settings')
    def test_is_available(self, mock_get_settings):
        mock_settings = Mock()
        mock_settings.USE_LOCAL_EMBEDDING = True
        mock_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_get_settings.return_value = mock_settings

        service = EmbeddingService()
        assert service.is_available() is True
