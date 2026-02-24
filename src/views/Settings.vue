<template>
  <div class="settings">
    <div class="settings-container">
      <div class="settings-header">
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Customize your XivMind experience</p>
      </div>

      <div class="settings-sections">
        <div class="settings-section">
          <h2 class="section-title">LLM Configuration</h2>
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">Provider</h3>
              <p class="item-description">Select the LLM provider for AI features</p>
            </div>
            <div class="llm-controls">
              <select 
                v-model="providerSelect" 
                @change="onProviderChange"
                class="provider-select"
                :disabled="llmStore.isLoading"
              >
                <option v-for="provider in llmStore.availableProviders" 
                        :key="provider.id" 
                        :value="provider.id">
                  {{ provider.name }} {{ !provider.available ? '(Not configured)' : '' }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">Model</h3>
              <p class="item-description">Select the model to use</p>
            </div>
            <div class="llm-controls">
              <select 
                v-model="modelSelect" 
                @change="onModelChange"
                class="model-select"
                :disabled="llmStore.isLoading"
              >
                <option v-for="model in llmStore.currentModels" :key="model" :value="model">
                  {{ model }}
                </option>
              </select>
            </div>
          </div>
          
          <div v-if="llmStore.selectedProvider === 'ollama'" class="settings-item ollama-status-item">
            <div class="item-info">
              <h3 class="item-title">Ollama Status</h3>
              <p class="item-description">Connection status for local Ollama server</p>
            </div>
            <div class="ollama-status">
              <div v-if="llmStore.ollamaStatus.loading" class="status-badge loading">
                <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
                </svg>
                <span>Checking...</span>
              </div>
              <div v-else-if="llmStore.ollamaStatus.available" class="status-badge available">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>Connected</span>
              </div>
              <div v-else class="status-badge unavailable">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span>{{ llmStore.ollamaStatus.error || 'Not connected' }}</span>
              </div>
              <button @click="refreshOllamaStatus" class="refresh-btn" :disabled="llmStore.ollamaStatus.loading">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M23 4v6h-6"/>
                  <path d="M1 20v-6h6"/>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">Appearance</h2>
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">Theme</h3>
              <p class="item-description">Choose between light and dark mode</p>
            </div>
            <div class="theme-selector">
              <button
                class="theme-option"
                :class="{ active: !isDark }"
                @click="setTheme('light')"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="5"/>
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                </svg>
                <span>Light</span>
              </button>
              <button
                class="theme-option"
                :class="{ active: isDark }"
                @click="setTheme('dark')"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
                <span>Dark</span>
              </button>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">Display</h2>
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">Sidebar State</h3>
              <p class="item-description">Control sidebar visibility</p>
            </div>
            <div class="sidebar-controls">
              <button
                class="control-btn"
                :class="{ active: !isCollapsed }"
                @click="expandSidebar"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
                <span>Expanded</span>
              </button>
              <button
                class="control-btn"
                :class="{ active: isCollapsed }"
                @click="collapseSidebar"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="15 18 9 12 15 6"/>
                </svg>
                <span>Collapsed</span>
              </button>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">API Settings</h2>
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">Max Results</h3>
              <p class="item-description">Maximum number of papers to fetch from arXiv API (10-3000)</p>
            </div>
            <div class="max-results-control">
              <div class="input-wrapper" :class="{ 'error': isInvalid }">
                <input
                  type="number"
                  v-model.number="tempMaxResults"
                  min="10"
                  max="3000"
                  class="number-input"
                  @input="handleMaxResultsChange"
                />
                <span class="input-suffix">papers</span>
              </div>
              <div v-if="isSaving || isSaved || isInvalid" class="save-status" :class="{ 'saving': isSaving, 'saved': isSaved, 'error': isInvalid }">
                <svg v-if="isSaving" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                <svg v-else-if="isSaved" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else-if="isInvalid" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{{ saveStatusText }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">About</h2>
          <div class="settings-item">
            <div class="item-info">
              <h3 class="item-title">XivMind</h3>
              <p class="item-description">Version 0.2.0</p>
            </div>
            <div class="about-links">
              <a href="https://www.xivmind.com/" target="_blank" class="link-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                </svg>
                <span>Visit XivMind</span>
              </a>
              <a href="https://github.com" target="_blank" class="link-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
                <span>GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '../stores/theme-store'
import { useSidebarStore } from '../stores/sidebar-store'
import { useConfigStore } from '../stores/config-store'
import { useLLMStore } from '../stores/llm-store'

const themeStore = useThemeStore()
const sidebarStore = useSidebarStore()
const configStore = useConfigStore()
const llmStore = useLLMStore()

const isDark = computed(() => themeStore.isDark)
const isCollapsed = computed(() => sidebarStore.isCollapsed)
const tempMaxResults = ref(configStore.maxResults)
const isSaving = ref(false)
const isSaved = ref(false)
const isInvalid = computed(() => {
  return tempMaxResults.value < 10 || tempMaxResults.value > 3000
})

const providerSelect = computed({
  get: () => llmStore.selectedProvider,
  set: () => {}
})

const modelSelect = computed({
  get: () => llmStore.selectedModel,
  set: () => {}
})

const saveStatusText = computed(() => {
  if (isSaving.value) return 'Saving...'
  if (isSaved.value) return 'Saved'
  if (isInvalid.value) return 'Invalid (10-3000)'
  return ''
})

const debounce = (fn: Function, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: unknown[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const saveMaxResults = () => {
  if (tempMaxResults.value >= 10 && tempMaxResults.value <= 3000) {
    configStore.setMaxResults(tempMaxResults.value)
  }
}

const debouncedSave = debounce(() => {
  if (tempMaxResults.value >= 10 && tempMaxResults.value <= 3000) {
    isSaving.value = true
    isSaved.value = false
    
    setTimeout(() => {
      saveMaxResults()
      isSaving.value = false
      isSaved.value = true
      
      setTimeout(() => {
        isSaved.value = false
      }, 2000)
    }, 500)
  }
}, 800)

const handleMaxResultsChange = () => {
  isSaved.value = false
  debouncedSave()
}

const setTheme = (theme: string) => {
  const wantDark = theme === 'dark'
  if (themeStore.isDark !== wantDark) {
    themeStore.toggleTheme()
  }
}

const expandSidebar = () => {
  sidebarStore.expandSidebar()
}

const collapseSidebar = () => {
  sidebarStore.collapseSidebar()
}

const onProviderChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  llmStore.setProvider(target.value)
}

const onModelChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  llmStore.setModel(target.value)
}

const refreshOllamaStatus = () => {
  llmStore.checkOllamaStatus()
}

onMounted(() => {
  llmStore.init()
})
</script>

<style scoped>
.settings {
  min-height: 100vh;
  padding-top: 64px;
  background: var(--bg-secondary);
}

.settings-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.settings-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-section {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.settings-item {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.settings-item:last-child {
  margin-bottom: 0;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.item-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.llm-controls {
  display: flex;
  gap: 12px;
}

.provider-select,
.model-select {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.provider-select:focus,
.model-select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.provider-select:disabled,
.model-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ollama-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.loading {
  background: rgba(255, 193, 7, 0.1);
  color: var(--warning-color);
}

.status-badge.available {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.status-badge.unavailable {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.status-badge svg {
  width: 18px;
  height: 18px;
}

.refresh-btn {
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.refresh-btn:hover:not(:disabled) {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 18px;
  height: 18px;
}

.theme-selector {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.theme-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.theme-option:hover {
  border-color: var(--accent-color);
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.theme-option.active {
  border-color: var(--accent-color);
  background: var(--accent-color);
  color: white;
}

.theme-option svg {
  width: 18px;
  height: 18px;
}

.sidebar-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.control-btn:hover {
  border-color: var(--accent-color);
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.control-btn.active {
  border-color: var(--accent-color);
  background: var(--accent-color);
  color: white;
}

.control-btn svg {
  width: 18px;
  height: 18px;
}

.max-results-control {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.number-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 500;
  transition: var(--transition);
}

.number-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.input-wrapper.error .number-input {
  border-color: var(--danger-color);
}

.input-wrapper.error .number-input:focus {
  border-color: var(--danger-color);
}

.input-suffix {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.save-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  transition: var(--transition);
  width: 100%;
}

.save-status.saving {
  border-color: var(--warning-color);
  background: rgba(255, 193, 7, 0.1);
  color: var(--warning-color);
}

.save-status.saved {
  border-color: var(--success-color);
  background: rgba(25, 135, 84, 0.1);
  color: var(--success-color);
}

.save-status.error {
  border-color: var(--danger-color);
  background: rgba(220, 53, 69, 0.1);
  color: var(--danger-color);
}

.save-status svg {
  width: 18px;
  height: 18px;
}

.save-status .spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.about-links {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.link-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.link-btn:hover {
  border-color: var(--accent-color);
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.link-btn svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 768px) {
  .settings-container {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 2rem;
  }

  .settings-section {
    padding: 20px;
  }

  .theme-selector,
  .sidebar-controls,
  .about-links,
  .llm-controls {
    flex-direction: column;
  }

  .theme-option,
  .control-btn,
  .link-btn,
  .provider-select,
  .model-select {
    width: 100%;
  }
}
</style>
