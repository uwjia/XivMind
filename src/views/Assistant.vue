<template>
  <div class="assistant-page">
    <div class="page-header">
      <h1>AI Assistant</h1>
      <p class="subtitle">Ask questions about papers, get summaries, and explore research topics</p>
    </div>

    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
            </svg>
          </div>
          <h3>Start a conversation</h3>
          <p>Ask me anything about arXiv papers, research topics, or get help with your literature review.</p>
          <div class="suggestions">
            <button v-for="suggestion in suggestions" :key="suggestion" class="suggestion-btn" @click="sendSuggestion(suggestion)">
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
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
          </div>
        </div>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"/>
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
          placeholder="Ask about papers, request summaries, or explore research topics..."
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
import { ref, nextTick, onMounted } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

const suggestions = [
  'What are the latest advances in transformer architectures?',
  'Summarize recent papers on large language models',
  'Explain the key concepts of attention mechanisms',
  'What is the state of multimodal AI research?'
]

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
  
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: `I understand you're asking about: "${message}"\n\nThis is a placeholder response. To enable AI-powered responses, you'll need to integrate with an LLM API (like OpenAI, Anthropic Claude, or a local model).\n\nFeatures to implement:\n- **API Integration**: Connect to your preferred LLM provider\n- **Context**: Add paper context from your bookmarks and downloads\n- **RAG**: Implement retrieval-augmented generation for paper-specific questions`
    })
    isLoading.value = false
    scrollToBottom()
  }, 1500)
}

const sendSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
  sendMessage()
}

onMounted(() => {
  inputRef.value?.focus()
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
  margin: 0;
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
  max-width: 70%;
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
    max-width: 85%;
  }

  .suggestions {
    flex-direction: column;
  }

  .suggestion-btn {
    text-align: left;
  }
}
</style>
