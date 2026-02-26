<template>
  <div class="subagent-manager">
    <div class="page-header">
      <div class="header-content">
        <h1>SubAgents</h1>
        <p class="description">
          Multi-agent orchestration system for complex tasks. Each SubAgent operates in an isolated context with specialized capabilities.
        </p>
      </div>
      <div class="header-actions">
        <button class="btn secondary" @click="handleReloadAll" :disabled="loading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          Reload All
        </button>
        <button class="btn primary" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Create SubAgent
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-tabs">
        <button 
          v-for="tab in filterTabs" 
          :key="tab.value"
          class="filter-tab"
          :class="{ active: activeFilter === tab.value }"
          @click="activeFilter = tab.value"
        >
          {{ tab.label }}
          <span class="count">{{ getFilterCount(tab.value) }}</span>
        </button>
      </div>
      <div class="filter-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search SubAgents..."
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Loading SubAgents...</span>
    </div>

    <div v-else-if="filteredAgents.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="3" y="11" width="18" height="10" rx="2"/>
        <circle cx="12" cy="5" r="2"/>
        <path d="M12 7v4"/>
      </svg>
      <h3>No SubAgents Found</h3>
      <p>Create your first SubAgent to get started.</p>
      <button class="btn primary" @click="showCreateModal = true">
        Create SubAgent
      </button>
    </div>

    <div v-else class="agents-grid">
      <SubAgentCard
        v-for="agent in filteredAgents"
        :key="agent.id"
        :agent="agent"
        :show-actions="true"
        :selected="selectedAgent?.id === agent.id"
        @select="selectAgent"
        @execute="openExecuteModal"
        @edit="openEditModal"
        @reload="handleReload"
        @delete="handleDelete"
      />
    </div>

    <Teleport to="body">
      <div v-if="showExecuteModal" class="modal-overlay" @click.self="closeExecuteModal">
        <div class="modal-container execute-modal">
          <SubAgentForm
            v-if="selectedAgent"
            :agent="selectedAgent"
            :executing="executing"
            @execute="handleExecute"
            @cancel="closeExecuteModal"
          />
        </div>
      </div>

      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-container edit-modal">
          <SubAgentEditor
            v-if="selectedAgent"
            :agent-id="selectedAgent.id"
            @save="handleSave"
            @cancel="closeEditModal"
          />
        </div>
      </div>

      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
        <div class="modal-container create-modal">
          <div class="create-form">
            <div class="form-header">
              <h3>Create New SubAgent</h3>
            </div>
            <div class="form-body">
              <div class="form-group">
                <label for="newId">ID</label>
                <input 
                  id="newId" 
                  v-model="newAgent.id" 
                  type="text" 
                  placeholder="e.g., my-agent"
                />
              </div>
              <div class="form-group">
                <label for="newName">Name</label>
                <input 
                  id="newName" 
                  v-model="newAgent.name" 
                  type="text" 
                  placeholder="e.g., My Agent"
                />
              </div>
              <div class="form-group">
                <label for="newDesc">Description</label>
                <textarea 
                  id="newDesc" 
                  v-model="newAgent.description" 
                  placeholder="Describe what this agent does..."
                  rows="3"
                ></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label for="newSkills">Skills (comma separated)</label>
                  <input 
                    id="newSkills" 
                    v-model="newAgent.skillsStr" 
                    type="text" 
                    placeholder="summary, translation"
                  />
                </div>
                <div class="form-group">
                  <label for="newTools">Tools (comma separated)</label>
                  <input 
                    id="newTools" 
                    v-model="newAgent.toolsStr" 
                    type="text" 
                    placeholder="search_papers, get_paper_details"
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="newPrompt">System Prompt</label>
                <textarea 
                  id="newPrompt" 
                  v-model="newAgent.system_prompt" 
                  placeholder="You are a helpful assistant..."
                  rows="5"
                ></textarea>
              </div>
            </div>
            <div class="form-footer">
              <button class="btn secondary" @click="closeCreateModal">Cancel</button>
              <button 
                class="btn primary" 
                @click="handleCreate"
                :disabled="!newAgent.id || !newAgent.name"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showResultModal" class="modal-overlay" @click.self="closeResultModal">
        <div class="modal-container result-modal">
          <ExecutionResult
            v-if="executionResult"
            :result="executionResult"
            @close="closeResultModal"
          />
        </div>
      </div>
    </Teleport>

    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSubAgents } from '../composables/useSubAgents'
import SubAgentCard from '../components/subagents/SubAgentCard.vue'
import SubAgentForm from '../components/subagents/SubAgentForm.vue'
import SubAgentEditor from '../components/subagents/SubAgentEditor.vue'
import ExecutionResult from '../components/subagents/ExecutionResult.vue'
import type { SubAgent, SubAgentExecuteRequest } from '../types/subagent'

const {
  agents,
  loading,
  executing,
  selectedAgent,
  executionResult,
  activeFilter,
  allSkills,
  allTools,
  loadSubAgents,
  executeSubAgent,
  createSubAgent,
  reloadSubAgents,
  reloadSubAgent,
  deleteSubAgent,
  selectAgent,
} = useSubAgents()

const searchQuery = ref('')
const showExecuteModal = ref(false)
const showEditModal = ref(false)
const showCreateModal = ref(false)
const showResultModal = ref(false)
const notification = ref<{ type: string; message: string } | null>(null)

const newAgent = ref({
  id: '',
  name: '',
  description: '',
  skillsStr: '',
  toolsStr: '',
  system_prompt: '',
})

const filterTabs = computed(() => [
  { label: 'All', value: 'all' },
  { label: 'Built-in', value: 'builtin' },
  { label: 'Dynamic', value: 'dynamic' },
  ...allSkills.value.map(s => ({ label: `Skill: ${s}`, value: `skill:${s}` })),
  ...allTools.value.map(t => ({ label: `Tool: ${t}`, value: `tool:${t}` })),
])

const filteredAgents = computed(() => {
  let result = agents.value
  
  if (activeFilter.value !== 'all') {
    if (activeFilter.value === 'builtin') {
      result = result.filter(a => a.source === 'builtin')
    } else if (activeFilter.value === 'dynamic') {
      result = result.filter(a => a.source === 'dynamic')
    } else if (activeFilter.value.startsWith('skill:')) {
      const skill = activeFilter.value.slice(6)
      result = result.filter(a => a.skills.includes(skill))
    } else if (activeFilter.value.startsWith('tool:')) {
      const tool = activeFilter.value.slice(5)
      result = result.filter(a => a.tools.includes(tool))
    }
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(a => 
      a.name.toLowerCase().includes(query) ||
      a.description.toLowerCase().includes(query) ||
      a.id.toLowerCase().includes(query)
    )
  }
  
  return result
})

const getFilterCount = (filterValue: string): number => {
  if (filterValue === 'all') return agents.value.length
  if (filterValue === 'builtin') return agents.value.filter(a => a.source === 'builtin').length
  if (filterValue === 'dynamic') return agents.value.filter(a => a.source === 'dynamic').length
  if (filterValue.startsWith('skill:')) {
    const skill = filterValue.slice(6)
    return agents.value.filter(a => a.skills.includes(skill)).length
  }
  if (filterValue.startsWith('tool:')) {
    const tool = filterValue.slice(5)
    return agents.value.filter(a => a.tools.includes(tool)).length
  }
  return 0
}

const showNotification = (type: string, message: string) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

const openExecuteModal = (agent: SubAgent) => {
  selectAgent(agent)
  showExecuteModal.value = true
}

const closeExecuteModal = () => {
  showExecuteModal.value = false
}

const openEditModal = (agent: SubAgent) => {
  selectAgent(agent)
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const closeCreateModal = () => {
  showCreateModal.value = false
  newAgent.value = {
    id: '',
    name: '',
    description: '',
    skillsStr: '',
    toolsStr: '',
    system_prompt: '',
  }
}

const closeResultModal = () => {
  showResultModal.value = false
}

const handleExecute = async (params: SubAgentExecuteRequest) => {
  if (!selectedAgent.value) return
  
  const result = await executeSubAgent(selectedAgent.value.id, params)
  
  if (result) {
    closeExecuteModal()
    showResultModal.value = true
  }
}

const handleSave = () => {
  closeEditModal()
  showNotification('success', 'SubAgent saved successfully')
}

const handleCreate = async () => {
  const result = await createSubAgent({
    id: newAgent.value.id,
    name: newAgent.value.name,
    description: newAgent.value.description,
    skills: newAgent.value.skillsStr.split(',').map(s => s.trim()).filter(Boolean),
    tools: newAgent.value.toolsStr.split(',').map(s => s.trim()).filter(Boolean),
    system_prompt: newAgent.value.system_prompt,
  })
  
  if (result) {
    closeCreateModal()
    showNotification('success', 'SubAgent created successfully')
  }
}

const handleReload = async (agent: SubAgent) => {
  const result = await reloadSubAgent(agent.id)
  if (result.success) {
    showNotification('success', `SubAgent '${agent.id}' reloaded`)
  } else {
    showNotification('error', result.message || 'Failed to reload')
  }
}

const handleReloadAll = async () => {
  const result = await reloadSubAgents()
  if (result.success) {
    showNotification('success', `Reloaded ${result.loaded} SubAgents`)
  } else {
    showNotification('error', result.message || 'Failed to reload')
  }
}

const handleDelete = async (agent: SubAgent) => {
  if (!confirm(`Are you sure you want to delete '${agent.name}'?`)) return
  
  const success = await deleteSubAgent(agent.id)
  if (success) {
    showNotification('success', `SubAgent '${agent.id}' deleted`)
  } else {
    showNotification('error', 'Failed to delete SubAgent')
  }
}

onMounted(loadSubAgents)
</script>

<style scoped>
.subagent-manager {
  padding: 88px 24px 24px 24px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 1.75rem;
  color: var(--text-primary);
}

.description {
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

.btn.primary {
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
  border: none;
  color: white;
  box-shadow: 0 0 20px rgba(0, 188, 212, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(0, 188, 212, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  border-color: var(--text-muted);
}

.filter-tab.active {
  background: rgba(0, 188, 212, 0.1);
  border-color: #00BCD4;
  color: #00BCD4;
}

.filter-tab .count {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.filter-tab.active .count {
  background: rgba(0, 188, 212, 0.2);
}

.filter-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  min-width: 250px;
}

.filter-search svg {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.filter-search input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
}

.filter-search input::placeholder {
  color: var(--text-muted);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0 0 20px 0;
  color: var(--text-muted);
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: var(--bg-secondary);
  border-radius: 12px;
  max-height: 90vh;
  overflow: auto;
}

.execute-modal {
  width: 100%;
  max-width: 500px;
}

.edit-modal {
  width: 100%;
  max-width: 900px;
  height: 80vh;
}

.create-modal {
  width: 100%;
  max-width: 500px;
}

.create-form {
  display: flex;
  flex-direction: column;
}

.create-form .form-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.create-form .form-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.create-form .form-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.create-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.create-form .form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.create-form .form-group input,
.create-form .form-group textarea {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.create-form .form-group input:focus,
.create-form .form-group textarea:focus {
  outline: none;
  border-color: #00BCD4;
}

.create-form .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.create-form .form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.result-modal{
  width: 100%;
  max-width: 800px;
}

.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background: #00BCD4;
  color: white;
}

.notification.error {
  background: #EF4444;
  color: white;
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
</style>
