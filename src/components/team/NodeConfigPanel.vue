<template>
  <div class="node-config-panel">
    <div v-if="!selectedNode" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M3 9h18"/>
        <path d="M9 21V9"/>
      </svg>
      <span>Select a node to configure</span>
    </div>
    
    <template v-else>
      <div class="panel-header">
        <span class="node-type-icon" :style="{ color: nodeTypeInfo?.color }">
          {{ nodeTypeInfo?.icon }}
        </span>
        <div class="header-info">
          <h3>{{ selectedNode.label }}</h3>
          <span class="node-type">{{ nodeTypeInfo?.description }}</span>
        </div>
      </div>
      
      <div class="panel-content">
        <div class="config-section">
          <label>Label</label>
          <input
            v-model="nodeLabel"
            type="text"
            placeholder="Node label"
            @change="updateLabel"
          />
        </div>
        
        <div v-if="selectedNode.type === 'agent'" class="config-section">
          <label>Agent</label>
          <select v-model="agentId" @change="updateConfig">
            <option value="">Select an agent...</option>
            <option v-for="agent in availableAgents" :key="agent" :value="agent">
              {{ agent }}
            </option>
          </select>
        </div>
        
        <div v-if="selectedNode.type === 'agent'" class="config-section">
          <label>Instruction</label>
          <textarea
            v-model="agentInstruction"
            placeholder="Enter specific instruction for this agent... (optional, uses workflow input if empty)"
            rows="3"
            @change="updateConfig"
          ></textarea>
          <span class="hint">Optional: Override the workflow instruction for this agent</span>
        </div>
        
        <div v-if="selectedNode.type === 'skill'" class="config-section">
          <label>Skill</label>
          <select v-model="skillId" @change="updateConfig">
            <option value="">Select a skill...</option>
            <option v-for="skill in availableSkills" :key="skill" :value="skill">
              {{ skill }}
            </option>
          </select>
        </div>
        
        <div v-if="selectedNode.type === 'condition'" class="config-section">
          <label>Condition</label>
          <textarea
            v-model="condition"
            placeholder="e.g., complexity == 'high'"
            rows="3"
            @change="updateConfig"
          ></textarea>
          <span class="hint">JavaScript expression evaluated at runtime</span>
        </div>
        
        <div v-if="selectedNode.type === 'input'" class="config-section">
          <label>Instruction</label>
          <textarea
            v-model="inputInstruction"
            placeholder="Enter your task instruction... e.g., 'Summarize paper 2401.12345'"
            rows="4"
            @change="updateConfig"
          ></textarea>
          <span class="hint">The main task instruction for the workflow</span>
        </div>
        
        <div v-if="selectedNode.type === 'input'" class="config-section">
          <label>Paper IDs (optional)</label>
          <input
            v-model="inputPaperIds"
            type="text"
            placeholder="e.g., 2401.12345, 2401.67890"
            @change="updateConfig"
          />
          <span class="hint">Comma-separated list of paper IDs</span>
        </div>
        
        <div v-if="nodeTypeInfo?.configurable" class="config-section">
          <label>Timeout (seconds)</label>
          <input
            v-model.number="timeout"
            type="number"
            min="10"
            max="600"
            @change="updateConfig"
          />
        </div>
        
        <div v-if="nodeTypeInfo?.configurable" class="config-section">
          <label>Max Retries</label>
          <input
            v-model.number="maxRetries"
            type="number"
            min="0"
            max="5"
            @change="updateConfig"
          />
        </div>
        
        <div class="config-section status-section">
          <label>Status</label>
          <div class="status-display">
            <span 
              class="status-indicator"
              :style="{ backgroundColor: statusColor }"
            ></span>
            <span class="status-text">{{ selectedNode.status }}</span>
          </div>
        </div>
        
        <NodePreview 
          v-if="selectedNode.result || selectedNode.error" 
          :result="selectedNode.result"
          :error="selectedNode.error"
        />
        
        <div class="config-section connections-section">
          <label>Connections</label>
          <div class="connections-info">
            <div class="connection-group">
              <span class="connection-label">Inputs:</span>
              <span class="connection-count">{{ inputCount }}</span>
            </div>
            <div class="connection-group">
              <span class="connection-label">Outputs:</span>
              <span class="connection-count">{{ outputCount }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="panel-actions">
        <button class="btn danger" @click="deleteNode">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          Delete Node
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useWorkflow } from '@/composables/useWorkflow'
import { getNodeTypeInfo } from '@/types/workflow'
import NodePreview from '@/components/team/NodePreview.vue'

const {
  selectedNode,
  edges,
  updateNode,
  updateNodeConfig,
  deleteNode: removeNode,
  getAvailableAgents,
  getAvailableSkills,
} = useWorkflow()

const availableAgents = ref<string[]>([])
const availableSkills = ref<string[]>([])

const nodeLabel = ref('')
const agentId = ref('')
const agentInstruction = ref('')
const skillId = ref('')
const condition = ref('')
const inputInstruction = ref('')
const inputPaperIds = ref('')
const timeout = ref(300)
const maxRetries = ref(1)

const nodeTypeInfo = computed(() => 
  selectedNode.value ? getNodeTypeInfo(selectedNode.value.type) : null
)

const statusColor = computed(() => {
  const colors: Record<string, string> = {
    idle: '#6B7280',
    pending: '#FBBF24',
    running: '#3B82F6',
    success: '#10B981',
    error: '#EF4444',
  }
  return colors[selectedNode.value?.status || 'idle'] || '#6B7280'
})

const inputCount = computed(() => 
  selectedNode.value 
    ? edges.value.filter(e => e.target === selectedNode.value!.id).length 
    : 0
)

const outputCount = computed(() => 
  selectedNode.value 
    ? edges.value.filter(e => e.source === selectedNode.value!.id).length 
    : 0
)

watch(selectedNode, (node) => {
  if (node) {
    nodeLabel.value = node.label
    agentId.value = node.config.agentId || ''
    agentInstruction.value = node.config.instruction || ''
    skillId.value = node.config.skillId || ''
    condition.value = node.config.condition || ''
    inputInstruction.value = node.config.instruction || ''
    inputPaperIds.value = (node.config.paperIds || []).join(', ')
    timeout.value = node.config.timeout || 300
    maxRetries.value = node.config.maxRetries || 1
  }
}, { immediate: true })

function updateLabel() {
  if (selectedNode.value) {
    updateNode(selectedNode.value.id, { label: nodeLabel.value })
  }
}

function updateConfig() {
  if (selectedNode.value) {
    const paperIds = inputPaperIds.value
      .split(',')
      .map(id => id.trim())
      .filter(Boolean)
    
    const config: Record<string, unknown> = {
      agentId: agentId.value || undefined,
      skillId: skillId.value || undefined,
      condition: condition.value || undefined,
      paperIds: paperIds.length > 0 ? paperIds : undefined,
      timeout: timeout.value,
      maxRetries: maxRetries.value,
    }
    
    if (selectedNode.value.type === 'agent') {
      config.instruction = agentInstruction.value || undefined
    } else if (selectedNode.value.type === 'input') {
      config.instruction = inputInstruction.value || undefined
    }
    
    updateNodeConfig(selectedNode.value.id, config)
  }
}

function deleteNode() {
  if (selectedNode.value) {
    removeNode(selectedNode.value.id)
  }
}

async function loadOptions() {
  availableAgents.value = await getAvailableAgents()
  availableSkills.value = await getAvailableSkills()
}

loadOptions()
</script>

<style scoped>
.node-config-panel {
  width: 100%;
  min-height: 0;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex: 1;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

.empty-state span {
  font-size: 0.9rem;
  text-align: center;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.node-type-icon {
  font-size: 1.5rem;
}

.header-info h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.node-type {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.panel-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
}

.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: transparent;
}

.panel-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.config-section {
  margin-bottom: 16px;
}

.config-section label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.config-section input,
.config-section select,
.config-section textarea {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.config-section input:focus,
.config-section select:focus,
.config-section textarea:focus {
  outline: none;
  border-color: #8B5CF6;
}

.config-section textarea {
  resize: vertical;
  min-height: 60px;
  font-family: 'Fira Code', monospace;
}

.hint {
  display: block;
  margin-top: 4px;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.status-section .status-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-text {
  font-size: 0.85rem;
  color: var(--text-primary);
  text-transform: capitalize;
}

.connections-section .connections-info {
  display: flex;
  gap: 16px;
}

.connection-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.connection-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.connection-count {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-actions {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn.danger {
  background: transparent;
  border: 1px solid #EF4444;
  color: #EF4444;
}

.btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}
</style>
