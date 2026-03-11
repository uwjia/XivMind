<template>
  <div class="node-palette">
    <div class="palette-header">
      <h3>Nodes</h3>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search nodes..."
        class="search-input"
      />
    </div>
    
    <div class="node-categories">
      <div
        v-for="category in categories"
        :key="category.name"
        class="category-section"
      >
        <h4 class="category-title">{{ category.name }}</h4>
        <div class="node-list">
          <div
            v-for="nodeType in category.nodes"
            :key="nodeType.type"
            class="node-item"
            draggable="true"
            @dragstart="handleDragStart($event, nodeType.type)"
            @click="handleClick(nodeType.type)"
          >
            <span class="node-icon" :style="{ color: nodeType.color }">
              {{ nodeType.icon }}
            </span>
            <div class="node-info">
              <span class="node-label">{{ nodeType.label }}</span>
              <span class="node-desc">{{ nodeType.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NODE_TYPES, type WorkflowNodeType } from '@/types/workflow'

const searchQuery = ref('')

const emit = defineEmits<{
  (e: 'node-selected', type: WorkflowNodeType): void
}>()

const filteredNodeTypes = computed(() => {
  if (!searchQuery.value) return NODE_TYPES
  
  const query = searchQuery.value.toLowerCase()
  return NODE_TYPES.filter(
    node => 
      node.label.toLowerCase().includes(query) ||
      node.description.toLowerCase().includes(query)
  )
})

const categories = computed(() => {
  const basicNodes = filteredNodeTypes.value.filter(
    n => ['input', 'output', 'agent'].includes(n.type)
  )
  const flowNodes = filteredNodeTypes.value.filter(
    n => ['condition', 'parallel', 'synthesize'].includes(n.type)
  )
  const toolNodes = filteredNodeTypes.value.filter(
    n => ['tool', 'skill', 'analyze', 'decompose'].includes(n.type)
  )
  
  return [
    { name: 'Basic', nodes: basicNodes },
    { name: 'Flow Control', nodes: flowNodes },
    { name: 'Tools & Skills', nodes: toolNodes },
  ].filter(c => c.nodes.length > 0)
})

function handleDragStart(event: DragEvent, nodeType: WorkflowNodeType) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('nodeType', nodeType)
    event.dataTransfer.effectAllowed = 'copy'
  }
}

function handleClick(nodeType: WorkflowNodeType) {
  emit('node-selected', nodeType)
}
</script>

<style scoped>
.node-palette {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.palette-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.palette-header h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.search-input:focus {
  outline: none;
  border-color: #8B5CF6;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.node-categories {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.node-categories::-webkit-scrollbar {
  display: none;
}

.category-section {
  margin-bottom: 16px;
}

.category-title {
  margin: 0 0 8px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s ease;
}

.node-item:hover {
  border-color: #8B5CF6;
  background: var(--bg-tertiary);
}

.node-item:active {
  cursor: grabbing;
}

.node-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.node-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

.node-desc {
  font-size: 0.7rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
