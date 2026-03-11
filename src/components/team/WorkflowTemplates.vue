<template>
  <div class="workflow-templates">
    <div class="templates-header">
      <h3>Templates</h3>
      <button class="close-btn" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
    
    <div class="templates-content">
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat"
          :class="['tab-btn', { active: selectedCategory === cat }]"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
      
      <div class="templates-list">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          @click="applyTemplate(template.id)"
        >
          <div class="template-preview">
            <div class="preview-nodes">
              <div
                v-for="(node, index) in template.nodes.slice(0, 5)"
                :key="index"
                class="preview-node"
                :style="{
                  left: `${(node.position.x / 900) * 100}%`,
                  top: `${(node.position.y / 400) * 100}%`,
                  backgroundColor: getNodeColor(node.type),
                }"
              ></div>
            </div>
          </div>
          <div class="template-info">
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
            <div class="template-meta">
              <span>{{ template.nodes.length }} nodes</span>
              <span>{{ template.edges.length }} connections</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWorkflow } from '@/composables/useWorkflow'
import { getNodeTypeInfo } from '@/types/workflow'

const { applyTemplate: apply, getTemplates } = useWorkflow()

const selectedCategory = ref('All')

const templates = computed(() => getTemplates())

const categories = computed(() => {
  const cats = new Set(['All'])
  templates.value.forEach(t => cats.add(t.category))
  return Array.from(cats)
})

const filteredTemplates = computed(() => {
  if (selectedCategory.value === 'All') {
    return templates.value
  }
  return templates.value.filter(t => t.category === selectedCategory.value)
})

function getNodeColor(type: string): string {
  const info = getNodeTypeInfo(type as any)
  return info?.color || '#6B7280'
}

function applyTemplate(templateId: string) {
  apply(templateId)
  emit('apply', templateId)
}

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'apply', templateId: string): void
}>()
</script>

<style scoped>
.workflow-templates {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.templates-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.templates-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-tertiary);
}

.close-btn svg {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.templates-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--bg-tertiary);
}

.tab-btn.active {
  background: #8B5CF6;
  border-color: #8B5CF6;
  color: white;
}

.templates-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.template-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-card:hover {
  border-color: #8B5CF6;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.2);
}

.template-preview {
  height: 100px;
  background: var(--bg-tertiary);
  position: relative;
  overflow: hidden;
}

.preview-nodes {
  position: absolute;
  inset: 10px;
}

.preview-node {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  opacity: 0.8;
}

.template-info {
  padding: 12px;
}

.template-info h4 {
  margin: 0 0 4px 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.template-info p {
  margin: 0 0 8px 0;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 12px;
  font-size: 0.7rem;
  color: var(--text-secondary);
}
</style>
