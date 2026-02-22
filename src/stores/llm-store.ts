import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { llmAPI } from '../services/llm'
import type { LLMProviderInfo } from '../services/llm'

interface OllamaStatus {
  loading: boolean
  available: boolean
  error: string | null
  models: string[]
}

export const useLLMStore = defineStore('llm', () => {
  const providers = ref<LLMProviderInfo[]>([])
  const selectedProvider = ref<string>('')
  const selectedModel = ref<string>('')
  const isLoading = ref(false)
  const ollamaStatus = ref<OllamaStatus>({
    loading: false,
    available: false,
    error: null,
    models: []
  })

  const availableProviders = computed(() => providers.value)
  
  const currentModels = computed(() => {
    if (selectedProvider.value === 'ollama' && ollamaStatus.value.models.length > 0) {
      return ollamaStatus.value.models
    }
    const provider = providers.value.find(p => p.id === selectedProvider.value)
    return provider?.models || []
  })

  const currentProvider = computed(() => {
    return providers.value.find(p => p.id === selectedProvider.value)
  })

  const loadProviders = async () => {
    isLoading.value = true
    try {
      const result = await llmAPI.getProviders()
      providers.value = result.providers || []
      
      const savedProvider = localStorage.getItem('llm_provider')
      const savedModel = localStorage.getItem('llm_model')
      
      if (savedProvider && providers.value.some(p => p.id === savedProvider)) {
        selectedProvider.value = savedProvider
      } else if (result.default_provider) {
        selectedProvider.value = result.default_provider
      } else if (providers.value.length > 0) {
        const firstAvailable = providers.value.find(p => p.available)
        if (firstAvailable) {
          selectedProvider.value = firstAvailable.id
        }
      }
      
      if (savedModel) {
        selectedModel.value = savedModel
      } else {
        const provider = providers.value.find(p => p.id === selectedProvider.value)
        if (provider && provider.models.length > 0) {
          selectedModel.value = provider.models[0]
        }
      }
      
      if (selectedProvider.value === 'ollama') {
        await checkOllamaStatus()
      }
    } catch (error) {
      console.error('Failed to load LLM providers:', error)
    } finally {
      isLoading.value = false
    }
  }

  const checkOllamaStatus = async (model?: string) => {
    ollamaStatus.value = {
      loading: true,
      available: false,
      error: null,
      models: []
    }
    
    try {
      const result = await llmAPI.getOllamaStatus(model || selectedModel.value || undefined)
      const availableModels = result.available_models || []
      
      ollamaStatus.value = {
        loading: false,
        available: result.available,
        error: result.available ? null : result.error,
        models: availableModels
      }
      
      if (availableModels.length > 0 && !availableModels.includes(selectedModel.value)) {
        selectedModel.value = availableModels[0]
      }
    } catch (error) {
      ollamaStatus.value = {
        loading: false,
        available: false,
        error: error instanceof Error ? error.message : 'Failed to check Ollama status',
        models: []
      }
    }
  }

  const setProvider = (providerId: string) => {
    selectedProvider.value = providerId
    localStorage.setItem('llm_provider', providerId)
    
    const provider = providers.value.find(p => p.id === providerId)
    if (provider && provider.models.length > 0) {
      selectedModel.value = provider.models[0]
      localStorage.setItem('llm_model', provider.models[0])
    }
    
    if (providerId === 'ollama') {
      checkOllamaStatus()
    }
  }

  const setModel = (model: string) => {
    selectedModel.value = model
    localStorage.setItem('llm_model', model)
    
    if (selectedProvider.value === 'ollama') {
      checkOllamaStatus(model)
    }
  }

  const init = async () => {
    await loadProviders()
  }

  return {
    providers,
    selectedProvider,
    selectedModel,
    isLoading,
    ollamaStatus,
    availableProviders,
    currentModels,
    currentProvider,
    loadProviders,
    checkOllamaStatus,
    setProvider,
    setModel,
    init
  }
})
