<template>
  <div class="execution-monitor">
    <div class="monitor-header">
      <h3>Execution Monitor</h3>
      <div class="status-badge" :class="statusClass">
        {{ statusText }}
      </div>
    </div>
    
    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
      <span class="progress-text">{{ Math.round(progress) }}%</span>
    </div>
    
    <div class="stats-grid">
      <div class="stat-item">
        <span class="stat-value">{{ totalNodes }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-item running">
        <span class="stat-value">{{ runningCount }}</span>
        <span class="stat-label">Running</span>
      </div>
      <div class="stat-item success">
        <span class="stat-value">{{ successCount }}</span>
        <span class="stat-label">Success</span>
      </div>
      <div class="stat-item error">
        <span class="stat-value">{{ errorCount }}</span>
        <span class="stat-label">Error</span>
      </div>
    </div>
    
    <div class="logs-section" v-if="showLogs">
      <div class="logs-header">
        <span>Logs</span>
        <button class="clear-btn" @click="clearLogs">Clear</button>
      </div>
      <div class="logs-list" ref="logsContainer">
        <div
          v-for="(log, index) in logs"
          :key="index"
          class="log-item"
          :class="log.level"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-node">{{ log.nodeLabel }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <div v-if="logs.length === 0" class="logs-empty">
          No logs yet
        </div>
      </div>
    </div>
    
    <div v-if="executionOutput && showOutput" class="output-section">
      <div class="output-header">
        <span>Output</span>
        <div class="output-actions">
          <button class="copy-btn" @click="copyOutput">Copy</button>
          <button class="edit-btn" @click="showEditDialog = true">Edit</button>
        </div>
      </div>
      <div class="output-content">
        {{ executionOutput }}
      </div>
    </div>
    
    <OutputEditDialog
      v-if="showEditDialog"
      :model-value="executionOutput || ''"
      @close="showEditDialog = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useWorkflow } from '@/composables/useWorkflow'
import OutputEditDialog from './OutputEditDialog.vue'

interface LogEntry {
  timestamp: Date
  nodeLabel: string
  level: 'info' | 'warn' | 'error'
  message: string
}

const {
  nodes,
  isExecuting,
  executionProgress,
  executionLogs,
  executionOutput,
  clearExecutionLogs,
} = useWorkflow()

const props = defineProps<{
  showLogs?: boolean
  showOutput?: boolean
}>()

const logsContainer = ref<HTMLElement | null>(null)
const showEditDialog = ref(false)

const progress = computed(() => executionProgress.value)

const totalNodes = computed(() => nodes.value.length)
const runningCount = computed(() => nodes.value.filter(n => n.status === 'running').length)
const successCount = computed(() => nodes.value.filter(n => n.status === 'success').length)
const errorCount = computed(() => nodes.value.filter(n => n.status === 'error').length)

const statusClass = computed(() => {
  if (!isExecuting.value && progress.value === 0) return 'idle'
  if (isExecuting.value) return 'running'
  if (errorCount.value > 0) return 'error'
  return 'success'
})

const statusText = computed(() => {
  if (!isExecuting.value && progress.value === 0) return 'Idle'
  if (isExecuting.value) return 'Running'
  if (errorCount.value > 0) return 'Error'
  return 'Completed'
})

const logs = computed<LogEntry[]>(() => {
  return executionLogs.value.map(log => {
    const node = nodes.value.find(n => n.id === log.nodeId)
    return {
      timestamp: log.timestamp,
      nodeLabel: node?.label || log.nodeId || 'System',
      level: log.level as 'info' | 'warn' | 'error',
      message: log.message,
    }
  })
})

watch(executionLogs, () => {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}, { deep: true })

watch(nodes, (newNodes, oldNodes) => {
  newNodes.forEach(node => {
    const oldNode = oldNodes?.find(n => n.id === node.id)
    
    if (oldNode && oldNode.status !== node.status) {
      addLog(node.label, node.status as any, `Status changed: ${oldNode.status} → ${node.status}`)
    }
  })
}, { deep: true })

function addLog(_nodeLabel: string, _level: 'info' | 'warn' | 'error', _message: string) {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

function clearLogs() {
  clearExecutionLogs()
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

async function copyOutput() {
  if (executionOutput.value) {
    try {
      await navigator.clipboard.writeText(executionOutput.value)
    } catch (e) {
      console.error('Failed to copy output:', e)
    }
  }
}

defineExpose({
  addLog,
  clearLogs,
})
</script>

<style scoped>
.execution-monitor {
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  min-height: 200px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.monitor-header h3 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.idle {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.status-badge.running {
  background: rgba(59, 130, 246, 0.2);
  color: #3B82F6;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #10B981;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.2);
  color: #EF4444;
}

.progress-section {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border-color);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8B5CF6, #6366F1);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 40px;
  text-align: right;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.stat-item.running .stat-value {
  color: #3B82F6;
}

.stat-item.success .stat-value {
  color: #10B981;
}

.stat-item.error .stat-value {
  color: #EF4444;
}

.logs-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 80px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.logs-header span {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.clear-btn {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--text-muted);
  cursor: pointer;
}

.clear-btn:hover {
  background: var(--bg-tertiary);
}

.logs-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
}

.logs-list::-webkit-scrollbar {
  width: 6px;
}

.logs-list::-webkit-scrollbar-track {
  background: transparent;
}

.logs-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.logs-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.log-item {
  display: flex;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
}

.log-item:hover {
  background: var(--bg-tertiary);
}

.log-item.info {
  color: var(--text-primary);
}

.log-item.warn {
  color: #FBBF24;
}

.log-item.error {
  color: #EF4444;
}

.log-time {
  color: var(--text-muted);
  flex-shrink: 0;
}

.log-node {
  color: #8B5CF6;
  flex-shrink: 0;
}

.log-message {
  color: var(--text-secondary);
}

.logs-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.output-section {
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  min-height: 80px;
  flex-shrink: 0;
}

.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.output-header span {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.output-actions {
  display: flex;
  gap: 8px;
}

.copy-btn,
.edit-btn {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover,
.edit-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.edit-btn {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3B82F6;
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.2);
}

.output-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 16px;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
