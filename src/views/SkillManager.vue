<template>
  <div class="skill-manager">
    <div class="page-header">
      <h1>Skills Management</h1>
      <p class="subtitle">Manage and execute dynamic skills</p>
      <div class="header-actions">
        <button @click="reloadAllSkills" class="reload-btn" :disabled="isReloading">
          <svg v-if="isReloading" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M23 4v6h-6"/>
            <path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          <span>Reload All</span>
        </button>
      </div>
    </div>
    
    <div class="filters">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        :class="['filter-btn', { active: activeFilter === cat.value }]"
        @click="activeFilter = cat.value"
      >
        {{ cat.label }}
        <span class="count">{{ getSkillCount(cat.value) }}</span>
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
      </svg>
      <span>Loading skills...</span>
    </div>
    
    <div v-else-if="filteredSkills.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4"/>
        <path d="M12 8h.01"/>
      </svg>
      <h3>No skills found</h3>
      <p>No skills match the current filter.</p>
    </div>
    
    <div v-else class="skills-grid">
      <SkillCard
        v-for="skill in filteredSkills"
        :key="skill.id"
        :skill="skill"
        :show-actions="true"
        :selected="selectedSkill?.id === skill.id"
        @select="showSkillDetail"
        @execute="executeSkill"
        @edit="editSkill"
        @reload="reloadSkill"
      />
    </div>
    
    <div v-if="showDetailModal && detailSkill" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content detail-modal" @click.stop>
        <div class="modal-header">
          <div class="detail-header">
            <h3>{{ detailSkill.name }}</h3>
            <div class="detail-meta">
              <span class="skill-category">{{ detailSkill.category }}</span>
              <span 
                v-if="detailSkill.source === 'dynamic'" 
                class="skill-source dynamic"
              >
                Dynamic
              </span>
              <span v-else class="skill-source builtin">Built-in</span>
            </div>
          </div>
          <button @click="closeDetailModal" class="close-btn">×</button>
        </div>
        <div class="detail-body">
          <div class="detail-section">
            <h4>Description</h4>
            <p>{{ detailSkill.description }}</p>
          </div>
          
          <div v-if="detailSkill.requires_paper" class="detail-section">
            <h4>Requirements</h4>
            <div class="requirement-tag">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              Requires Paper ID
            </div>
          </div>
          
          <div v-if="detailSkill.input_schema" class="detail-section">
            <h4>Parameters</h4>
            <div class="params-list">
              <div 
                v-for="(prop, key) in detailSkill.input_schema.properties" 
                :key="key" 
                class="param-item"
              >
                <span class="param-name">{{ key }}</span>
                <span class="param-type">{{ prop.type }}</span>
                <span v-if="detailSkill.input_schema.required?.includes(key)" class="param-required">required</span>
                <span v-if="prop.description" class="param-desc">{{ prop.description }}</span>
                <span v-if="prop.default" class="param-default">default: {{ prop.default }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeDetailModal" class="cancel-btn">Close</button>
          <button 
            @click="executeFromDetail" 
            class="execute-btn"
            :disabled="!detailSkill.available"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Execute
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
      <button @click="notification = null" class="close-btn">×</button>
    </div>
    
    <div v-if="showExecuteModal" class="modal-overlay" @click.self="isExecuting ? null : closeExecuteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedSkill?.name }}</h3>
          <button @click="closeExecuteModal" class="close-btn" :disabled="isExecuting">×</button>
        </div>
        <SkillForm
          v-if="selectedSkill"
          :skill="selectedSkill"
          :is-executing="isExecuting"
          @submit="handleExecute"
          @cancel="closeExecuteModal"
        />
      </div>
    </div>
    
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content editor-modal" @click.stop>
        <div class="modal-header">
          <h3>Edit: {{ editingSkill?.id }}</h3>
          <button @click="closeEditModal" class="close-btn">×</button>
        </div>
        <div class="editor-container">
          <textarea
            v-model="editingContent"
            class="skill-editor"
            spellcheck="false"
          />
        </div>
        <div class="modal-actions">
          <button @click="closeEditModal" class="cancel-btn">Cancel</button>
          <button @click="saveSkill" class="save-btn" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save & Reload' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { skillsAPI } from '../services/skills'
import SkillCard from '../components/skills/SkillCard.vue'
import SkillForm from '../components/skills/SkillForm.vue'
import type { Skill } from '../types/skill'
import { useLLMStore } from '../stores/llm-store'

const llmStore = useLLMStore()

const skills = ref<Skill[]>([])
const loading = ref(true)
const isReloading = ref(false)
const isSaving = ref(false)
const activeFilter = ref('all')
const notification = ref<{ type: string; message: string } | null>(null)

const selectedSkill = ref<Skill | null>(null)
const showExecuteModal = ref(false)
const isExecuting = ref(false)

const detailSkill = ref<Skill | null>(null)
const showDetailModal = ref(false)

const editingSkill = ref<Skill | null>(null)
const editingContent = ref('')
const showEditModal = ref(false)

const showNotification = (type: string, message: string) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

const categories = [
  { value: 'all', label: 'All' },
  { value: 'analysis', label: 'Analysis' },
  { value: 'writing', label: 'Writing' },
  { value: 'search', label: 'Search' },
  { value: 'dynamic', label: 'Dynamic' },
  { value: 'builtin', label: 'Built-in' },
]

const filteredSkills = computed(() => {
  if (activeFilter.value === 'all') return skills.value
  if (activeFilter.value === 'dynamic') {
    return skills.value.filter(s => s.source === 'dynamic')
  }
  if (activeFilter.value === 'builtin') {
    return skills.value.filter(s => s.source !== 'dynamic')
  }
  return skills.value.filter(s => s.category === activeFilter.value)
})

const getSkillCount = (filter: string) => {
  if (filter === 'all') return skills.value.length
  if (filter === 'dynamic') {
    return skills.value.filter(s => s.source === 'dynamic').length
  }
  if (filter === 'builtin') {
    return skills.value.filter(s => s.source !== 'dynamic').length
  }
  return skills.value.filter(s => s.category === filter).length
}

const loadSkills = async () => {
  loading.value = true
  try {
    const result = await skillsAPI.getSkills()
    skills.value = result.skills || []
  } catch (error) {
    showNotification('error', 'Failed to load skills')
  } finally {
    loading.value = false
  }
}

const reloadAllSkills = async () => {
  isReloading.value = true
  try {
    const result = await skillsAPI.reloadSkills()
    showNotification('success', `Reloaded ${result.loaded} skills`)
    await loadSkills()
  } catch (error) {
    showNotification('error', 'Failed to reload skills')
  } finally {
    isReloading.value = false
  }
}

const executeSkill = (skill: Skill) => {
  selectedSkill.value = skill
  showExecuteModal.value = true
}

const showSkillDetail = (skill: Skill) => {
  detailSkill.value = skill
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  detailSkill.value = null
}

const executeFromDetail = () => {
  if (!detailSkill.value) return
  selectedSkill.value = detailSkill.value
  closeDetailModal()
  showExecuteModal.value = true
}

const closeExecuteModal = () => {
  showExecuteModal.value = false
  selectedSkill.value = null
}

const handleExecute = async (paperIds: string[], params: Record<string, unknown>) => {
  if (!selectedSkill.value) return
  
  isExecuting.value = true
  try {
    const result = await skillsAPI.executeSkill(
      selectedSkill.value.id,
      paperIds,
      params,
      llmStore.selectedProvider || undefined,
      llmStore.selectedModel || undefined
    )
    
    if (result.success) {
      showNotification('success', `Skill "${selectedSkill.value.name}" executed successfully`)
    } else {
      showNotification('error', result.error || 'Execution failed')
    }
  } catch (error) {
    showNotification('error', 'Failed to execute skill')
  } finally {
    isExecuting.value = false
    closeExecuteModal()
  }
}

const editSkill = async (skill: Skill) => {
  editingSkill.value = skill
  
  try {
    const result = await skillsAPI.getSkillRaw(skill.id)
    editingContent.value = result.content
    showEditModal.value = true
  } catch (error) {
    showNotification('error', 'Failed to load skill content')
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingSkill.value = null
  editingContent.value = ''
}

const saveSkill = async () => {
  if (!editingSkill.value) return
  
  isSaving.value = true
  try {
    const result = await skillsAPI.saveSkill(editingSkill.value.id, editingContent.value)
    if (result.success) {
      showNotification('success', 'Skill saved and reloaded')
      closeEditModal()
      await loadSkills()
    } else {
      showNotification('error', result.message || 'Failed to save skill')
    }
  } catch (error) {
    showNotification('error', 'Failed to save skill')
  } finally {
    isSaving.value = false
  }
}

const reloadSkill = async (skill: Skill) => {
  try {
    const result = await skillsAPI.reloadSkill(skill.id)
    if (result.success) {
      showNotification('success', `Skill ${skill.id} reloaded`)
      await loadSkills()
    } else {
      showNotification('error', result.message || 'Failed to reload')
    }
  } catch (error) {
    showNotification('error', 'Failed to reload skill')
  }
}

onMounted(loadSkills)
</script>

<style scoped>
.skill-manager {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.reload-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.reload-btn:hover:not(:disabled) {
  border-color: #10B981;
  color: #10B981;
}

.reload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reload-btn svg {
  width: 18px;
  height: 18px;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.filters {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #10B981;
  color: var(--text-primary);
}

.filter-btn.active {
  background: #10B981;
  border-color: #10B981;
  color: white;
}

.filter-btn .count {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.75rem;
}

.filter-btn.active .count {
  background: rgba(255, 255, 255, 0.2);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.loading-state svg,
.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 1.2rem;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-state p {
  margin: 0;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification.success {
  background: #10B981;
  color: white;
}

.notification.error {
  background: #EF4444;
  color: white;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
}

.editor-modal {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.modal-header .close-btn {
  color: var(--text-muted);
  font-size: 1.5rem;
}

.editor-container {
  padding: 20px;
}

.skill-editor {
  width: 100%;
  min-height: 400px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  resize: vertical;
}

.skill-editor:focus {
  outline: none;
  border-color: #10B981;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.cancel-btn {
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
}

.save-btn {
  padding: 10px 20px;
  background: #10B981;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.detail-modal {
  max-width: 600px;
}

.detail-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-header h3 {
  margin: 0;
}

.detail-meta {
  display: flex;
  gap: 8px;
}

.detail-body {
  padding: 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

.detail-section p {
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

.requirement-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  border-radius: 6px;
  font-size: 0.85rem;
}

.requirement-tag svg {
  width: 16px;
  height: 16px;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.param-name {
  font-weight: 600;
  color: var(--text-primary);
  font-family: monospace;
}

.param-type {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.param-required {
  padding: 2px 6px;
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.param-desc {
  flex-basis: 100%;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.param-default {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: monospace;
}

.execute-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #10B981;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background: #059669;
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.execute-btn svg {
  width: 16px;
  height: 16px;
}

.skill-category {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  color: var(--text-muted);
  text-transform: capitalize;
}

.skill-source {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}

.skill-source.dynamic {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.skill-source.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}
</style>
