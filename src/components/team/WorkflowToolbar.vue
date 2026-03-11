<template>
  <div class="workflow-toolbar">
    <div class="toolbar-left">
      <button 
        class="tool-btn drawer-btn"
        :class="{ active: !leftDrawerCollapsed }"
        @click="$emit('toggle-left-drawer')"
        title="Toggle Node Palette"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="7" height="18" rx="1"/>
          <rect x="14" y="3" width="7" height="18" rx="1"/>
        </svg>
      </button>
      
      <div class="separator"></div>
      
      <div class="workflow-name">
        <input
          v-model="workflowName"
          type="text"
          placeholder="Workflow name"
          @change="updateName"
        />
      </div>
    </div>
    
    <div class="toolbar-center">
      <button 
        class="tool-btn" 
        @click="undo" 
        :disabled="!canUndo"
        title="Undo (Ctrl+Z)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 7v6h6"/>
          <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/>
        </svg>
      </button>
      
      <button 
        class="tool-btn" 
        @click="redo" 
        :disabled="!canRedo"
        title="Redo (Ctrl+Y)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 7v6h-6"/>
          <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13"/>
        </svg>
      </button>
      
      <div class="separator"></div>
      
      <button class="tool-btn" @click="saveWorkflow" title="Save">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
      </button>
      
      <button class="tool-btn" @click="exportWorkflow" title="Export JSON">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </button>
      
      <div class="separator"></div>

      <div class="load-dropdown">
        <button class="tool-btn templates-btn" @click="toggleLoadMenu" title="Load">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </button>
        <div v-if="showLoadMenu" class="dropdown-menu">
          <div class="dropdown-header">Preset Workflows</div>
          <button 
            v-for="preset in presetWorkflows" 
            :key="preset.id"
            class="dropdown-item"
            @click="loadPreset(preset)"
          >
            <span class="preset-name">{{ preset.name }}</span>
            <span class="preset-desc">{{ preset.description }}</span>
          </button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" @click="loadFromFile">
            <span class="preset-name">📁 Load from file...</span>
          </button>
        </div>
      </div>
      
      <button class="tool-btn templates-btn" @click="$emit('open-templates')" title="Templates">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
      </button>
      
      <div class="separator"></div>
      
      <button class="tool-btn" @click="clearCanvas" title="Clear Canvas">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
      
      <div class="separator"></div>
      
      <button class="tool-btn center-btn" @click="centerView" title="Center View">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4"/>
          <path d="M12 18v4"/>
          <path d="M2 12h4"/>
          <path d="M18 12h4"/>
        </svg>
      </button>
    </div>
    
    <div class="toolbar-right">
      <div class="execute-wrapper">
        <button 
          v-if="!isExecuting"
          class="execute-btn"
          @click="execute"
          :disabled="!canExecute"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Execute
        </button>
        
        <button 
          v-else
          class="stop-btn"
          @click="stop"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="6" y="6" width="12" height="12"/>
          </svg>
          Stop
        </button>
        
        <div v-if="!isExecuting && !canExecute && validationErrors.length > 0" class="execute-tooltip">
          <div class="tooltip-header">⚠️ Cannot Execute</div>
          <ul class="tooltip-errors">
            <li v-for="(error, index) in validationErrors" :key="index">{{ error }}</li>
          </ul>
        </div>
      </div>
      
      <div class="separator"></div>
      
      <button 
        class="tool-btn drawer-btn"
        :class="{ active: !rightDrawerCollapsed }"
        @click="$emit('toggle-right-drawer')"
        title="Toggle Config & Monitor"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="7" rx="1"/>
          <rect x="3" y="14" width="18" height="7" rx="1"/>
        </svg>
      </button>
      
      <button 
        class="tool-btn monitor-btn"
        :class="{ active: showLogs }"
        @click="$emit('toggle-logs')"
        title="Toggle Logs"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </button>
      
      <button 
        class="tool-btn monitor-btn"
        :class="{ active: showOutput }"
        @click="$emit('toggle-output')"
        title="Toggle Output"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M9 12l2 2 4-4"/>
        </svg>
      </button>
    </div>
    
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      style="display: none"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWorkflow } from '@/composables/useWorkflow'

const props = defineProps<{
  leftDrawerCollapsed?: boolean
  rightDrawerCollapsed?: boolean
  showLogs?: boolean
  showOutput?: boolean
}>()

const {
  currentWorkflow,
  canUndo,
  canRedo,
  isExecuting,
  nodes,
  undo,
  redo,
  createNewWorkflow,
  importFromJSON,
  exportToJSON,
  stopExecution,
  validateWorkflow,
} = useWorkflow()

const fileInput = ref<HTMLInputElement | null>(null)
const showLoadMenu = ref(false)
const isExecutingInternal = ref(false)

const presetWorkflows = ref<Array<{id: string; name: string; description: string; url: string}>>([
  {
    id: 'task-analysis',
    name: 'Task Analysis',
    description: 'Analyze task complexity and decomposition',
    url: '/workflows/task-analysis.json'
  },
  {
    id: 'paper-analysis',
    name: 'Paper Analysis',
    description: 'Simple paper analysis workflow',
    url: '/workflows/paper-analysis.json'
  },
  {
    id: 'multi-agent',
    name: 'Multi-Agent Collaboration',
    description: 'Complex parallel workflow',
    url: '/workflows/multi-agent.json'
  },
  {
    id: 'quick-summary',
    name: 'Quick Summary',
    description: 'Minimal summarization workflow',
    url: '/workflows/quick-summary.json'
  },
])

const workflowName = computed({
  get: () => currentWorkflow.value?.name || 'Untitled Workflow',
  set: (value) => {
    if (currentWorkflow.value) {
      currentWorkflow.value.name = value
    }
  }
})

const canExecute = computed(() => {
  if (isExecuting.value) return false
  if (nodes.value.length === 0) return false
  const validation = validateWorkflow()
  return validation.valid
})

const validationErrors = computed(() => {
  if (isExecuting.value || nodes.value.length === 0) return []
  const validation = validateWorkflow()
  return validation.errors
})

const emit = defineEmits<{
  (e: 'save'): void
  (e: 'load'): void
  (e: 'execute'): void
  (e: 'stop'): void
  (e: 'toggle-left-drawer'): void
  (e: 'toggle-right-drawer'): void
  (e: 'center-view'): void
  (e: 'toggle-logs'): void
  (e: 'toggle-output'): void
  (e: 'open-templates'): void
}>()

function updateName() {
}

function saveWorkflow() {
  const json = exportToJSON()
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${workflowName.value.replace(/\s+/g, '_')}.json`
  a.click()
  URL.revokeObjectURL(url)
  emit('save')
}

function toggleLoadMenu() {
  showLoadMenu.value = !showLoadMenu.value
}

function closeLoadMenu() {
  showLoadMenu.value = false
}

async function loadPreset(preset: { id: string; name: string; description: string; url: string }) {
  try {
    const response = await fetch(preset.url)
    const json = await response.text()
    importFromJSON(json)
    closeLoadMenu()
    emit('load')
  } catch (error) {
    console.error('Failed to load preset workflow:', error)
  }
}

function loadFromFile() {
  closeLoadMenu()
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target?.result as string
    importFromJSON(content)
    emit('load')
  }
  reader.readAsText(file)
  
  target.value = ''
}

function exportWorkflow() {
  const json = exportToJSON()
  navigator.clipboard.writeText(json)
}

function clearCanvas() {
  if (confirm('Are you sure you want to clear the canvas?')) {
    createNewWorkflow()
  }
}

async function execute() {
  if (isExecuting.value || isExecutingInternal.value) {
    return
  }
  
  const validation = validateWorkflow()
  if (!validation.valid) {
    console.log('execute validation errors:' + validation.errors)
    return
  }
  
  isExecutingInternal.value = true
  
  try {
    emit('execute')
  } finally {
    isExecutingInternal.value = false
  }
}

function stop() {
  stopExecution()
  emit('stop')
}

function centerView() {
  emit('center-view')
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.load-dropdown')) {
    closeLoadMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.workflow-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-name input {
  background: transparent;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
}

.workflow-name input:focus {
  outline: none;
  background: var(--bg-tertiary);
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

.tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tool-btn svg {
  width: 18px;
  height: 18px;
  color: var(--text-secondary);
}

.tool-btn.drawer-btn {
  background: rgba(59, 130, 246, 0.1);
  border: none;
}

.tool-btn.drawer-btn svg {
  color: #3B82F6;
}

.tool-btn.drawer-btn:hover {
  background: rgba(59, 130, 246, 0.2);
}

.tool-btn.drawer-btn.active {
  background: rgba(16, 185, 129, 0.15);
}

.tool-btn.drawer-btn.active svg {
  color: #10B981;
}

.tool-btn.monitor-btn {
  background: rgba(139, 92, 246, 0.1);
  border: none;
}

.tool-btn.monitor-btn svg {
  color: #8B5CF6;
}

.tool-btn.monitor-btn:hover {
  background: rgba(139, 92, 246, 0.2);
}

.tool-btn.monitor-btn.active {
  background: rgba(16, 185, 129, 0.15);
}

.tool-btn.monitor-btn.active svg {
  color: #10B981;
}

.tool-btn.templates-btn {
  background: rgba(236, 72, 153, 0.1);
  border: none;
}

.tool-btn.templates-btn svg {
  color: #EC4899;
}

.tool-btn.templates-btn:hover {
  background: rgba(236, 72, 153, 0.2);
}

.separator {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 4px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.execute-btn,
.stop-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.execute-btn {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border: none;
  color: white;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.stop-btn {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  border: none;
  color: white;
}

.stop-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.execute-btn svg,
.stop-btn svg {
  width: 16px;
  height: 16px;
}

.load-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  min-width: 240px;
  z-index: 1002;
  overflow: hidden;
}

.dropdown-header {
  padding: 10px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-secondary);
}

.dropdown-item {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: var(--bg-tertiary);
}

.preset-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.preset-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 4px 0;
}

.execute-wrapper {
  position: relative;
}

.execute-tooltip {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  min-width: 220px;
  max-width: 320px;
  z-index: 1002;
  padding: 12px;
}

.tooltip-header {
  font-size: 0.85rem;
  font-weight: 600;
  color: #EF4444;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.tooltip-errors {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tooltip-errors li {
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 4px 0;
  padding-left: 12px;
  position: relative;
}

.tooltip-errors li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #FBBF24;
}
</style>
