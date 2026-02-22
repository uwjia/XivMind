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
        @execute="executeSkill"
        @edit="editSkill"
        @reload="reloadSkill"
      />
    </div>
    
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
      <button @click="notification = null" class="close-btn">×</button>
    </div>
    
    <div v-if="showExecuteModal" class="modal-overlay" @click="closeExecuteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedSkill?.name }}</h3>
          <button @click="closeExecuteModal" class="close-btn">×</button>
        </div>
        <SkillForm
          v-if="selectedSkill"
          :skill="selectedSkill"
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

const editingSkill = ref<Skill | null>(null)
const editingContent = ref('')
const showEditModal = ref(false)

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

const closeExecuteModal = () => {
  showExecuteModal.value = false
  selectedSkill.value = null
}

const handleExecute = async (paperIds: string[], params: Record<string, unknown>) => {
  if (!selectedSkill.value) return
  
  try {
    const result = await skillsAPI.executeSkill(
      selectedSkill.value.id,
      paperIds,
      params,
      llmStore.selectedProvider || undefined,
      llmStore.selectedModel || undefined
    )
    
    if (result.success) {
      showNotification('success', `Skill executed successfully`)
    } else {
      showNotification('error', result.error || 'Execution failed')
    }
  } catch (error) {
    showNotification('error', 'Failed to execute skill')
  }
  
  closeExecuteModal()
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
    await skillsAPI.reloadSkill(editingSkill.value.id)
    showNotification('success', 'Skill saved and reloaded')
    closeEditModal()
    await loadSkills()
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

const showNotification = (type: string, message: string) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
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
</style>
