<template>
  <div 
    class="custom-node"
    :class="{ 
      selected: isSelected,
      collapsed: collapsed,
      running: node.status === 'running',
      success: node.status === 'success',
      error: node.status === 'error'
    }"
    :style="nodeStyle"
    @mousedown="onNodeMouseDown"
  >
    <div class="node-header" :style="{ backgroundColor: headerColor }">
      <span class="node-icon">{{ typeInfo?.icon || '📦' }}</span>
      <span 
        v-if="!isEditingLabel" 
        class="node-title" 
        @dblclick="startEditLabel"
      >{{ node.label }}</span>
      <input
        v-if="isEditingLabel"
        ref="labelInput"
        v-model="editLabel"
        class="label-input"
        @blur="finishEditLabel"
        @keyup.enter="finishEditLabel"
        @click.stop
      />
      <button class="collapse-btn" @click.stop="toggleCollapse">
        {{ collapsed ? '▶' : '▼' }}
      </button>
    </div>
    
    <div class="node-body" v-show="!collapsed">
      <div class="inputs-section">
        <div v-for="port in node.inputs" :key="port.id" class="port-row input-row">
          <div 
            class="port input-port"
            :class="{ connected: port.connected, 'hover-valid': isHoverValid(port.id, 'input') }"
            :style="{ backgroundColor: getPortColor(port.dataType) }"
            :data-port-id="port.id"
            :data-node-id="node.id"
            :data-port-type="'input'"
            @mousedown.stop="onPortMouseDown(port, 'input', $event)"
            @mouseup.stop="onPortMouseUp(port, 'input')"
          ></div>
          <span class="port-label">{{ port.label }}</span>
        </div>
      </div>
      
      <div v-if="configFields.length > 0" class="config-section">
        <div v-for="field in configFields" :key="field.key" class="config-field">
          <label class="config-label">{{ field.label }}</label>
          <textarea
            v-if="field.type === 'textarea'"
            v-model="configValues[field.key]"
            class="config-textarea"
            :placeholder="field.placeholder"
            rows="2"
            @change="updateConfig(field.key, configValues[field.key])"
            @mousedown.stop
          ></textarea>
          <input
            v-else-if="field.type === 'text'"
            v-model="configValues[field.key]"
            type="text"
            class="config-input"
            :placeholder="field.placeholder"
            @change="updateConfig(field.key, configValues[field.key])"
            @mousedown.stop
          />
          <input
            v-else-if="field.type === 'number'"
            v-model.number="configValues[field.key]"
            type="number"
            class="config-input"
            :min="field.min"
            :max="field.max"
            @change="updateConfig(field.key, configValues[field.key])"
            @mousedown.stop
          />
          <select
            v-else-if="field.type === 'select'"
            v-model="configValues[field.key]"
            class="config-select"
            @change="updateConfig(field.key, configValues[field.key])"
            @mousedown.stop
          >
            <option value="">{{ field.placeholder || 'Select...' }}</option>
            <option v-for="opt in getSelectOptions(field)" :key="opt" :value="opt">
              {{ opt }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="outputs-section">
        <div v-for="port in node.outputs" :key="port.id" class="port-row output-row">
          <span class="port-label">{{ port.label }}</span>
          <div 
            class="port output-port"
            :class="{ connected: port.connected, 'hover-valid': isHoverValid(port.id, 'output') }"
            :style="{ backgroundColor: getPortColor(port.dataType) }"
            :data-port-id="port.id"
            :data-node-id="node.id"
            :data-port-type="'output'"
            @mousedown.stop="onPortMouseDown(port, 'output', $event)"
            @mouseup.stop="onPortMouseUp(port, 'output')"
          ></div>
        </div>
      </div>
    </div>
    
    <div class="collapsed-ports" v-if="collapsed">
      <div class="collapsed-inputs">
        <div 
          v-for="port in node.inputs" 
          :key="port.id"
          class="port collapsed-port input-port"
          :class="{ connected: port.connected, 'hover-valid': isHoverValid(port.id, 'input') }"
          :style="{ backgroundColor: getPortColor(port.dataType) }"
          :data-port-id="port.id"
          :data-node-id="node.id"
          :data-port-type="'input'"
          :title="port.label"
          @mousedown.stop="onPortMouseDown(port, 'input', $event)"
          @mouseup.stop="onPortMouseUp(port, 'input')"
        ></div>
      </div>
      <div class="collapsed-outputs">
        <div 
          v-for="port in node.outputs" 
          :key="port.id"
          class="port collapsed-port output-port"
          :class="{ connected: port.connected, 'hover-valid': isHoverValid(port.id, 'output') }"
          :style="{ backgroundColor: getPortColor(port.dataType) }"
          :data-port-id="port.id"
          :data-node-id="node.id"
          :data-port-type="'output'"
          :title="port.label"
          @mousedown.stop="onPortMouseDown(port, 'output', $event)"
          @mouseup.stop="onPortMouseUp(port, 'output')"
        ></div>
      </div>
    </div>
    
    <div v-if="node.status === 'running'" class="status-indicator running">
      <span class="spinner"></span>
    </div>
    <div v-else-if="node.status === 'success'" class="status-indicator success">✓</div>
    <div v-else-if="node.status === 'error'" class="status-indicator error">✗</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { WorkflowNode, Port, PortDataType, NodeConfigField } from '@/types/workflow'
import { getNodeTypeInfo, NODE_PORT_DEFINITIONS } from '@/types/workflow'

const props = defineProps<{
  node: WorkflowNode
  isSelected: boolean
  isHoverValidPort?: { portId: string; type: string } | null
  agents?: string[]
  skills?: string[]
}>()

const emit = defineEmits<{
  (e: 'select'): void
  (e: 'drag-start', event: MouseEvent): void
  (e: 'update:config', key: string, value: any): void
  (e: 'update:label', label: string): void
  (e: 'port-drag-start', port: Port, portType: string, event: MouseEvent): void
  (e: 'port-drag-end', port: Port, portType: string): void
  (e: 'toggle-collapse'): void
}>()

const collapsed = ref(false)
const isEditingLabel = ref(false)
const editLabel = ref('')
const labelInput = ref<HTMLInputElement | null>(null)
const configValues = ref<Record<string, any>>({})

const typeInfo = computed(() => getNodeTypeInfo(props.node.type))
const portDefs = computed(() => NODE_PORT_DEFINITIONS[props.node.type])
const configFields = computed(() => portDefs.value?.configFields || [])

const headerColor = computed(() => {
  const colors: Record<string, string> = {
    input: '#3B82F6',
    analyze: '#8B5CF6',
    decompose: '#F59E0B',
    agent: '#10B981',
    condition: '#EC4899',
    parallel: '#14B8A6',
    synthesize: '#6366F1',
    output: '#EF4444',
    tool: '#64748B',
    skill: '#F97316',
  }
  return colors[props.node.type] || '#6B7280'
})

const nodeStyle = computed(() => ({
  left: `${props.node.position.x}px`,
  top: `${props.node.position.y}px`,
}))

watch(() => props.node.config, (config) => {
  configValues.value = { ...config }
  if (Array.isArray(configValues.value.paperIds)) {
    configValues.value.paperIds = configValues.value.paperIds.join(', ')
  }
}, { immediate: true, deep: true })

function getPortColor(dataType: PortDataType): string {
  const colors: Record<PortDataType, string> = {
    text: '#3B82F6',
    data: '#8B5CF6',
    paper: '#10B981',
    analysis: '#F59E0B',
    task: '#EC4899',
    result: '#14B8A6',
    any: '#6B7280',
  }
  return colors[dataType] || colors.any
}

function isHoverValid(portId: string, type: string): boolean {
  if (!props.isHoverValidPort) return false
  return props.isHoverValidPort.portId === portId && props.isHoverValidPort.type === type
}

function getSelectOptions(field: NodeConfigField): string[] {
  if (field.key === 'agentId' && props.agents) {
    return props.agents
  }
  if (field.key === 'skillId' && props.skills) {
    return props.skills
  }
  return field.options || []
}

function onNodeMouseDown(event: MouseEvent) {
  if ((event.target as HTMLElement).closest('.port')) return
  if ((event.target as HTMLElement).closest('.config-section')) return
  emit('select')
  emit('drag-start', event)
}

function onPortMouseDown(port: Port, portType: string, event: MouseEvent) {
  emit('port-drag-start', port, portType, event)
}

function onPortMouseUp(port: Port, portType: string) {
  emit('port-drag-end', port, portType)
}

function toggleCollapse() {
  collapsed.value = !collapsed.value
  emit('toggle-collapse')
}

function startEditLabel() {
  isEditingLabel.value = true
  editLabel.value = props.node.label
  nextTick(() => {
    labelInput.value?.focus()
    labelInput.value?.select()
  })
}

function finishEditLabel() {
  if (editLabel.value.trim() && editLabel.value !== props.node.label) {
    emit('update:label', editLabel.value.trim())
  }
  isEditingLabel.value = false
}

function updateConfig(key: string, value: any) {
  emit('update:config', key, value)
}
</script>

<style scoped>
.custom-node {
  position: absolute;
  min-width: 180px;
  max-width: 280px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 12px;
  user-select: none;
  z-index: 1;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.custom-node.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.custom-node.running {
  border-color: #3B82F6;
}

.custom-node.success {
  border-color: #10B981;
}

.custom-node.error {
  border-color: #EF4444;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 6px 6px 0 0;
  cursor: move;
  color: white;
  font-weight: 500;
  gap: 6px;
}

.collapsed .node-header {
  border-radius: 6px;
}

.node-icon {
  font-size: 14px;
}

.node-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.label-input {
  flex: 1;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.collapse-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 0;
  font-size: 10px;
  line-height: 1;
}

.collapse-btn:hover {
  color: white;
}

.node-body {
  padding: 8px;
}

.inputs-section,
.outputs-section {
  margin-bottom: 4px;
}

.port-row {
  display: flex;
  align-items: center;
  padding: 3px 0;
  position: relative;
}

.output-row {
  justify-content: flex-end;
}

.port {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: crosshair;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 2px solid var(--bg-secondary);
}

.port:hover {
  transform: scale(1.3);
  box-shadow: 0 0 6px currentColor;
}

.port.connected {
  box-shadow: 0 0 4px currentColor;
}

.port.hover-valid {
  transform: scale(1.5);
  box-shadow: 0 0 8px currentColor;
}

.input-port {
  position: absolute;
  left: -6px;
}

.output-port {
  position: absolute;
  right: -6px;
}

.port-label {
  font-size: 11px;
  color: var(--text-secondary);
  padding: 0 16px;
}

.config-section {
  margin: 8px 0;
  padding: 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.config-field {
  margin-bottom: 8px;
}

.config-field:last-child {
  margin-bottom: 0;
}

.config-label {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-input,
.config-textarea,
.config-select {
  width: 100%;
  padding: 6px 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 11px;
  font-family: inherit;
}

.config-input:focus,
.config-textarea:focus,
.config-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.config-textarea {
  resize: vertical;
  min-height: 40px;
}

.config-select {
  cursor: pointer;
}

.status-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.status-indicator.running {
  background: #3B82F6;
  color: white;
}

.status-indicator.success {
  background: #10B981;
  color: white;
}

.status-indicator.error {
  background: #EF4444;
  color: white;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.collapsed-ports {
  position: relative;
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  min-height: 18px;
}

.collapsed-inputs,
.collapsed-outputs {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.collapsed-port {
  width: 10px;
  height: 10px;
  border: 2px solid var(--bg-secondary);
  position: static;
}

.collapsed-inputs {
  position: absolute;
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
}

.collapsed-outputs {
  position: absolute;
  right: -5px;
  top: 50%;
  transform: translateY(-50%);
}
</style>
