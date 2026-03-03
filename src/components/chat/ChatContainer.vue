<template>
  <div class="chat-container">
    <div class="messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg v-if="mode === 'search'" viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
            <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"/>
          </svg>
        </div>
        <h3>{{ mode === 'search' ? 'Search Papers' : mode === 'ask' ? 'Ask Questions' : 'Select a Skill' }}</h3>
        <p v-if="mode === 'search'">Enter a natural language query to find relevant papers using semantic search.</p>
        <p v-else-if="mode === 'ask'">Ask questions about research topics and get AI-powered answers with paper references.</p>
        <p v-else>Select a skill to perform specific tasks on papers.</p>
        
        <slot name="empty-state-content"></slot>
      </div>

      <ChatMessages
        v-else
        :messages="messages"
        :loading="loading"
        :is-copied="isCopied"
        :format-message="formatMessage"
        :set-message-ref="setMessageRef"
        :mode="mode"
        @view-paper="$emit('viewPaper', $event)"
        @go-to-settings="$emit('goToSettings')"
        @copy="$emit('copy', $event)"
        @save-to-knowledge="$emit('saveToKnowledge', $event)"
        @retry="$emit('retry', $event)"
      />
    </div>

    <div class="input-area">
      <slot name="input-area"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import ChatMessages from './ChatMessages.vue'
import type { Message } from '../../composables/useChatMessages'

defineProps<{
  mode: 'search' | 'ask'
  messages: Message[]
  loading?: boolean
  isCopied: (message: Message) => boolean
  formatMessage: (content: string) => string
  setMessageRef: (el: any, index: number) => void
}>()

defineEmits<{
  (e: 'viewPaper', paperId: string): void
  (e: 'goToSettings'): void
  (e: 'copy', message: Message): void
  (e: 'saveToKnowledge', message: Message): void
  (e: 'retry', index: number): void
}>()
</script>

<style scoped>
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
  justify-content: flex-start;
  padding-top: 40px;
  height: 100%;
  text-align: center;
  color: var(--text-muted);
  overflow-y: auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
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

.input-area {
  padding: 16px 24px 12px;
  background: var(--bg-primary);
}
</style>
