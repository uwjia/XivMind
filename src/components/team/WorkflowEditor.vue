<template>
  <div class="workflow-editor">
    <WorkflowToolbar
      :left-drawer-collapsed="leftDrawerCollapsed"
      :right-drawer-collapsed="activeDrawer !== 'config'"
      :show-logs="activeDrawer === 'logs'"
      :show-output="activeDrawer === 'output'"
      @save="handleSave"
      @load="handleLoad"
      @execute="handleExecute"
      @stop="handleStop"
      @toggle-left-drawer="leftDrawerCollapsed = !leftDrawerCollapsed"
      @toggle-right-drawer="toggleDrawer('config')"
      @center-view="handleCenterView"
      @toggle-logs="toggleDrawer('logs')"
      @toggle-output="toggleDrawer('output')"
      @open-templates="openTemplates"
    />
    
    <div class="editor-main">
      <!-- Left Drawer: Node Palette -->
      <div class="left-drawer" :class="{ collapsed: leftDrawerCollapsed }">
        <div class="drawer-content">
          <NodePalette @node-selected="handleNodeSelected" />
        </div>
      </div>
      
      <div class="canvas-container">
        <CustomCanvas
          v-if="useCustomCanvas"
          ref="customCanvasRef"
          :nodes="nodes"
          :edges="edges"
          :selected-node-id="selectedNodeId"
          :available-agents="availableAgents"
          :available-skills="availableSkills"
          :active-view="activeView || 'workflow'"
          @node-select="handleNodeSelect"
          @node-drag="handleNodeDrag"
          @node-config-update="handleNodeConfigUpdate"
          @node-label-update="handleNodeLabelUpdate"
          @edge-create="handleEdgeCreate"
          @edge-delete="handleEdgeDelete"
          @canvas-click="handleCanvasClick"
          @canvas-double-click="handleCanvasDoubleClick"
          @node-drop="handleNodeDrop"
          @change-view="$emit('change-view', $event)"
        />
        <WorkflowCanvas
          v-else
          ref="canvasRef"
          :active-view="activeView || 'workflow'"
          @node-selected="handleCanvasNodeSelected"
          @edge-selected="handleEdgeSelected"
          @canvas-click="handleCanvasClick"
          @change-view="$emit('change-view', $event)"
        />
      </div>
      
      <!-- Right Drawer: Config & Monitor -->
      <div class="right-drawer" :class="{ collapsed: activeDrawer !== 'config' }">
        <div 
          class="resize-handle"
          :class="{ dragging: isResizing && resizingDrawer === 'config' }"
          @mousedown="startResize('config', $event)"
        ></div>
        <div class="drawer-content">
          <div class="right-panel-content">
            <NodeConfigPanel ref="configPanelRef" />
            <ExecutionMonitor ref="monitorRef" />
          </div>
        </div>
      </div>
      
      <!-- Logs Drawer -->
      <div class="logs-drawer" :class="{ collapsed: activeDrawer !== 'logs' }">
        <div 
          class="resize-handle"
          :class="{ dragging: isResizing && resizingDrawer === 'logs' }"
          @mousedown="startResize('logs', $event)"
        ></div>
        <div class="drawer-content">
          <div class="logs-panel">
            <div class="logs-header">
              <h3>Execution Logs</h3>
              <button class="clear-btn" @click="clearLogs">Clear</button>
            </div>
            <div class="logs-list" ref="logsListRef">
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
        </div>
      </div>
      
      <!-- Output Drawer -->
      <div class="output-drawer" :class="{ collapsed: activeDrawer !== 'output' }">
        <div 
          class="resize-handle"
          :class="{ dragging: isResizing && resizingDrawer === 'output' }"
          @mousedown="startResize('output', $event)"
        ></div>
        <div class="drawer-content">
          <div class="output-panel">
            <div class="output-header">
              <h3>Execution Output</h3>
              <div class="output-actions">
                <button class="copy-btn" @click="copyOutput">Copy</button>
                <button class="edit-btn" @click="showEditDialog = true">Edit</button>
              </div>
            </div>
            <div class="output-content">
              {{ executionOutput }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <WorkflowTemplates
      v-if="showTemplates"
      @close="showTemplates = false"
      @apply="handleTemplateApply"
    />
    
    <ExecutionInputDialog
      v-if="showExecuteDialog"
      :default-instruction="inputNode?.config?.instruction || ''"
      :default-paper-ids="inputNode?.config?.paperIds || []"
      @confirm="handleExecuteConfirm"
      @cancel="showExecuteDialog = false"
    />
    
    <OutputEditDialog
      v-if="showEditDialog"
      :model-value="executionOutput || ''"
      @close="showEditDialog = false"
    />
    
    <div v-if="showTemplates || showExecuteDialog" class="modal-overlay" @click="showExecuteDialog = false"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import WorkflowToolbar from './WorkflowToolbar.vue'
import NodePalette from './NodePalette.vue'
import WorkflowCanvas from './WorkflowCanvas.vue'
import CustomCanvas from './CustomCanvas.vue'
import NodeConfigPanel from './NodeConfigPanel.vue'
import ExecutionMonitor from './ExecutionMonitor.vue'
import WorkflowTemplates from './WorkflowTemplates.vue'
import ExecutionInputDialog from './ExecutionInputDialog.vue'
import OutputEditDialog from './OutputEditDialog.vue'
import { useWorkflow } from '@/composables/useWorkflow'
import type { WorkflowNodeType } from '@/types/workflow'

const {
  createNewWorkflow,
  addNode,
  selectNode,
  nodes,
  edges,
  executeWorkflow,
  stopExecution,
  error,
  updateNode,
  addEdge,
  deleteEdge,
  selectedNodeId,
  getAvailableAgents,
  getAvailableSkills,
  executionLogs,
  executionOutput,
  clearExecutionLogs,
} = useWorkflow()

const props = defineProps<{
  activeView?: 'task' | 'workflow'
}>()

const emit = defineEmits<{
  (e: 'change-view', view: 'task' | 'workflow'): void
}>()

const useCustomCanvas = ref(true)
const canvasRef = ref<InstanceType<typeof WorkflowCanvas> | null>(null)
const customCanvasRef = ref<InstanceType<typeof CustomCanvas> | null>(null)
const monitorRef = ref<InstanceType<typeof ExecutionMonitor> | null>(null)
const showTemplates = ref(false)
const showExecuteDialog = ref(false)
const leftDrawerCollapsed = ref(false)
const activeDrawer = ref<'config' | 'logs' | 'output' | null>('config')
const rightDrawerWidth = ref(320)
const isResizing = ref(false)
const resizingDrawer = ref<'config' | 'logs' | 'output' | null>(null)
const availableAgents = ref<string[]>([])
const availableSkills = ref<string[]>([])
const showEditDialog = ref(false)
const logsListRef = ref<HTMLElement | null>(null)
const logsDrawerWidth = ref(320)
const outputDrawerWidth = ref(320)

function toggleDrawer(drawer: 'config' | 'logs' | 'output') {
  if (activeDrawer.value === drawer) {
    activeDrawer.value = null
  } else {
    activeDrawer.value = drawer
  }
}

onMounted(async () => {
  availableAgents.value = await getAvailableAgents()
  availableSkills.value = await getAvailableSkills()
})

const inputNode = computed(() => nodes.value.find(n => n.type === 'input'))

interface LogEntry {
  timestamp: Date
  nodeLabel: string
  level: 'info' | 'warn' | 'error'
  message: string
}

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

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function clearLogs() {
  clearExecutionLogs()
}

watch(executionLogs, () => {
  nextTick(() => {
    if (logsListRef.value) {
      logsListRef.value.scrollTop = logsListRef.value.scrollHeight
    }
  })
}, { deep: true })

async function copyOutput() {
  if (executionOutput.value) {
    try {
      await navigator.clipboard.writeText(executionOutput.value)
    } catch (e) {
      console.error('Failed to copy output:', e)
    }
  }
}

function startResize(drawer: 'config' | 'logs' | 'output', e: MouseEvent) {
  isResizing.value = true
  resizingDrawer.value = drawer
  const startX = e.clientX
  
  const getWidthRef = () => {
    switch (drawer) {
      case 'config': return rightDrawerWidth
      case 'logs': return logsDrawerWidth
      case 'output': return outputDrawerWidth
    }
  }
  
  const widthRef = getWidthRef()
  const startWidth = widthRef.value
  
  const onMouseMove = (e: MouseEvent) => {
    const delta = startX - e.clientX
    const newWidth = Math.min(600, Math.max(200, startWidth + delta))
    widthRef.value = newWidth
  }
  
  const onMouseUp = () => {
    isResizing.value = false
    resizingDrawer.value = null
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function handleNodeSelected(type: WorkflowNodeType) {
  if (useCustomCanvas.value) {
    const x = 200 + Math.random() * 200
    const y = 100 + Math.random() * 200
    addNode(type, { x, y })
  } else {
    const canvas = canvasRef.value?.$el?.querySelector('.canvas-area')
    if (canvas) {
      const rect = canvas.getBoundingClientRect()
      const x = rect.width / 2
      const y = rect.height / 2
      addNode(type, { x, y })
    }
  }
}

function handleCanvasNodeSelected(nodeId: string) {
  selectNode(nodeId)
}

function handleNodeSelect(nodeId: string) {
  selectNode(nodeId)
}

function handleNodeDrag(nodeId: string, position: { x: number; y: number }) {
  updateNode(nodeId, { position })
}

function handleNodeConfigUpdate(nodeId: string, key: string, value: any) {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    let processedValue = value
    
    if (key === 'paperIds' && typeof value === 'string') {
      processedValue = value
        .split(',')
        .map((id: string) => id.trim())
        .filter(Boolean)
    }
    
    updateNode(nodeId, {
      config: { ...node.config, [key]: processedValue }
    })
  }
}

function handleNodeLabelUpdate(nodeId: string, label: string) {
  updateNode(nodeId, { label })
}

function handleEdgeCreate(sourceId: string, targetId: string, sourcePort: string, targetPort: string) {
  addEdge(sourceId, targetId, sourcePort, targetPort)
}

function handleEdgeDelete(edgeId: string) {
  deleteEdge(edgeId)
}

function handleCanvasDoubleClick(_position: { x: number; y: number }) {
}

function handleNodeDrop(nodeType: string, position: { x: number; y: number }) {
  addNode(nodeType as WorkflowNodeType, position)
}

function handleEdgeSelected(_edgeId: string) {
}

function handleCanvasClick() {
}

function handleCenterView() {
  if (useCustomCanvas.value && customCanvasRef.value) {
    customCanvasRef.value.fitView()
  }
}

function handleSave() {
}

function handleLoad() {
}

function handleExecute() {
  if (!inputNode.value?.config?.instruction) {
    showExecuteDialog.value = true
    return
  }
  
  executeWorkflowInternal()
}

async function handleExecuteConfirm(input: { instruction: string; paperIds?: string[] }) {
  showExecuteDialog.value = false
  
  if (inputNode.value) {
    const { updateNodeConfig } = useWorkflow()
    updateNodeConfig(inputNode.value.id, {
      instruction: input.instruction,
      paperIds: input.paperIds,
    })
  }
  
  await nextTick()
  executeWorkflowInternal()
}

async function executeWorkflowInternal() {
  const instruction = inputNode.value?.config?.instruction
  const paperIds = inputNode.value?.config?.paperIds
  
  if (!instruction) {
    monitorRef.value?.addLog('System', 'error', 'No instruction provided')
    return
  }
  
  monitorRef.value?.addLog('System', 'info', 'Workflow execution started')
  
  const success = await executeWorkflow({ instruction, paperIds })
  
  if (success) {
    monitorRef.value?.addLog('System', 'info', 'Workflow execution completed')
  } else if (error.value) {
    monitorRef.value?.addLog('System', 'error', `Execution failed: ${error.value}`)
  }
}

function handleStop() {
  stopExecution()
  monitorRef.value?.addLog('System', 'warn', 'Workflow execution stopped')
}

function handleTemplateApply(templateId: string) {
  showTemplates.value = false
  monitorRef.value?.addLog('System', 'info', `Template applied: ${templateId}`)
}

function openTemplates() {
  showTemplates.value = true
}

onMounted(() => {
  createNewWorkflow()
})

defineExpose({
  openTemplates,
})
</script>

<style scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
}

.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.canvas-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.left-drawer,
.right-drawer {
  display: flex;
  background: var(--bg-secondary);
  border-color: var(--border-color);
  overflow: hidden;
}

.left-drawer {
  border-right: 1px solid var(--border-color);
  width: 260px;
  flex-shrink: 0;
}

.left-drawer.collapsed {
  width: 0;
}

.right-drawer {
  border-left: 1px solid var(--border-color);
  width: v-bind(rightDrawerWidth + 'px');
  min-width: 200px;
  max-width: 600px;
  flex-shrink: 0;
  position: relative;
}

.right-drawer.collapsed {
  width: 0;
  min-width: 0;
}

.logs-drawer,
.output-drawer {
  display: flex;
  background: var(--bg-secondary);
  border-color: var(--border-color);
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  border-left: 1px solid var(--border-color);
}

.logs-drawer {
  width: v-bind(logsDrawerWidth + 'px');
  min-width: 200px;
  max-width: 600px;
}

.output-drawer {
  width: v-bind(outputDrawerWidth + 'px');
  min-width: 200px;
  max-width: 600px;
}

.logs-drawer.collapsed,
.output-drawer.collapsed {
  width: 0;
  min-width: 0;
}

.logs-drawer:not(.collapsed),
.output-drawer:not(.collapsed) {
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
}

.right-drawer:not(.collapsed) .resize-handle,
.logs-drawer:not(.collapsed) .resize-handle,
.output-drawer:not(.collapsed) .resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: ew-resize;
  background: transparent;
  transition: background 0.2s;
  z-index: 10;
}

.right-drawer:not(.collapsed) .resize-handle:hover,
.right-drawer:not(.collapsed) .resize-handle.dragging,
.logs-drawer:not(.collapsed) .resize-handle:hover,
.logs-drawer:not(.collapsed) .resize-handle.dragging,
.output-drawer:not(.collapsed) .resize-handle:hover,
.output-drawer:not(.collapsed) .resize-handle.dragging {
  background: var(--primary-color);
}

.drawer-content {
  flex: 1;
  overflow: hidden;
  opacity: 1;
}

.left-drawer .drawer-content {
  padding: 12px;
}

.left-drawer.collapsed .drawer-content,
.right-drawer.collapsed .drawer-content,
.logs-drawer.collapsed .drawer-content,
.output-drawer.collapsed .drawer-content {
  opacity: 0;
  pointer-events: none;
}

.right-panel-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  padding: 16px;
  overflow-y: auto;
}

.logs-panel,
.output-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
}

.logs-panel .logs-header,
.output-panel .output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.logs-panel .logs-header h3,
.output-panel .output-header h3 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.logs-panel .clear-btn,
.output-panel .copy-btn,
.output-panel .edit-btn {
  padding: 4px 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.logs-panel .clear-btn:hover,
.output-panel .copy-btn:hover,
.output-panel .edit-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.output-panel .output-actions {
  display: flex;
  gap: 8px;
}

.output-panel .edit-btn {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3B82F6;
}

.logs-panel .logs-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
}

.logs-panel .logs-list::-webkit-scrollbar {
  width: 6px;
}

.logs-panel .logs-list::-webkit-scrollbar-track {
  background: transparent;
}

.logs-panel .logs-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.logs-panel .log-item {
  display: flex;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
}

.logs-panel .log-item:hover {
  background: var(--bg-tertiary);
}

.logs-panel .log-item.info {
  color: var(--text-primary);
}

.logs-panel .log-item.warn {
  color: #FBBF24;
}

.logs-panel .log-item.error {
  color: #EF4444;
}

.logs-panel .log-time {
  color: var(--text-muted);
  flex-shrink: 0;
}

.logs-panel .log-node {
  color: #8B5CF6;
  flex-shrink: 0;
}

.logs-panel .log-message {
  color: var(--text-secondary);
}

.logs-panel .logs-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.output-panel .output-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}
</style>
