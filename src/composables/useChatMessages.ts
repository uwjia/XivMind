import { ref, computed, nextTick, type Ref } from 'vue'
import { arxivBackendAPI } from '../services/arxivBackend'
import { useLLMStore } from '../stores/llm-store'
import { useConfigError } from './useConfigError'

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
  skillId?: string
  skillName?: string
  paperIds?: string[]
  skillParams?: Record<string, unknown>
}

export type ChatMode = 'search' | 'ask' | 'skills'

export function useChatMessages(mode: Ref<ChatMode>) {
  const llmStore = useLLMStore()
  const { isConfigError } = useConfigError()

  const searchMessages = ref<Message[]>([])
  const askMessages = ref<Message[]>([])
  const skillsMessages = ref<Message[]>([])
  const messageRefs = ref<Map<number, HTMLElement>>(new Map())
  const currentUserMessageIndex = ref<number | null>(null)
  const isLoading = ref(false)

  const currentModeMessages = computed({
    get: () => {
      switch (mode.value) {
        case 'search': return searchMessages.value
        case 'ask': return askMessages.value
        case 'skills': return skillsMessages.value
        default: return searchMessages.value
      }
    },
    set: (value: Message[]) => {
      switch (mode.value) {
        case 'search': searchMessages.value = value; break
        case 'ask': askMessages.value = value; break
        case 'skills': skillsMessages.value = value; break
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

  const sendMessage = async (messageContent: string, isRetry: boolean = false): Promise<void> => {
    const message = messageContent.trim()
    if (!message || isLoading.value) return

    const currentMode = mode.value
    const currentMessages = currentMode === 'search' ? searchMessages : 
                            currentMode === 'ask' ? askMessages : 
                            skillsMessages

    if (!isRetry) {
      currentMessages.value.push({ role: 'user', content: message })
    }
    currentUserMessageIndex.value = currentMessages.value.length - 1
    scrollToBottom()

    isLoading.value = true
    
    try {
      if (currentMode === 'search') {
        const result = await arxivBackendAPI.semanticSearch(message, 10)
        
        currentMessages.value.push({
          role: 'assistant',
          content: '',
          papers: result.papers.map((p) => ({
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
          llmStore.selectedProvider || undefined,
          llmStore.selectedModel || undefined
        )
        
        if (result.error) {
          const configError = isConfigError(result.error)
          currentMessages.value.push({
            role: 'assistant',
            content: `Error: ${result.error}`,
            isConfigError: configError
          })
        } else {
          currentMessages.value.push({
            role: 'assistant',
            content: '',
            answer: result.answer,
            references: result.references || [],
            model: result.model
          })
        }
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMsg = error instanceof Error ? error.message : 'Something went wrong'
      const configError = isConfigError(errorMsg)
      currentMessages.value.push({
        role: 'assistant',
        content: `Error: ${errorMsg}`,
        isConfigError: configError
      })
    } finally {
      isLoading.value = false
      scrollToBottom()
    }
  }

  const retryMessage = async (
    message: Message, 
    _skills: Array<{ id: string }>,
    onSkillRetry?: (skillId: string, paperIds: string[], params: Record<string, unknown>) => Promise<void>
  ): Promise<void> => {
    const messageIndex = currentModeMessages.value.findIndex(m => getMessageId(m) === getMessageId(message))
    if (messageIndex <= 0) return
    
    const userMessage = currentModeMessages.value[messageIndex - 1]
    if (userMessage.role !== 'user') return
    
    currentModeMessages.value = currentModeMessages.value.slice(0, messageIndex)
    
    if (userMessage.skillId && userMessage.paperIds && userMessage.skillParams && onSkillRetry) {
      await onSkillRetry(userMessage.skillId, userMessage.paperIds, userMessage.skillParams)
    } else {
      const originalInput = userMessage.content
      await sendMessage(originalInput, true)
    }
  }

  const clearMessages = () => {
    currentModeMessages.value = []
    currentUserMessageIndex.value = null
  }

  const addUserMessage = (content: string, options?: Partial<Message>) => {
    currentModeMessages.value.push({
      role: 'user',
      content,
      ...options
    })
    currentUserMessageIndex.value = currentModeMessages.value.length - 1
    scrollToBottom()
  }

  const addAssistantMessage = (content: string, options?: Partial<Message>) => {
    currentModeMessages.value.push({
      role: 'assistant',
      content,
      ...options
    })
    scrollToBottom()
  }

  return {
    searchMessages,
    askMessages,
    skillsMessages,
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
    addUserMessage,
    addAssistantMessage
  }
}
