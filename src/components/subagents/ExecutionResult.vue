<template>
  <div class="execution-result">
    <div class="result-header">
      <div class="result-title">
        <h3>Execution Result</h3>
        <span class="status-badge" :class="result.status.toLowerCase()">
          {{ result.status }}
        </span>
      </div>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <div class="result-meta">
      <div class="meta-item">
        <span class="meta-label">Agent:</span>
        <span class="meta-value">{{ result.agent_id }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Task ID:</span>
        <span class="meta-value">{{ result.task_id }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Turns:</span>
        <span class="meta-value">{{ result.turns_used }}</span>
      </div>
      <div v-if="result.model" class="meta-item">
        <span class="meta-label">Model:</span>
        <span class="meta-value">{{ result.model }}</span>
      </div>
      <div v-if="result.provider" class="meta-item">
        <span class="meta-label">Provider:</span>
        <span class="meta-value">{{ result.provider }}</span>
      </div>
    </div>

    <div v-if="result.error" class="result-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <span>{{ result.error }}</span>
    </div>

    <div class="result-body">
      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'output' }"
          @click="activeTab = 'output'"
        >
          Output
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'messages' }"
          @click="activeTab = 'messages'"
        >
          Messages ({{ messages.length }})
        </button>
      </div>

      <div v-if="activeTab === 'output'" class="tab-content output-tab">
        <div class="output-actions">
          <button class="action-btn" @click="copyOutput" title="Copy to clipboard">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            Copy
          </button>
        </div>
        <pre class="output-content">{{ result.output || 'No output generated' }}</pre>
      </div>

      <div v-else class="tab-content messages-tab">
        <div class="messages-list">
          <div 
            v-for="(msg, idx) in messages" 
            :key="idx" 
            class="message-item"
            :class="msg.role"
          >
            <div class="message-header">
              <span class="message-role">{{ getRoleLabel(msg.role) }}</span>
              <span v-if="msg.name" class="message-name">{{ msg.name }}</span>
            </div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { SubAgentExecuteResponse } from '../../types/subagent'

const props = defineProps<{
  result: SubAgentExecuteResponse
}>()

defineEmits<{
  close: []
}>()

const activeTab = ref<'output' | 'messages'>('output')

const messages = computed(() => {
  return (props.result as any).messages || []
})

const getRoleLabel = (role: string): string => {
  const labels: Record<string, string> = {
    system: 'System',
    user: 'User',
    assistant: 'Assistant',
    tool: 'Tool Result',
  }
  return labels[role] || role
}

const copyOutput = async () => {
  try {
    await navigator.clipboard.writeText(props.result.output || '')
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}
</script>

<style scoped>
.execution-result {
  background: var(--bg-secondary);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-title h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.status-badge {
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.completed {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.status-badge.running {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  padding: 4px;
}

.close-btn:hover {
  color: var(--text-primary);
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
}

.meta-label {
  color: var(--text-muted);
}

.meta-value {
  color: var(--text-primary);
  font-weight: 500;
}

.result-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  font-size: 0.9rem;
}

.result-error svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.result-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabs {
  display: flex;
  gap: 4px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  padding: 8px 16px;
  background: none;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.tab-content {
  flex: 1;
  overflow: auto;
  padding: 16px 20px;
}

.output-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.output-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.output-content {
  margin: 0;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--text-primary);
  font-family: inherit;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-primary);
}

.message-item.system {
  background: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366F1;
}

.message-item.user {
  background: rgba(0, 188, 212, 0.05);
  border-left: 3px solid #00BCD4;
}

.message-item.assistant {
  background: rgba(245, 158, 11, 0.05);
  border-left: 3px solid #F59E0B;
}

.message-item.tool {
  background: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366F1;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.message-role {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
}

.message-name {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  color: var(--text-secondary);
}

.message-content {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
