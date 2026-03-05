import pytest
import sys
from unittest.mock import patch, AsyncMock, MagicMock

sys.modules["pymilvus"] = MagicMock()
sys.modules["pymilvus.connections"] = MagicMock()
sys.modules["pymilvus.Collection"] = MagicMock()
sys.modules["pymilvus.utility"] = MagicMock()
sys.modules["pymilvus.DataType"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.llm import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_llm_service():
    with patch('app.routers.llm.llm_service') as mock:
        yield mock


@pytest.fixture
def sample_providers():
    return [
        {
            "id": "openai",
            "name": "OpenAI",
            "models": ["gpt-4o-mini", "gpt-4o"],
            "available": True,
            "description": "OpenAI GPT models",
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
            "available": False,
            "description": "Anthropic Claude models",
        },
        {
            "id": "ollama",
            "name": "Ollama",
            "models": ["llama3", "mistral"],
            "available": True,
            "description": "Local Ollama models",
        },
    ]


class TestGetLLMProviders:
    def test_get_providers_success(self, client, mock_llm_service, sample_providers):
        mock_llm_service.get_providers.return_value = sample_providers
        mock_llm_service.is_available.return_value = True
        mock_llm_service.settings.LLM_PROVIDER = "openai"
        
        response = client.get("/llm/providers")
        
        assert response.status_code == 200
        assert "providers" in response.json()
        assert "default_provider" in response.json()
        assert response.json()["default_provider"] == "openai"
        assert len(response.json()["providers"]) == 3
    
    def test_get_providers_with_fallback_default(self, client, mock_llm_service, sample_providers):
        mock_llm_service.get_providers.return_value = sample_providers
        mock_llm_service.is_available.return_value = False
        mock_llm_service.settings.LLM_PROVIDER = "anthropic"
        
        response = client.get("/llm/providers")
        
        assert response.status_code == 200
        assert response.json()["default_provider"] == "openai"
    
    def test_get_providers_empty(self, client, mock_llm_service):
        mock_llm_service.get_providers.return_value = []
        mock_llm_service.is_available.return_value = False
        
        response = client.get("/llm/providers")
        
        assert response.status_code == 200
        assert response.json()["providers"] == []
        assert response.json()["default_provider"] is None
    
    def test_get_providers_structure(self, client, mock_llm_service, sample_providers):
        mock_llm_service.get_providers.return_value = sample_providers
        mock_llm_service.is_available.return_value = True
        mock_llm_service.settings.LLM_PROVIDER = "openai"
        
        response = client.get("/llm/providers")
        
        for provider in response.json()["providers"]:
            assert "id" in provider
            assert "name" in provider
            assert "models" in provider
            assert "available" in provider
            assert "description" in provider


class TestGetOllamaStatus:
    def test_ollama_status_available(self, client, mock_llm_service):
        mock_llm_service.settings.OLLAMA_MODEL = "llama3"
        mock_llm_service.settings.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_provider = AsyncMock()
        mock_provider.check_available = AsyncMock(return_value=(True, None))
        mock_provider._get_available_models = AsyncMock(return_value=["llama3", "mistral"])
        
        with patch('app.services.llm_service.OllamaProvider', return_value=mock_provider):
            response = client.get("/llm/ollama/status")
        
        assert response.status_code == 200
        assert response.json()["available"] is True
        assert response.json()["error"] is None
        assert "llama3" in response.json()["available_models"]
    
    def test_ollama_status_unavailable(self, client, mock_llm_service):
        mock_llm_service.settings.OLLAMA_MODEL = "llama3"
        mock_llm_service.settings.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_provider = AsyncMock()
        mock_provider.check_available = AsyncMock(return_value=(False, "Connection refused"))
        mock_provider._get_available_models = AsyncMock(return_value=[])
        
        with patch('app.services.llm_service.OllamaProvider', return_value=mock_provider):
            response = client.get("/llm/ollama/status")
        
        assert response.status_code == 200
        assert response.json()["available"] is False
        assert "connection" in response.json()["error"].lower()
    
    def test_ollama_status_with_model_param(self, client, mock_llm_service):
        mock_llm_service.settings.OLLAMA_MODEL = "llama3"
        mock_llm_service.settings.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_provider = AsyncMock()
        mock_provider.check_available = AsyncMock(return_value=(True, None))
        mock_provider._get_available_models = AsyncMock(return_value=["mistral"])
        
        with patch('app.services.llm_service.OllamaProvider', return_value=mock_provider) as mock_class:
            response = client.get("/llm/ollama/status?model=mistral")
            
            mock_class.assert_called_once()
            call_kwargs = mock_class.call_args[1]
            assert call_kwargs["model"] == "mistral"
        
        assert response.status_code == 200
    
    def test_ollama_status_default_model(self, client, mock_llm_service):
        mock_llm_service.settings.OLLAMA_MODEL = "llama3"
        mock_llm_service.settings.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_provider = AsyncMock()
        mock_provider.check_available = AsyncMock(return_value=(True, None))
        mock_provider._get_available_models = AsyncMock(return_value=[])
        
        with patch('app.services.llm_service.OllamaProvider', return_value=mock_provider):
            response = client.get("/llm/ollama/status")
        
        assert response.status_code == 200
        assert response.json()["default_model"] == "llama3"
    
    def test_ollama_status_models_error(self, client, mock_llm_service):
        mock_llm_service.settings.OLLAMA_MODEL = "llama3"
        mock_llm_service.settings.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_provider = AsyncMock()
        mock_provider.check_available = AsyncMock(return_value=(True, None))
        mock_provider._get_available_models = AsyncMock(side_effect=Exception("API error"))
        
        with patch('app.services.llm_service.OllamaProvider', return_value=mock_provider):
            response = client.get("/llm/ollama/status")
        
        assert response.status_code == 200
        assert response.json()["available_models"] == []
