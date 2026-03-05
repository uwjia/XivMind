import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.embedding import (
    EmbeddingServiceInterface,
    LocalEmbeddingService,
    OpenAIEmbeddingService,
    EmbeddingServiceFactory,
    get_embedding_service,
    get_embedding_dimension,
)


class TestOpenAIEmbeddingService:
    def test_init(self):
        service = OpenAIEmbeddingService(
            api_key="test-key",
            model_name="text-embedding-ada-002"
        )
        assert service.api_key == "test-key"
        assert service.model_name == "text-embedding-ada-002"
        assert service.dimension == 1536

    def test_get_dimension(self):
        service = OpenAIEmbeddingService(api_key="test-key")
        assert service.get_dimension() == 1536

    def test_get_model_name(self):
        service = OpenAIEmbeddingService(
            api_key="test-key",
            model_name="text-embedding-3-small"
        )
        assert service.get_model_name() == "text-embedding-3-small"

    def test_encode_success(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response

        service = OpenAIEmbeddingService(api_key="test-key")
        service._client = mock_client
        
        embedding, model = service.encode("test text")

        assert embedding == [0.1, 0.2, 0.3]
        assert model == "text-embedding-ada-002"
        mock_client.embeddings.create.assert_called_once_with(
            input="test text",
            model="text-embedding-ada-002"
        )

    def test_encode_empty_text(self):
        service = OpenAIEmbeddingService(api_key="test-key")
        embedding, model = service.encode("")
        
        assert embedding == [0.0] * 1536
        assert model == "text-embedding-ada-002"

    def test_encode_batch_success(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        service = OpenAIEmbeddingService(api_key="test-key")
        service._client = mock_client
        
        embeddings, model = service.encode_batch(["text1", "text2"])

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    def test_encode_batch_empty(self):
        service = OpenAIEmbeddingService(api_key="test-key")
        embeddings, model = service.encode_batch([])
        assert embeddings == []
        assert model == "text-embedding-ada-002"

    def test_encode_error_returns_zeros(self):
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API Error")

        service = OpenAIEmbeddingService(api_key="test-key")
        service._client = mock_client
        
        embedding, model = service.encode("test text")
        
        assert embedding == [0.0] * 1536
        assert model == "text-embedding-ada-002"


class TestLocalEmbeddingService:
    def test_init(self):
        service = LocalEmbeddingService(model_name="all-MiniLM-L6-v2")
        assert service.model_name == "all-MiniLM-L6-v2"
        assert service.dimension == 384

    def test_get_dimension(self):
        service = LocalEmbeddingService()
        assert service.get_dimension() == 384

    def test_get_model_name(self):
        service = LocalEmbeddingService(model_name="test-model")
        assert service.get_model_name() == "test-model"

    def test_encode_success(self):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

        service = LocalEmbeddingService()
        service._model = mock_model
        
        embedding, model = service.encode("test text")

        assert embedding == [0.1, 0.2, 0.3]
        assert model == "all-MiniLM-L6-v2"
        mock_model.encode.assert_called_once()

    def test_encode_empty_text(self):
        service = LocalEmbeddingService()
        embedding, model = service.encode("")
        
        assert embedding == [0.0] * 384
        assert model == "all-MiniLM-L6-v2"

    def test_encode_batch_success(self):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])

        service = LocalEmbeddingService()
        service._model = mock_model
        
        embeddings, model = service.encode_batch(["text1", "text2"])

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    def test_encode_batch_empty(self):
        service = LocalEmbeddingService()
        embeddings, model = service.encode_batch([])
        assert embeddings == []
        assert model == "all-MiniLM-L6-v2"

    def test_encode_error_returns_zeros(self):
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Model error")

        service = LocalEmbeddingService()
        service._model = mock_model
        
        embedding, model = service.encode("test text")
        
        assert embedding == [0.0] * 384
        assert model == "all-MiniLM-L6-v2"

    def test_device_auto_cuda(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3080"
        mock_torch.backends.mps.is_available.return_value = False

        with patch.dict('sys.modules', {'torch': mock_torch}):
            service = LocalEmbeddingService(device="auto")
            device = service._get_device()
            
            assert device == "cuda"
            mock_torch.cuda.is_available.assert_called_once()

    def test_device_auto_mps(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True

        with patch.dict('sys.modules', {'torch': mock_torch}):
            service = LocalEmbeddingService(device="auto")
            device = service._get_device()
            
            assert device == "mps"

    def test_device_auto_cpu(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False

        with patch.dict('sys.modules', {'torch': mock_torch}):
            service = LocalEmbeddingService(device="auto")
            device = service._get_device()
            
            assert device == "cpu"

    def test_device_auto_no_torch(self):
        with patch.dict('sys.modules', {'torch': None}):
            service = LocalEmbeddingService(device="auto")
            device = service._get_device()
            
            assert device == "cpu"

    def test_device_explicit(self):
        service = LocalEmbeddingService(device="cuda")
        device = service._get_device()
        
        assert device == "cuda"

    def test_device_property(self):
        service = LocalEmbeddingService(device="cpu")
        assert service.device == "cpu"

    def test_get_device_method(self):
        service = LocalEmbeddingService(device="cpu")
        assert service.get_device() == "cpu"


class TestEmbeddingServiceFactory:
    def test_get_local_embedding_service(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.USE_LOCAL_EMBEDDING = True
            mock_settings.return_value.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            mock_settings.return_value.EMBEDDING_DEVICE = "cpu"
            
            EmbeddingServiceFactory.reset()
            service = EmbeddingServiceFactory.get_local_embedding_service()
            
            assert isinstance(service, LocalEmbeddingService)
            assert service.model_name == "all-MiniLM-L6-v2"

    def test_get_openai_embedding_service(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"
            mock_settings.return_value.OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
            mock_settings.return_value.OPENAI_BASE_URL = ""
            
            EmbeddingServiceFactory.reset()
            service = EmbeddingServiceFactory.get_openai_embedding_service()
            
            assert isinstance(service, OpenAIEmbeddingService)
            assert service.model_name == "text-embedding-ada-002"

    def test_get_embedding_service_local(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.USE_LOCAL_EMBEDDING = True
            mock_settings.return_value.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            mock_settings.return_value.EMBEDDING_DEVICE = "cpu"
            
            EmbeddingServiceFactory.reset()
            service = EmbeddingServiceFactory.get_embedding_service(provider="local")
            
            assert isinstance(service, LocalEmbeddingService)

    def test_get_embedding_service_openai(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"
            mock_settings.return_value.OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
            mock_settings.return_value.OPENAI_BASE_URL = ""
            
            EmbeddingServiceFactory.reset()
            service = EmbeddingServiceFactory.get_embedding_service(provider="openai")
            
            assert isinstance(service, OpenAIEmbeddingService)

    def test_get_embedding_service_unknown_provider(self):
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            EmbeddingServiceFactory.get_embedding_service(provider="unknown")

    def test_get_current_provider_local(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.USE_LOCAL_EMBEDDING = True
            
            provider = EmbeddingServiceFactory.get_current_provider()
            assert provider == "local"

    def test_get_current_provider_openai(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.USE_LOCAL_EMBEDDING = False
            
            provider = EmbeddingServiceFactory.get_current_provider()
            assert provider == "openai"

    def test_reset(self):
        EmbeddingServiceFactory._local_instance = Mock()
        EmbeddingServiceFactory._openai_instance = Mock()
        
        EmbeddingServiceFactory.reset()
        
        assert EmbeddingServiceFactory._local_instance is None
        assert EmbeddingServiceFactory._openai_instance is None


class TestConvenienceFunctions:
    def test_get_embedding_service(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.USE_LOCAL_EMBEDDING = True
            mock_settings.return_value.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            mock_settings.return_value.EMBEDDING_DEVICE = "cpu"
            
            EmbeddingServiceFactory.reset()
            service = get_embedding_service()
            
            assert isinstance(service, LocalEmbeddingService)

    def test_get_embedding_dimension(self):
        with patch('app.services.embedding.factory.get_settings') as mock_settings:
            mock_settings.return_value.EMBEDDING_DIM = 1024
            
            dim = get_embedding_dimension()
            assert dim == 1024
