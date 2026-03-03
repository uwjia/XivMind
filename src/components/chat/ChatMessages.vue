<template>
  <div class="chat-messages">
    <div 
      v-for="(message, index) in messages" 
      :key="index" 
      class="message" 
      :class="message.role"
      :ref="el => setMessageRef(el, index)"
    >
      <div class="message-avatar">
        <svg v-if="message.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <svg v-else-if="mode === 'search'" viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
          <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
        </svg>
      </div>
      <div class="message-content">
        <div v-if="message.papers && message.papers.length > 0" class="papers-result">
          <div class="result-header">
            Found {{ message.papers.length }} papers
            <span v-if="message.model" class="model-badge">{{ message.model }}</span>
          </div>
          <div class="paper-cards">
            <div 
              v-for="paper in message.papers" 
              :key="paper.id" 
              class="paper-card" 
              @click="$emit('viewPaper', paper.id)"
            >
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
            <div 
              v-for="ref in message.references" 
              :key="ref.id" 
              class="reference-item" 
              @click="$emit('viewPaper', ref.id)"
            >
              <span class="ref-title">{{ ref.title }}</span>
              <span class="ref-authors">{{ ref.authors?.slice(0, 2).join(', ') }}</span>
              <span class="ref-score">{{ (ref.relevance_score * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
        <div v-else class="message-text" v-html="formatMessage(message.content)"></div>
        <div v-if="message.isConfigError" class="config-error-hint">
          <button @click="$emit('goToSettings')" class="settings-link-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            Go to Settings to configure LLM Provider
          </button>
        </div>
        <div v-if="message.role === 'assistant'" class="message-actions">
          <button 
            @click="$emit('copy', message)" 
            class="action-icon-btn"
            :title="isCopied(message) ? 'Copied!' : 'Copy all'"
          >
            <svg v-if="isCopied(message)" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </button>
          <button 
            @click="$emit('saveToKnowledge', message)" 
            class="action-icon-btn save-to-knowledge-btn"
            title="Save to Knowledge Base"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </button>
          <button 
            v-if="message.answer || message.papers || message.content"
            @click="$emit('retry', index)" 
            class="action-icon-btn"
            title="Retry"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M23 4v6h-6"/>
              <path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="message assistant">
      <div class="message-avatar">
        <svg v-if="mode === 'search'" viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="#00BCD4">
          <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
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
</template>

<script setup lang="ts">
import type { Message } from '../../composables/useChatMessages'

defineProps<{
  messages: Message[]
  loading?: boolean
  isCopied: (message: Message) => boolean
  formatMessage: (content: string) => string
  setMessageRef: (el: any, index: number) => void
  mode?: 'search' | 'ask'
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
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
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
  background: rgba(0, 188, 212, 0.1);
}

.message-avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  max-width: 80%;
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

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-content:hover .message-actions {
  opacity: 1;
}

.action-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-icon-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.action-icon-btn.save-to-knowledge-btn:hover {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.action-icon-btn svg {
  width: 16px;
  height: 16px;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.config-error-hint {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.settings-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settings-link-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
}

.settings-link-btn svg {
  width: 16px;
  height: 16px;
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
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
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
  border-color: #00BCD4;
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
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
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
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
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
  background: #00BCD4;
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
</style>
