<template>
  <div class="header-controls">
    <div class="mode-switch">
      <button 
        :class="['mode-btn', { active: mode === 'search' }]"
        @click="$emit('update:mode', 'search')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <span>Search</span>
      </button>
      <button 
        :class="['mode-btn', { active: mode === 'ask' }]"
        @click="$emit('update:mode', 'ask')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Ask</span>
      </button>
    </div>
    <div class="conversation-controls">
      <button class="header-action-btn" @click="$emit('new-conversation')" title="New Conversation">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>New</span>
      </button>
      <button 
        ref="historyBtnRef"
        class="header-action-btn" 
        :class="{ active: showHistoryPanel }"
        @click="$emit('toggle-history')" 
        title="Conversation History"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M12 8v4l3 3"/>
          <circle cx="12" cy="12" r="10"/>
        </svg>
        <span>History</span>
      </button>
    </div>
    <div 
      v-if="hasMemory" 
      class="memory-indicator" 
      @click="$emit('go-to-memory')" 
      title="Memory active - Click to manage"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      <span class="memory-count">{{ memoryCount }}</span>
    </div>
    <MemoryToggle 
      v-if="mode === 'ask'"
      @change="onMemoryToggleChange" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MemoryToggle from './MemoryToggle.vue'

defineProps<{
  mode: 'search' | 'ask'
  showHistoryPanel: boolean
  hasMemory: boolean
  memoryCount: number
}>()

const emit = defineEmits<{
  (e: 'update:mode', mode: 'search' | 'ask'): void
  (e: 'new-conversation'): void
  (e: 'toggle-history'): void
  (e: 'go-to-memory'): void
  (e: 'memory-toggle', value: boolean): void
}>()

const historyBtnRef = ref<HTMLElement | null>(null)

const onMemoryToggleChange = (value: boolean) => {
  emit('memory-toggle', value)
}

defineExpose({
  historyBtnRef
})
</script>

<style scoped>
.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-switch {
  display: flex;
  gap: 8px;
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
  border-color: #00BCD4;
  color: #00BCD4;
}

.mode-btn.active {
  background: #00BCD4;
  border-color: #00BCD4;
  color: white;
}

.conversation-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(0, 188, 212, 0.1);
  border: 1px solid rgba(0, 188, 212, 0.3);
  border-radius: 20px;
  color: #00BCD4;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.header-action-btn:hover {
  background: rgba(0, 188, 212, 0.2);
  border-color: #00BCD4;
}

.header-action-btn.active {
  background: rgba(0, 188, 212, 0.3);
  border-color: #00BCD4;
}

.header-action-btn svg {
  width: 16px;
  height: 16px;
}

.memory-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(0, 188, 212, 0.1);
  border: 1px solid rgba(0, 188, 212, 0.3);
  border-radius: 20px;
  color: #00BCD4;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.memory-indicator:hover {
  background: rgba(0, 188, 212, 0.2);
  border-color: #00BCD4;
}

.memory-indicator svg {
  width: 16px;
  height: 16px;
}

.memory-count {
  font-weight: 600;
}

@media (max-width: 768px) {
  .header-controls {
    flex-wrap: wrap;
  }
}
</style>
