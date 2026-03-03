import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { conversationService } from '@/services/conversation'
import type { ConversationMeta, ConversationUpdate, ConversationMessage } from '@/types/conversation'

export type ChatMode = 'search' | 'ask'

export const useConversationStore = defineStore('conversation', () => {
  const currentSessionId = ref<string>('')
  const conversations = ref<ConversationMeta[]>([])
  const currentMessages = ref<ConversationMessage[]>([])
  const showHistoryPanel = ref(false)
  const loading = ref(false)
  const mode = ref<ChatMode>('search')
  const lastConversationByMode = ref<Record<ChatMode, string>>({
    search: '',
    ask: '',
  })

  const currentConversation = computed(() => 
    conversations.value.find(c => c.session_id === currentSessionId.value)
  )

  async function init() {
    await loadConversations()
    if (!currentSessionId.value && conversations.value.length > 0) {
      await switchConversation(conversations.value[0].session_id)
    }
    if (currentConversation.value?.mode) {
      mode.value = currentConversation.value.mode as ChatMode
    }
  }

  async function loadConversations() {
    loading.value = true
    try {
      conversations.value = await conversationService.getConversations()
    } finally {
      loading.value = false
    }
  }

  async function createNewConversation(newMode?: ChatMode): Promise<ConversationMeta> {
    const conversationMode = newMode || mode.value
    const conversation = await conversationService.createConversation({ mode: conversationMode })
    conversations.value.unshift(conversation)
    currentSessionId.value = conversation.session_id
    currentMessages.value = []
    lastConversationByMode.value[conversationMode] = conversation.session_id
    return conversation
  }

  async function switchConversation(sessionId: string) {
    currentSessionId.value = sessionId
    
    try {
      const data = await conversationService.getConversationMessages(sessionId)
      currentMessages.value = data.messages || []
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
      currentMessages.value = []
    }
    
    if (currentConversation.value?.mode) {
      const conversationMode = currentConversation.value.mode as ChatMode
      mode.value = conversationMode
      lastConversationByMode.value[conversationMode] = sessionId
    }
  }

  async function switchMode(newMode: ChatMode) {
    if (currentConversation.value && currentConversation.value.mode === newMode) {
      return
    }
    
    const lastSessionId = lastConversationByMode.value[newMode]
    if (lastSessionId && conversations.value.find(c => c.session_id === lastSessionId)) {
      await switchConversation(lastSessionId)
      return
    }
    
    const modeConversations = conversations.value
      .filter(c => c.mode === newMode)
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    
    if (modeConversations.length > 0) {
      await switchConversation(modeConversations[0].session_id)
    } else {
      const latestConversation = await conversationService.getLatestConversationByMode(newMode)
      
      if (latestConversation) {
        await switchConversation(latestConversation.session_id)
      } else {
        currentSessionId.value = ''
        currentMessages.value = []
      }
    }
    
    mode.value = newMode
  }

  async function ensureConversationForMode(): Promise<string | undefined> {
    if (currentConversation.value && currentConversation.value.mode === mode.value) {
      return currentSessionId.value
    }
    
    const conversation = await createNewConversation()
    return conversation.session_id
  }

  async function addMessage(message: ConversationMessage) {
    currentMessages.value.push(message)
    
    try {
      await conversationService.addMessage(currentSessionId.value, message)
      
      const conversation = conversations.value.find(c => c.session_id === currentSessionId.value)
      const previousCount = conversation?.message_count || 0
      if (conversation) {
        conversation.message_count += 1
      }
      
      if (previousCount === 0 && message.role === 'user') {
        const newTitle = message.content.substring(0, 50) + (message.content.length > 50 ? '...' : '')
        await updateConversation(currentSessionId.value, { title: newTitle })
      }
    } catch (error) {
      console.error('Failed to save message:', error)
    }
  }

  async function updateConversation(sessionId: string, update: ConversationUpdate) {
    const updated = await conversationService.updateConversation(sessionId, update)
    const index = conversations.value.findIndex(c => c.session_id === sessionId)
    if (index !== -1) {
      conversations.value[index] = updated
    }
  }

  async function deleteConversation(sessionId: string) {
    await conversationService.deleteConversation(sessionId)
    conversations.value = conversations.value.filter(c => c.session_id !== sessionId)
    if (currentSessionId.value === sessionId) {
      if (conversations.value.length > 0) {
        await switchConversation(conversations.value[0].session_id)
      } else {
        currentSessionId.value = ''
        currentMessages.value = []
      }
    }
  }

  async function searchConversations(query: string) {
    loading.value = true
    try {
      conversations.value = await conversationService.searchConversations(query)
    } finally {
      loading.value = false
    }
  }

  return {
    currentSessionId,
    conversations,
    currentMessages,
    showHistoryPanel,
    loading,
    currentConversation,
    mode,
    lastConversationByMode,
    init,
    loadConversations,
    createNewConversation,
    switchConversation,
    switchMode,
    ensureConversationForMode,
    addMessage,
    updateConversation,
    deleteConversation,
    searchConversations,
  }
})
