<template>
  <div class="assistant-page">
    <div class="page-header">
      <h1>AI Assistant</h1>
      <p class="subtitle">Search papers or ask questions about research topics</p>
      <ChatControls
        ref="chatControlsRef"
        :mode="conversationStore.mode"
        :show-history-panel="conversationStore.showHistoryPanel"
        :has-memory="memoryStore.hasCoreMemory"
        :memory-count="memoryStore.totalMemories"
        @update:mode="conversationStore.mode = $event"
        @new-conversation="createNewConversation"
        @toggle-history="toggleConversationHistoryPanel"
        @go-to-memory="goToMemory"
      />
    </div>

    <ChatContainer
      :mode="conversationStore.mode"
      :messages="currentModeMessages"
      :loading="isLoading"
      :is-copied="isCopied"
      :format-message="formatMessage"
      :set-message-ref="setMessageRef"
      @view-paper="viewPaper"
      @go-to-settings="goToSettings"
      @copy="copyMessage"
      @save-to-knowledge="saveToKnowledge"
      @retry="retryMessage"
    >
      <template #empty-state-content>
        <div class="suggestions">
          <button v-for="suggestion in currentSuggestions" :key="suggestion" class="suggestion-btn" @click="sendSuggestion(suggestion)">
            {{ suggestion }}
          </button>
        </div>
      </template>

      <template #input-area>
        <ChatInput
          ref="chatInputRef"
          v-model="inputMessage"
          :mode="conversationStore.mode"
          :loading="isLoading"
          @send="sendMessage()"
        />
      </template>
    </ChatContainer>

    <ConversationHistoryPanel
      :visible="conversationStore.showHistoryPanel"
      :trigger-element="historyBtnRef"
      @close="conversationStore.showHistoryPanel = false"
      @select="onConversationSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLLMStore } from '@/stores/llm-store'
import { useMemoryStore } from '@/stores/memory-store'
import { useConversationStore } from '@/stores/conversation-store'
import { useChatMessages, type Message } from '@/composables/useChatMessages'
import { useMessageCopy } from '@/composables/useMessageCopy'
import { ROUTES } from '@/constants/routes'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ChatControls from '@/components/chat/ChatControls.vue'
import ConversationHistoryPanel from '@/components/ConversationHistoryPanel.vue'

const router = useRouter()
const llmStore = useLLMStore()
const memoryStore = useMemoryStore()
const conversationStore = useConversationStore()
const { mode } = storeToRefs(conversationStore)

const inputMessage = ref('')
const chatInputRef = ref<InstanceType<typeof ChatInput> | null>(null)
const chatControlsRef = ref<InstanceType<typeof ChatControls> | null>(null)

const {
  currentModeMessages,
  currentUserMessageIndex,
  isLoading: chatLoading,
  setMessageRef,
  sendMessage: sendChatMessage,
  retryMessage: retryChatMessage,
  clearMessages,
  setMessages,
  saveToKnowledge,
} = useChatMessages(mode)

const {
  copyMessage,
  isCopied
} = useMessageCopy()

const isLoading = computed(() => chatLoading.value)

const historyBtnRef = computed(() => chatControlsRef.value?.historyBtnRef || null)

const viewPaper = (paperId: string) => {
  router.push(ROUTES.PAPER_DETAIL.replace(':id', paperId))
}

watch(() => conversationStore.currentSessionId, (newId) => {
  if (!newId) {
    currentUserMessageIndex.value = null
    clearMessages()
  }
})

watch(() => conversationStore.mode, async (newMode) => {
  currentUserMessageIndex.value = null
  clearMessages()
  await conversationStore.switchMode(newMode)
  
  if (conversationStore.currentMessages.length > 0) {
    const messages: Message[] = conversationStore.currentMessages.map(msg => ({
      role: msg.role,
      content: msg.content || '',
      papers: msg.papers,
      answer: msg.answer,
      references: msg.references,
    }))
    setMessages(messages)
  }
  
  if (newMode === 'ask' && llmStore.providers.length === 0) {
    llmStore.init()
  }
}, { immediate: true })

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
  return conversationStore.mode === 'search' ? searchSuggestions : askSuggestions
})

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return
  
  inputMessage.value = ''
  chatInputRef.value?.resetHeight()
  await sendChatMessage(message)
}

const sendSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
  sendMessage()
}

const goToSettings = () => {
  router.push(ROUTES.SETTINGS)
}

const goToMemory = () => {
  router.push(ROUTES.MEMORY)
}

const createNewConversation = () => {
  clearMessages()
  conversationStore.currentSessionId = ''
  conversationStore.currentMessages = []
}

const toggleConversationHistoryPanel = () => {
  conversationStore.showHistoryPanel = !conversationStore.showHistoryPanel
}

const onConversationSelect = async (sessionId: string) => {
  clearMessages()
  await conversationStore.switchConversation(sessionId)
  
  if (conversationStore.currentMessages && conversationStore.currentMessages.length > 0) {
    const messages: Message[] = conversationStore.currentMessages.map(msg => ({
      role: msg.role,
      content: msg.content || '',
      papers: msg.papers,
      answer: msg.answer,
      references: msg.references,
    }))
    setMessages(messages)
  }
}

const retryMessage = async (index: number) => {
  await retryChatMessage(index)
}

onMounted(() => {
  chatInputRef.value?.focus()
  if (conversationStore.mode === 'ask') {
    llmStore.init()
  }
  memoryStore.init()
  conversationStore.init()
})
</script>

<style scoped>
.assistant-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-muted);
  margin: 0 0 16px 0;
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
  border-color: #00BCD4;
  color: #00BCD4;
}

@media (max-width: 768px) {
  .assistant-page {
    padding: 80px 16px 16px 16px;
  }

  .suggestions {
    flex-direction: column;
  }

  .suggestion-btn {
    text-align: left;
  }
}
</style>
