interface LLMProviderInfo {
  id: string
  name: string
  models: string[]
  available: boolean
  description: string
}

interface LLMProvidersResponse {
  providers: LLMProviderInfo[]
  default_provider: string | null
}

interface OllamaStatusResponse {
  available: boolean
  error: string | null
  base_url: string
  default_model: string
  checked_model?: string
  available_models: string[]
}

const LLM_API_BASE = '/api/llm'

export const llmAPI = {
  async getProviders(): Promise<LLMProvidersResponse> {
    const response = await fetch(`${LLM_API_BASE}/providers`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getOllamaStatus(model?: string): Promise<OllamaStatusResponse> {
    const params = model ? `?model=${encodeURIComponent(model)}` : ''
    const response = await fetch(`${LLM_API_BASE}/ollama/status${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
}

export type { LLMProviderInfo, LLMProvidersResponse, OllamaStatusResponse }
