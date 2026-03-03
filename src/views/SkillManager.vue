<template>
  <div class="skill-manager">
    <div class="page-header">
      <div class="header-content">
        <h1>Skills Management</h1>
        <p class="subtitle">Manage and execute dynamic skills</p>
      </div>
      <div class="header-actions">
        <button @click="reloadAllSkillsHandler" class="btn secondary" :disabled="isReloading">
          <svg v-if="isReloading" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
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
        @select="selectSkill"
        @execute="selectSkill"
        @detail="showSkillDetail"
        @edit="editSkill"
        @reload="reloadSkillHandler"
      />
    </div>
    
    <SkillDetailModal
      :skill="isModalOpen('detail') ? detailSkill : null"
      @close="closeDetailModal"
      @execute="executeFromDetail"
    />
    
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
      <button @click="notification = null" class="close-btn">×</button>
    </div>
    
    <div v-if="isModalOpen('execute')" class="modal-overlay" @click.self="executing ? null : closeExecuteModal">
      <div class="modal-content" @click.stop>
        <SkillForm
          v-if="selectedSkill"
          :skill="selectedSkill"
          :is-executing="executing"
          :result="skillResult"
          @submit="handleExecute"
          @cancel="closeExecuteModal"
          @clear-result="clearSkillResult"
        />
      </div>
    </div>
    
    <div v-if="isModalOpen('edit')" class="modal-overlay" @click="closeEditModal">
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
          <button @click="saveSkill" class="save-btn" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save & Reload' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import SkillCard from '@/components/skills/SkillCard.vue'
import SkillForm from '@/components/skills/SkillForm.vue'
import SkillDetailModal from '@/components/skills/SkillDetailModal.vue'
import type { Skill } from '@/types/skill'
import { useSkills } from '@/composables/useSkills'
import { useModals } from '@/composables/useModal'

const { 
  loading, 
  executing,
  saving,
  loadSkills, 
  executeSkill, 
  reloadSkill, 
  reloadAllSkills,
  getSkillsByCategory,
  getSkillRaw,
  saveSkillContent
} = useSkills()

const { open: openModal, close: closeModal, isOpen: isModalOpen } = useModals(['execute', 'edit', 'detail'] as const)

const isReloading = ref(false)
const activeFilter = ref('all')
const notification = ref<{ type: string; message: string } | null>(null)

const selectedSkill = ref<Skill | null>(null)
const detailSkill = ref<Skill | null>(null)
const editingSkill = ref<Skill | null>(null)
const editingContent = ref('')
const skillResult = ref<any>(null)

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
  return getSkillsByCategory(activeFilter.value)
})

const getSkillCount = (filter: string) => {
  const filtered = getSkillsByCategory(filter)
  return filtered.length
}

const reloadAllSkillsHandler = async () => {
  isReloading.value = true
  try {
    const result = await reloadAllSkills()
    if (result.loaded > 0) {
      showNotification('success', `Reloaded ${result.loaded} skills`)
    } else {
      showNotification('error', result.message || 'Failed to reload skills')
    }
  } catch (error) {
    showNotification('error', 'Failed to reload skills')
  } finally {
    isReloading.value = false
  }
}

const selectSkill = (skill: Skill) => {
  selectedSkill.value = skill
  openModal('execute')
}

const showSkillDetail = (skill: Skill) => {
  detailSkill.value = skill
  openModal('detail')
}

const closeDetailModal = () => {
  closeModal('detail')
  detailSkill.value = null
}

const executeFromDetail = () => {
  if (!detailSkill.value) return
  selectedSkill.value = detailSkill.value
  closeDetailModal()
  openModal('execute')
}

const closeExecuteModal = () => {
  closeModal('execute')
  selectedSkill.value = null
  skillResult.value = null
}

const clearSkillResult = () => {
  skillResult.value = null
}

const handleExecute = async (paperIds: string[], params: Record<string, unknown>) => {
  if (!selectedSkill.value) return
  
  skillResult.value = null
  
  try {
    const result = await executeSkill({
      skillId: selectedSkill.value.id,
      paperIds,
      params
    })
    
    if (result && result.success) {
      showNotification('success', `Skill "${selectedSkill.value.name}" executed successfully`)
      skillResult.value = result.result || result
    } else {
      const errorMsg = result?.error || 'Execution failed'
      showNotification('error', errorMsg)
      skillResult.value = { error: errorMsg }
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Failed to execute skill'
    showNotification('error', errorMsg)
    skillResult.value = { error: errorMsg }
  }
}

const editSkill = async (skill: Skill) => {
  editingSkill.value = skill
  
  const result = await getSkillRaw(skill.id)
  if (result) {
    editingContent.value = result.content
    openModal('edit')
  } else {
    showNotification('error', 'Failed to load skill content')
  }
}

const closeEditModal = () => {
  closeModal('edit')
  editingSkill.value = null
  editingContent.value = ''
}

const saveSkill = async () => {
  if (!editingSkill.value) return
  
  const result = await saveSkillContent(editingSkill.value.id, editingContent.value)
  if (result.success) {
    showNotification('success', 'Skill saved and reloaded')
    closeEditModal()
  } else {
    showNotification('error', result.message || 'Failed to save skill')
  }
}

const reloadSkillHandler = async (skill: Skill) => {
  try {
    const result = await reloadSkill(skill.id)
    if (result.success) {
      showNotification('success', `Skill ${skill.id} reloaded`)
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
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  max-width: 500px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn.secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn.secondary:hover:not(:disabled) {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  border-color: #00BCD4;
  color: var(--text-primary);
}

.filter-btn.active {
  background: #00BCD4;
  border-color: #00BCD4;
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
  background: #00BCD4;
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
  border-color: #00BCD4;
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
  background: #00BCD4;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.execute-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #00BCD4;
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
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.skill-source.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}
</style>
