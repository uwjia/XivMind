<template>
  <div class="chat-input">
    <div v-if="mode === 'search' || mode === 'ask'" class="input-container" :title="'Enter to send · Shift+Enter for new line'">
      <div class="input-wrapper">
        <textarea
          :value="modelValue"
          @input="handleInput"
          @keydown="handleKeydown"
          :placeholder="mode === 'search' ? 'Enter your search query...' : 'Ask a question about research...'"
          ref="inputRef"
          rows="2"
        ></textarea>
        <button 
          @click="$emit('send')" 
          :disabled="!modelValue.trim() || loading" 
          class="send-btn"
          :title="modelValue.trim() ? 'Send message' : 'Type a message'"
        >
          <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  mode: 'search' | 'ask'
  modelValue: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'send'): void
}>()

const inputRef = ref<HTMLTextAreaElement | null>(null)

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  autoResize()
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    emit('send')
  }
}

const autoResize = () => {
  const textarea = inputRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    const newHeight = Math.min(textarea.scrollHeight, 200)
    textarea.style.height = `${newHeight}px`
  }
}

const resetHeight = () => {
  const textarea = inputRef.value
  if (textarea) {
    textarea.style.height = '72px'
  }
}

const focus = () => {
  inputRef.value?.focus()
}

defineExpose({ resetHeight, focus })
</script>

<style scoped>
.chat-input {
  width: 100%;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.input-wrapper:focus-within {
  border-color: #00BCD4;
  box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1), 0 4px 12px rgba(0, 0, 0, 0.08);
}

.input-wrapper textarea {
  flex: 1;
  padding: 14px 16px;
  padding-right: 56px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.5;
  resize: none;
  outline: none;
  font-family: inherit;
  min-height: 72px;
  max-height: 200px;
  overflow-y: auto;
}

.input-wrapper textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: #00BCD4;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #059669;
  transform: scale(1.05);
}

.send-btn:disabled {
  background: var(--border-color);
  cursor: not-allowed;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}

.send-btn .spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
