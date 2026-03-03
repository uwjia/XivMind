import { ref, computed, nextTick, type Ref } from 'vue'
import { arxivBackendAPI } from '@/services/arxivBackend'
import { useLLMStore } from '@/stores/llm-store'
import { useMemoryStore } from '@/stores/memory-store'
import { useConversationStore } from '@/stores/conversation-store'
import { useConfigError } from '@/composables/useConfigError'
import { memoryService } from '@/services/memory'
import type { ConversationMessage } from '@/types/conversation'

export interface Paper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  similarity_score: number
}

export interface Reference {
  id: string
  title: string
  authors: string[]
  published?: string
  relevance_score: number
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  papers?: Paper[]
  answer?: string
  references?: Reference[]
  model?: string
  isConfigError?: boolean
  memoryUsed?: boolean
  relevantMemoriesCount?: number
}

export type ChatMode = 'search' | 'ask'

export function useChatMessages(mode: Ref<ChatMode>) {
  const llmStore = useLLMStore()
  const memoryStore = useMemoryStore()
  const conversationStore = useConversationStore()
  const { isConfigError } = useConfigError()

  const searchMessages = ref<Message[]>([])
  const askMessages = ref<Message[]>([])
  const messageRefs = ref<Map<number, HTMLElement>>(new Map())
  const currentUserMessageIndex = ref<number | null>(null)
  const isLoading = ref(false)

  const currentModeMessages = computed({
    get: () => {
      return mode.value === 'search' ? searchMessages.value : askMessages.value
    },
    set: (value: Message[]) => {
      if (mode.value === 'search') {
        searchMessages.value = value
      } else {
        askMessages.value = value
      }
    }
  })

  const setMessageRef = (el: unknown, index: number) => {
    if (el) {
      messageRefs.value.set(index, el as HTMLElement)
    }
  }

  const getMessageId = (message: Message): string => {
    return `${message.role}-${message.content.substring(0, 50)}-${message.papers?.length || 0}-${message.answer?.substring(0, 50) || ''}`
  }

  const scrollToBottom = () => {
    nextTick(() => {
      const container = document.querySelector('.messages')
      if (container) {
        if (currentUserMessageIndex.value !== null) {
          const userMessageEl = messageRefs.value.get(currentUserMessageIndex.value)
          if (userMessageEl) {
            userMessageEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
            return
          }
        }
        container.scrollTop = container.scrollHeight
      }
    })
  }

  const executeSearch = async (query: string): Promise<Message> => {
    const result = await arxivBackendAPI.semanticSearch(query, 10)
    
    if (result.error) {
      return {
        role: 'assistant' as const,
        content: `Error: ${result.error}`,
        isConfigError: isConfigError(result.error)
      }
    }
    
    const papers = result.papers.map((p) => ({
      id: p.id,
      title: p.title,
      abstract: p.abstract,
      authors: p.authors || [],
      primary_category: p.primary_category || '',
      categories: p.categories || [],
      published: p.published || '',
      similarity_score: p.similarity_score || 0
    }))
    
    return {
      role: 'assistant' as const,
      content: papers.length > 0 ? `Found ${papers.length} papers for "${query}"` : `No papers found for "${query}"`,
      papers: papers,
      model: result.model
    }
  }

  const executeAsk = async (query: string): Promise<Message> => {
    const useMemory = localStorage.getItem('use_memory') !== 'false'
    
    const result = await arxivBackendAPI.askQuestionWithMemory(
      query, 
      5, 
      useMemory,
      llmStore.selectedProvider || undefined,
      llmStore.selectedModel || undefined
    )
    
    if (result.error) {
      return {
        role: 'assistant' as const,
        content: `Error: ${result.error}`,
        isConfigError: isConfigError(result.error)
      }
    }
    
    return {
      role: 'assistant' as const,
      content: result.answer || '',
      answer: result.answer,
      references: result.references || [],
      model: result.model,
      memoryUsed: result.memory_used,
      relevantMemoriesCount: result.relevant_memories_count
    }
  }

  const handleRequestError = (error: unknown): Message => {
    console.error('Error:', error)
    const errorMsg = error instanceof Error ? error.message : 'Something went wrong'
    return {
      role: 'assistant' as const,
      content: `Error: ${errorMsg}`,
      isConfigError: isConfigError(errorMsg)
    }
  }

  const sendMessage = async (messageContent: string): Promise<void> => {
    const message = messageContent.trim()
    if (!message || isLoading.value) return

    if (!conversationStore.currentSessionId) {
      await conversationStore.ensureConversationForMode()
    }

    await addUserMessage(message)

    isLoading.value = true
    
    try {
      const assistantMsg = mode.value === 'search' 
        ? await executeSearch(message)
        : await executeAsk(message)
      
      await addAssistantMessage(assistantMsg.content, assistantMsg)
      
      if (!assistantMsg.isConfigError) {
        const assistantContent = assistantMsg.answer || assistantMsg.content || 
          (assistantMsg.papers ? `Found ${assistantMsg.papers.length} papers` : '')
        if (assistantContent) {
          recordConversationToMemory(message, assistantContent)
        }
      }
    } catch (error) {
      const errorMsg = handleRequestError(error)
      await addAssistantMessage(errorMsg.content, errorMsg)
    } finally {
      isLoading.value = false
      scrollToBottom()
    }
  }

  const retryMessage = async (messageIndex: number): Promise<void> => {
    if (messageIndex < 0 || messageIndex >= currentModeMessages.value.length) return
    
    const message = currentModeMessages.value[messageIndex]
    if (message.role !== 'assistant') return
    
    if (messageIndex === 0) return
    
    const userMessage = currentModeMessages.value[messageIndex - 1]
    if (userMessage.role !== 'user') return
    
    await sendMessage(userMessage.content)
  }

  const clearMessages = () => {
    searchMessages.value = []
    askMessages.value = []
    currentUserMessageIndex.value = null
  }

  const setMessages = (messages: Message[]) => {
    clearMessages()
    currentModeMessages.value = messages
  }

  const recordConversationToMemory = async (userMessage: string, assistantResponse: string) => {
    try {
      const sessionId = conversationStore.currentSessionId || `chat-${Date.now()}`
      const extractProfile = localStorage.getItem('extract_profile') === 'true'
      
      const result = await memoryService.processConversation({
        session_id: sessionId,
        user_message: userMessage,
        assistant_message: assistantResponse,
        extract: extractProfile,
      })
      
      if (result.status === 'processing') {
        setTimeout(async () => {
          await memoryStore.fetchStats()
          if (extractProfile) {
            await memoryStore.fetchCoreMemory()
          }
        }, 5000)
      }
    } catch (error) {
      console.warn('Failed to record conversation to memory:', error)
    }
  }

  const addUserMessage = async (content: string, options?: Partial<Message>) => {
    if (!conversationStore.currentSessionId) {
      await conversationStore.ensureConversationForMode()
    }
    
    currentModeMessages.value.push({
      role: 'user',
      content,
      ...options
    })
    currentUserMessageIndex.value = currentModeMessages.value.length - 1
    scrollToBottom()
    
    if (conversationStore.currentSessionId) {
      const message: ConversationMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: content,
        timestamp: new Date().toISOString(),
      }
      await conversationStore.addMessage(message)
    }
  }

  const addAssistantMessage = async (content: string, options?: Partial<Message>) => {
    if (!conversationStore.currentSessionId) {
      await conversationStore.ensureConversationForMode()
    }
    
    currentModeMessages.value.push({
      role: 'assistant',
      content,
      ...options
    })
    // currentUserMessageIndex.value = currentModeMessages.value.length - 1
    // scrollToBottom()
    
    if (conversationStore.currentSessionId) {
      const message: ConversationMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: content,
        timestamp: new Date().toISOString(),
        papers: options?.papers,
        answer: options?.answer,
        references: options?.references,
      }
      await conversationStore.addMessage(message)
    }
  }

  const saveToKnowledge = async (message: Message) => {
    const content = message.answer || message.content || ''
    if (!content) return
    
    const title = content.slice(0, 50) + (content.length > 50 ? '...' : '')
    
    try {
      await memoryStore.createArchivalMemory({
        content_type: 'insight',
        title: title,
        content: content,
        source_papers: message.references?.map(r => r.id) || [],
        tags: [],
      })
    } catch (error) {
      console.error('Failed to save to knowledge base:', error)
    }
  }

  return {
    searchMessages,
    askMessages,
    currentModeMessages,
    messageRefs,
    currentUserMessageIndex,
    isLoading,
    setMessageRef,
    getMessageId,
    scrollToBottom,
    sendMessage,
    retryMessage,
    clearMessages,
    setMessages,
    addUserMessage,
    addAssistantMessage,
    recordConversationToMemory,
    saveToKnowledge,
  }
}
