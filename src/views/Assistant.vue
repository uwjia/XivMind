<template>
  <div class="assistant-page">
    <div class="page-header">
      <h1>AI Assistant</h1>
      <p class="subtitle">Search papers or ask questions about research topics</p>
      <div class="header-controls">
        <div class="mode-switch">
          <button 
            :class="['mode-btn', { active: mode === 'search' }]" 
            @click="mode = 'search'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <span>Search</span>
          </button>
          <button 
            :class="['mode-btn', { active: mode === 'ask' }]" 
            @click="mode = 'ask'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span>Ask</span>
          </button>
        </div>
        
        <div v-if="mode === 'ask' && llmProviders.length > 0" class="llm-selector">
          <select v-model="selectedProvider" @change="onProviderChange" class="provider-select">
            <option v-for="provider in availableProviders" :key="provider.id" :value="provider.id">
              {{ provider.name }} {{ !provider.available ? '(Not configured)' : '' }}
            </option>
          </select>
          <select v-model="selectedModel" class="model-select">
            <option v-for="model in currentModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="mode === 'ask' && selectedProvider === 'ollama' && showStatusMessage && (ollamaStatus.loading || ollamaStatus.available || ollamaStatus.error)" class="ollama-status-row">
        <span v-if="ollamaStatus.loading" class="status-loading">
          <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
          </svg>
          Checking Ollama...
        </span>
        <span v-else-if="ollamaStatus.available" class="status-available">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          Ollama connected
        </span>
        <span v-else-if="ollamaStatus.error" class="status-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ ollamaStatus.error }}
        </span>
      </div>
    </div>

    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg v-if="mode === 'search'" viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"/>
            </svg>
          </div>
          <h3>{{ mode === 'search' ? 'Search Papers' : 'Ask Questions' }}</h3>
          <p v-if="mode === 'search'">Enter a natural language query to find relevant papers using semantic search.</p>
          <p v-else>Ask questions about research topics and get AI-powered answers with paper references.</p>
          <div class="suggestions">
            <button v-for="suggestion in currentSuggestions" :key="suggestion" class="suggestion-btn" @click="sendSuggestion(suggestion)">
              {{ suggestion }}
            </button>
          </div>
        </div>

        <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
          <div class="message-avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <div class="message-content">
            <div v-if="message.papers && message.papers.length > 0" class="papers-result">
              <div class="result-header">
                Found {{ message.papers.length }} papers
                <span v-if="message.model" class="model-badge">{{ message.model }}</span>
              </div>
              <div class="paper-cards">
                <div v-for="paper in message.papers" :key="paper.id" class="paper-card" @click="$emit('viewPaper', paper.id)">
                  <div class="paper-header">
                    <h4 class="paper-title">{{ paper.title }}</h4>
                    <span class="similarity-score">{{ (paper.similarity_score * 100).toFixed(1) }}%</span>
                  </div>
                  <p class="paper-authors">{{ paper.authors?.slice(0, 3).join(', ') }}{{ paper.authors?.length > 3 ? ' et al.' : '' }}</p>
                  <p class="paper-abstract">{{ paper.abstract?.substring(0, 200) }}{{ paper.abstract?.length > 200 ? '...' : '' }}</p>
                  <div class="paper-meta">
                    <span class="paper-category">{{ paper.primary_category }}</span>
                    <span class="paper-date">{{ paper.published?.substring(0, 10) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="message.answer" class="answer-result">
              <div class="answer-text" v-html="formatMessage(message.answer)"></div>
              <div v-if="message.references && message.references.length > 0" class="references">
                <h5>📚 References</h5>
                <div v-for="ref in message.references" :key="ref.id" class="reference-item" @click="$emit('viewPaper', ref.id)">
                  <span class="ref-title">{{ ref.title }}</span>
                  <span class="ref-authors">{{ ref.authors?.slice(0, 2).join(', ') }}</span>
                  <span class="ref-score">{{ (ref.relevance_score * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
            <div v-else class="message-text" v-html="formatMessage(message.content)"></div>
          </div>
        </div>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <textarea
          v-model="inputMessage"
          @keydown.enter.exact.prevent="sendMessage"
          :placeholder="mode === 'search' ? 'Enter your search query...' : 'Ask a question about research...'"
          rows="1"
          ref="inputRef"
        ></textarea>
        <button @click="sendMessage" :disabled="!inputMessage.trim() || isLoading" class="send-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { arxivBackendAPI } from '../services/arxivBackend'

interface Paper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  similarity_score: number
}

interface Reference {
  id: string
  title: string
  authors: string[]
  published?: string
  relevance_score: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  papers?: Paper[]
  answer?: string
  references?: Reference[]
  model?: string
}

interface LLMProvider {
  id: string
  name: string
  models: string[]
  available: boolean
  description: string
}

interface OllamaStatus {
  loading: boolean
  available: boolean
  error: string | null
  models: string[]
}

const mode = ref<'search' | 'ask'>('search')
const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

const llmProviders = ref<LLMProvider[]>([])
const selectedProvider = ref<string>('')
const selectedModel = ref<string>('')
const isUpdatingModel = ref(false)
const showStatusMessage = ref(true)
let statusTimeout: ReturnType<typeof setTimeout> | null = null
const ollamaStatus = ref<OllamaStatus>({
  loading: false,
  available: false,
  error: null,
  models: []
})

const availableProviders = computed(() => {
  return llmProviders.value
})

const currentModels = computed(() => {
  if (selectedProvider.value === 'ollama' && ollamaStatus.value.models.length > 0) {
    return ollamaStatus.value.models
  }
  const provider = llmProviders.value.find(p => p.id === selectedProvider.value)
  return provider?.models || []
})

const onProviderChange = async () => {
  const provider = llmProviders.value.find(p => p.id === selectedProvider.value)
  
  if (selectedProvider.value === 'ollama') {
    await checkOllamaStatus()
  } else if (provider && provider.models.length > 0) {
    selectedModel.value = provider.models[0]
  }
}

const checkOllamaStatus = async () => {
  if (isUpdatingModel.value) return
  
  if (statusTimeout) {
    clearTimeout(statusTimeout)
    statusTimeout = null
  }
  
  showStatusMessage.value = true
  ollamaStatus.value = {
    loading: true,
    available: false,
    error: null,
    models: []
  }
  
  try {
    const result = await arxivBackendAPI.getOllamaStatus(selectedModel.value || undefined)
    const availableModels = result.available_models || []
    
    if (result.available) {
      ollamaStatus.value = {
        loading: false,
        available: true,
        error: null,
        models: availableModels
      }
      
      if (availableModels.length > 0 && !availableModels.includes(selectedModel.value)) {
        isUpdatingModel.value = true
        selectedModel.value = availableModels[0]
        nextTick(() => {
          isUpdatingModel.value = false
        })
      }
    } else {
      ollamaStatus.value = {
        loading: false,
        available: false,
        error: result.error,
        models: availableModels
      }
      
      if (availableModels.length > 0) {
        isUpdatingModel.value = true
        selectedModel.value = availableModels[0]
        nextTick(() => {
          isUpdatingModel.value = false
        })
      }
    }
    
    statusTimeout = setTimeout(() => {
      showStatusMessage.value = false
    }, 5000)
    
  } catch (error) {
    ollamaStatus.value = {
      loading: false,
      available: false,
      error: error instanceof Error ? error.message : 'Failed to check Ollama status',
      models: []
    }
    
    statusTimeout = setTimeout(() => {
      showStatusMessage.value = false
    }, 5000)
  }
}

const loadLLMProviders = async () => {
  try {
    const result = await arxivBackendAPI.getLLMProviders()
    llmProviders.value = result.providers || []
    
    if (result.default_provider) {
      selectedProvider.value = result.default_provider
    } else if (llmProviders.value.length > 0) {
      const firstAvailable = llmProviders.value.find(p => p.available)
      if (firstAvailable) {
        selectedProvider.value = firstAvailable.id
      }
    }
    
    if (selectedProvider.value) {
      onProviderChange()
    }
  } catch (error) {
    console.error('Failed to load LLM providers:', error)
  }
}

watch(mode, (newMode) => {
  if (newMode === 'ask' && llmProviders.value.length === 0) {
    loadLLMProviders()
  }
})

watch(selectedProvider, (newProvider) => {
  if (newProvider === 'ollama') {
    checkOllamaStatus()
  }
})

watch(selectedModel, () => {
  if (selectedProvider.value === 'ollama' && !ollamaStatus.value.loading && !isUpdatingModel.value) {
    checkOllamaStatus()
  }
})

const searchSuggestions = [
  'transformer attention mechanisms',
  'large language model training',
  'graph neural networks',
  'diffusion models for image generation'
]

const askSuggestions = [
  'What are the key innovations in transformer architecture?',
  'Explain the difference between BERT and GPT',
  'What is retrieval-augmented generation?',
  'How do diffusion models work?'
]

const currentSuggestions = computed(() => {
  return mode.value === 'search' ? searchSuggestions : askSuggestions
})

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  messages.value.push({ role: 'user', content: message })
  inputMessage.value = ''
  scrollToBottom()

  isLoading.value = true
  
  try {
    if (mode.value === 'search') {
      const result = await arxivBackendAPI.semanticSearch(message, 10)
      
      messages.value.push({
        role: 'assistant',
        content: '',
        papers: result.papers.map((p: any) => ({
          id: p.id,
          title: p.title,
          abstract: p.abstract,
          authors: p.authors || [],
          primary_category: p.primary_category || '',
          categories: p.categories || [],
          published: p.published || '',
          similarity_score: p.similarity_score || 0
        })),
        model: result.model
      })
    } else {
      const result = await arxivBackendAPI.askQuestion(
        message, 
        5, 
        selectedProvider.value || undefined,
        selectedModel.value || undefined
      )
      
      messages.value.push({
        role: 'assistant',
        content: '',
        answer: result.answer,
        references: result.references || [],
        model: result.model
      })
    }
  } catch (error) {
    console.error('Error:', error)
    messages.value.push({
      role: 'assistant',
      content: `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const sendSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
  sendMessage()
}

onMounted(() => {
  inputRef.value?.focus()
  if (mode.value === 'ask') {
    loadLLMProviders()
  }
})

onUnmounted(() => {
  if (statusTimeout) {
    clearTimeout(statusTimeout)
    statusTimeout = null
  }
})
</script>

<style scoped>
.assistant-page {
  padding: 88px 24px 24px 24px;
  max-width: 900px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.mode-switch {
  display: flex;
  gap: 8px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.llm-selector {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ollama-status-row {
  margin-top: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
  font-size: 0.85rem;
}

.ollama-status-row svg {
  flex-shrink: 0;
}

.status-loading {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-loading .spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-available {
  color: #10B981;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-error {
  color: #EF4444;
  display: flex;
  align-items: center;
  gap: 6px;
}

.provider-select,
.model-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
}

.provider-select:hover,
.model-select:hover {
  border-color: #10B981;
}

.provider-select:focus,
.model-select:focus {
  border-color: #10B981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn svg {
  width: 18px;
  height: 18px;
}

.mode-btn:hover {
  border-color: #10B981;
  color: #10B981;
}

.mode-btn.active {
  background: #10B981;
  border-color: #10B981;
  color: white;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-state p {
  max-width: 400px;
  margin: 0 0 24px 0;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
}

.suggestion-btn {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  border-color: #10B981;
  color: #10B981;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--accent-color);
  color: white;
}

.message.assistant .message-avatar {
  background: rgba(16, 185, 129, 0.1);
}

.message-avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  max-width: 80%;
}

.message.user .message-content {
  display: flex;
  justify-content: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.5;
}

.message.user .message-text {
  background: var(--accent-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.papers-result {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  border-bottom-left-radius: 4px;
}

.result-header {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.paper-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.paper-card:hover {
  border-color: #10B981;
  transform: translateY(-2px);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.paper-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.similarity-score {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.paper-authors {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.paper-abstract {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.paper-meta {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
}

.paper-category {
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.paper-date {
  color: var(--text-muted);
}

.answer-result {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  border-bottom-left-radius: 4px;
}

.answer-text {
  line-height: 1.6;
  color: var(--text-primary);
}

.references {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.references h5 {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.reference-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reference-item:hover {
  background: var(--bg-tertiary);
}

.ref-title {
  flex: 1;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.ref-authors {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.ref-score {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #10B981;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.95rem;
  resize: none;
  outline: none;
  font-family: inherit;
}

.input-area textarea:focus {
  border-color: #10B981;
}

.input-area textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: #10B981;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  background: #059669;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .assistant-page {
    padding: 80px 16px 16px 16px;
  }

  .message-content {
    max-width: 90%;
  }

  .suggestions {
    flex-direction: column;
  }

  .suggestion-btn {
    text-align: left;
  }

  .header-controls {
    flex-wrap: wrap;
  }

  .llm-selector {
    flex-wrap: wrap;
  }

  .provider-select,
  .model-select {
    flex: 1;
    min-width: 120px;
  }
}
</style>
