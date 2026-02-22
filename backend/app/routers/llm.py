from fastapi import APIRouter, Query
from typing import Optional

from app.services.llm_service import llm_service
from app.models import LLMProvidersResponse, LLMProviderInfo

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/providers", response_model=LLMProvidersResponse)
async def get_llm_providers():
    """
    Get available LLM providers.
    
    Returns list of supported LLM providers with their availability status,
    supported models, and descriptions.
    """
    providers = llm_service.get_providers()
    
    default_provider = None
    if llm_service.is_available(llm_service.settings.LLM_PROVIDER):
        default_provider = llm_service.settings.LLM_PROVIDER
    else:
        for p in providers:
            if p.get("available"):
                default_provider = p.get("id")
                break
    
    return LLMProvidersResponse(
        providers=[LLMProviderInfo(**p) for p in providers],
        default_provider=default_provider,
    )


@router.get("/ollama/status")
async def get_ollama_status(
    model: Optional[str] = Query(None, description="Model to check availability for")
):
    """
    Check Ollama service status and available models.
    
    Returns detailed status information about the Ollama service.
    If model is provided, checks if that specific model is available.
    """
    from app.services.llm_service import OllamaProvider
    
    check_model = model or llm_service.settings.OLLAMA_MODEL or "llama3"
    
    provider = OllamaProvider(
        base_url=llm_service.settings.OLLAMA_BASE_URL,
        model=check_model,
    )
    
    available, error = await provider.check_available()
    
    try:
        models = await provider._get_available_models()
    except Exception:
        models = []
    
    return {
        "available": available,
        "error": error if not available else None,
        "base_url": llm_service.settings.OLLAMA_BASE_URL,
        "default_model": llm_service.settings.OLLAMA_MODEL or "llama3",
        "checked_model": check_model,
        "available_models": models,
    }
