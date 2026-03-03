<template>
  <div class="memory-page">
    <div class="page-header">
      <div class="header-text">
        <h1>Memory</h1>
        <p class="subtitle">Manage your AI's long-term memory for personalized experience</p>
      </div>
    </div>

    <div class="memory-content">
      <div class="memory-stats" v-if="memoryStore.stats">
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.total_memories }}</div>
          <div class="stat-label">Total Memories</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.recall_memory_count }}</div>
          <div class="stat-label">Conversations</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.archival_memory_count }}</div>
          <div class="stat-label">Notes</div>
        </div>
      </div>

      <div class="memory-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="tab-icon" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <div class="tab-header" v-if="activeTab === 'profile'">
          <h4>Profile Settings</h4>
          <button @click="saveProfile" class="save-btn" :disabled="memoryStore.isSaving">
            <svg v-if="memoryStore.isSaving" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
            </svg>
            <span>{{ memoryStore.isSaving ? 'Saving...' : 'Save Profile' }}</span>
          </button>
        </div>
        
        <div v-if="activeTab === 'profile'" class="profile-tab">
          <div class="profile-form">
            
            <div class="form-group">
              <div class="toggle-setting">
                <div class="toggle-info">
                  <label>Extract Profile from Conversations</label>
                  <p class="toggle-description">Automatically extract user preferences and research interests from conversations to update your profile.</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="extractProfile" @change="saveExtractSetting" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Research Interests</label>
              <div class="tags-input">
                <div class="tags-container">
                  <span v-for="(interest, index) in localProfile.research_interests" :key="index" class="tag">
                    {{ interest }}
                    <button @click="removeInterest(index)" class="tag-remove">&times;</button>
                  </span>
                </div>
                <div class="input-row">
                  <input
                    v-model="newInterest"
                    @keydown.enter.prevent="addInterest"
                    placeholder="Add research interest..."
                    class="tag-input"
                  />
                  <button @click="addInterest" class="add-tag-btn" :disabled="!newInterest.trim()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Preferred Domains</label>
              <div class="tags-input">
                <div class="tags-container">
                  <span v-for="(domain, index) in localProfile.preferred_domains" :key="index" class="tag domain">
                    {{ domain }}
                    <button @click="removeDomain(index)" class="tag-remove">&times;</button>
                  </span>
                </div>
                <div class="input-row">
                  <input
                    v-model="newDomain"
                    @keydown.enter.prevent="addDomain"
                    placeholder="Add preferred domain..."
                    class="tag-input"
                  />
                  <button @click="addDomain" class="add-tag-btn" :disabled="!newDomain.trim()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label>Preferred Language</label>
                <select v-model="localProfile.language_preference" class="form-select">
                  <option value="en-US">English</option>
                  <option value="zh-CN">中文</option>
                </select>
              </div>

              <div class="form-group half">
                <label>Summary Style</label>
                <select v-model="localProfile.summary_style" class="form-select">
                  <option value="detailed">Detailed</option>
                  <option value="brief">Brief</option>
                  <option value="bullet_points">Bullet Points</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Custom Instructions</label>
              <textarea
                v-model="localProfile.custom_instructions"
                placeholder="Add custom instructions for the AI..."
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'knowledge'" class="knowledge-tab">
          <div class="knowledge-header">
            <h4>Knowledge Base</h4>
            <button @click="showNoteEditor = true" class="add-note-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>Add Note</span>
            </button>
          </div>

          <div class="knowledge-list" v-if="memoryStore.archivalMemories.length > 0">
            <div 
              v-for="memory in memoryStore.archivalMemories" 
              :key="memory.memory_id" 
              class="knowledge-item"
            >
              <div class="knowledge-info">
                <div class="knowledge-type-badge" :class="memory.content_type">
                  {{ memory.content_type }}
                </div>
                <h5 class="knowledge-title">{{ memory.title || 'Untitled' }}</h5>
                <p class="knowledge-content">{{ memory.content?.slice(0, 150) }}{{ memory.content?.length > 150 ? '...' : '' }}</p>
                <div class="knowledge-meta">
                  <span class="knowledge-date">{{ formatDate(memory.created_at) }}</span>
                  <div class="knowledge-tags" v-if="memory.tags?.length">
                    <span v-for="tag in memory.tags.slice(0, 3)" :key="tag" class="knowledge-tag">{{ tag }}</span>
                  </div>
                </div>
              </div>
              <div class="knowledge-actions">
                <button @click="deleteKnowledge(memory.memory_id)" class="delete-btn" title="Delete">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <p>No notes yet. Create your first note to build your knowledge base!</p>
          </div>
        </div>

        <div v-else-if="activeTab === 'history'" class="history-tab">
          

          <div class="search-input-wrapper">
            <input
              v-model="searchQuery"
              @keydown.enter="performSearch"
              placeholder="Search memories..."
              class="search-input"
            />
            <button @click="performSearch" class="search-btn" :disabled="memoryStore.isLoading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </button>
            <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn" title="Clear search">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div v-if="memoryStore.searchResults.length > 0" class="search-results">
            <div class="search-results-header">
              <span>Search Results ({{ memoryStore.searchResults.length }})</span>
            </div>
            <div v-for="result in memoryStore.searchResults" :key="result.memory_id" class="history-item">
              <div class="history-content">{{ result.content?.slice(0, 150) }}{{ result.content?.length > 150 ? '...' : '' }}</div>
              <div class="history-meta">
                <span class="result-type">{{ result.memory_type }}</span>
                <span class="result-score">Similarity: {{ (result.similarity_score * 100).toFixed(1) }}%</span>
                <span class="history-time">{{ formatTime(result.timestamp) }}</span>
              </div>
              <button @click="deleteHistory(result.memory_id)" class="delete-btn small" title="Delete">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-else-if="hasSearched && memoryStore.searchResults.length === 0" class="no-results">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <p>No memories found matching your search.</p>
            <button @click="clearSearch" class="clear-search-link">Clear search</button>
          </div>

          <div v-else-if="memoryStore.recallMemories.length > 0" class="history-list">
            <div class="history-header">
              <h4>Recall Memories <span class="history-count">({{ memoryStore.stats?.recall_memory_count || 0 }} items)</span></h4>
            </div>
            <div v-for="memory in memoryStore.recallMemories" :key="memory.memory_id" class="history-item">
              <div class="history-content">{{ memory.content?.slice(0, 150) }}{{ memory.content?.length > 150 ? '...' : '' }}</div>
              <div class="history-meta">
                <span class="history-time">{{ formatTime(memory.timestamp) }}</span>
                <span class="history-importance">Importance: {{ (memory.importance_score * 100).toFixed(0) }}%</span>
              </div>
              <button @click="deleteHistory(memory.memory_id)" class="delete-btn small" title="Delete">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <p>No conversation memories yet. Start a conversation to build your memory!</p>
          </div>
        </div>

        <div v-else-if="activeTab === 'danger'" class="danger-tab">
          <div class="danger-section">
            <h4>Danger Zone</h4>
            <p class="danger-description">Clear specific types of memories. These actions cannot be undone.</p>
            
            <div class="danger-actions">
              <div class="danger-action-item">
                <div class="danger-action-info">
                  <h5>Clear Profile (Core Memory)</h5>
                  <p>Delete your user profile including research interests, preferred domains, and custom instructions.</p>
                </div>
                <button @click="confirmClearCore" class="danger-btn" :disabled="memoryStore.isLoading">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  <span>Clear Profile</span>
                </button>
              </div>
              
              <div class="danger-action-item">
                <div class="danger-action-info">
                  <h5>Clear Conversation History (Recall Memory)</h5>
                  <p>Delete all conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }} items). Your profile and knowledge base will remain.</p>
                </div>
                <button @click="confirmClearRecall" class="danger-btn" :disabled="memoryStore.isLoading">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  <span>Clear History</span>
                </button>
              </div>
              
              <div class="danger-action-item">
                <div class="danger-action-info">
                  <h5>Clear Knowledge Base (Archival Memory)</h5>
                  <p>Delete all saved notes and insights ({{ memoryStore.stats?.archival_memory_count || 0 }} items). Your profile and conversation history will remain.</p>
                </div>
                <button @click="confirmClearArchival" class="danger-btn" :disabled="memoryStore.isLoading">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  <span>Clear Knowledge</span>
                </button>
              </div>
            </div>
            
            <div class="danger-divider"></div>
            
            <div class="danger-section-all">
              <h5>Clear All Memories</h5>
              <p class="danger-description">Permanently delete all memories including profile, conversation history, and knowledge base.</p>
              <button @click="showClearConfirm = true" class="danger-btn danger-btn-all" :disabled="memoryStore.isLoading">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                <span>Clear All Memories</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showNoteEditor" class="modal-overlay" @click.self="showNoteEditor = false">
        <ArchivalMemoryEditor 
          @close="showNoteEditor = false" 
          @saved="onNoteSaved"
        />
      </div>

      <div v-if="showClearConfirm" class="modal-overlay" @click.self="showClearConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear All Memories</h3>
          <p>Are you sure you want to clear all memories? This will delete:</p>
          <ul>
            <li>Your user profile</li>
            <li>All conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }})</li>
            <li>All saved notes ({{ memoryStore.stats?.archival_memory_count || 0 }})</li>
          </ul>
          <div class="modal-actions">
            <button @click="showClearConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearAllMemories" class="confirm-btn danger">Clear All</button>
          </div>
        </div>
      </div>

      <div v-if="showClearCoreConfirm" class="modal-overlay" @click.self="showClearCoreConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear Profile</h3>
          <p>Are you sure you want to clear your profile? This will delete:</p>
          <ul>
            <li>Research interests</li>
            <li>Preferred domains</li>
            <li>Custom instructions</li>
          </ul>
          <div class="modal-actions">
            <button @click="showClearCoreConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearCoreMemory" class="confirm-btn danger">Clear Profile</button>
          </div>
        </div>
      </div>

      <div v-if="showClearRecallConfirm" class="modal-overlay" @click.self="showClearRecallConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear History</h3>
          <p>Are you sure you want to clear all conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }} items)?</p>
          <p class="modal-note">Your profile and knowledge base will remain intact.</p>
          <div class="modal-actions">
            <button @click="showClearRecallConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearRecallMemories" class="confirm-btn danger">Clear History</button>
          </div>
        </div>
      </div>

      <div v-if="showClearArchivalConfirm" class="modal-overlay" @click.self="showClearArchivalConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear Knowledge Base</h3>
          <p>Are you sure you want to clear all saved notes and insights ({{ memoryStore.stats?.archival_memory_count || 0 }} items)?</p>
          <p class="modal-note">Your profile and conversation history will remain intact.</p>
          <div class="modal-actions">
            <button @click="showClearArchivalConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearArchivalMemories" class="confirm-btn danger">Clear Knowledge</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onActivated, watch, h } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useMemoryStore } from '@/stores/memory-store'
import ArchivalMemoryEditor from '@/components/ArchivalMemoryEditor.vue'

const memoryStore = useMemoryStore()

type TabId = 'profile' | 'knowledge' | 'history' | 'danger'

const activeTab = ref<TabId>('profile')
const newInterest = ref('')
const newDomain = ref('')
const searchQuery = ref('')
const hasSearched = ref(false)
const showNoteEditor = ref(false)
const showClearConfirm = ref(false)
const showClearCoreConfirm = ref(false)
const showClearRecallConfirm = ref(false)
const showClearArchivalConfirm = ref(false)
const extractProfile = ref(localStorage.getItem('extract_profile') === 'true')

const localProfile = reactive({
  research_interests: [] as string[],
  preferred_domains: [] as string[],
  frequently_used_skills: [] as string[],
  language_preference: 'en-US',
  summary_style: 'detailed' as 'detailed' | 'brief' | 'bullet_points',
  custom_instructions: ''
})

const tabs: { id: TabId; label: string; icon: ReturnType<typeof h> }[] = [
  { id: 'profile', label: 'Profile', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '12', cy: '7', r: '4' }),
  ])},
  { id: 'knowledge', label: 'Knowledge', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
    h('polyline', { points: '14 2 14 8 20 8' }),
  ])},
  { id: 'history', label: 'History', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('polyline', { points: '12 6 12 12 16 14' }),
  ])},
  { id: 'danger', label: 'Danger', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
    h('line', { x1: '12', y1: '9', x2: '12', y2: '13' }),
    h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' }),
  ])},
]

watch(() => memoryStore.coreMemory, (newVal) => {
  if (newVal) {
    localProfile.research_interests = [...(newVal.research_interests || [])]
    localProfile.preferred_domains = [...(newVal.preferred_domains || [])]
    localProfile.frequently_used_skills = [...(newVal.frequently_used_skills || [])]
    localProfile.language_preference = newVal.language_preference || 'en-US'
    localProfile.summary_style = newVal.summary_style || 'detailed'
    localProfile.custom_instructions = newVal.custom_instructions || ''
  }
}, { immediate: true })

const addInterest = () => {
  if (newInterest.value.trim() && !localProfile.research_interests.includes(newInterest.value.trim())) {
    localProfile.research_interests.push(newInterest.value.trim())
    newInterest.value = ''
  }
}

const removeInterest = (index: number) => {
  localProfile.research_interests.splice(index, 1)
}

const addDomain = () => {
  if (newDomain.value.trim() && !localProfile.preferred_domains.includes(newDomain.value.trim())) {
    localProfile.preferred_domains.push(newDomain.value.trim())
    newDomain.value = ''
  }
}

const removeDomain = (index: number) => {
  localProfile.preferred_domains.splice(index, 1)
}

const saveProfile = async () => {
  // Add any pending input before saving
  if (newInterest.value.trim()) {
    addInterest()
  }
  if (newDomain.value.trim()) {
    addDomain()
  }
  
  await memoryStore.updateCoreMemory({
    research_interests: localProfile.research_interests,
    preferred_domains: localProfile.preferred_domains,
    frequently_used_skills: localProfile.frequently_used_skills,
    language_preference: localProfile.language_preference,
    summary_style: localProfile.summary_style,
    custom_instructions: localProfile.custom_instructions,
  })
}

const saveExtractSetting = () => {
  localStorage.setItem('extract_profile', extractProfile.value.toString())
}

const performSearch = async () => {
  if (searchQuery.value.trim()) {
    hasSearched.value = true
    await memoryStore.searchMemories(searchQuery.value.trim())
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  memoryStore.searchResults = []
  hasSearched.value = false
}

const deleteHistory = async (memoryId: string) => {
  await memoryStore.deleteRecallMemory(memoryId)
}

const deleteKnowledge = async (memoryId: string) => {
  await memoryStore.deleteArchivalMemory(memoryId)
}

const clearAllMemories = async () => {
  await memoryStore.clearAllMemories()
  showClearConfirm.value = false
}

const confirmClearCore = () => {
  showClearCoreConfirm.value = true
}

const confirmClearRecall = () => {
  showClearRecallConfirm.value = true
}

const confirmClearArchival = () => {
  showClearArchivalConfirm.value = true
}

const clearCoreMemory = async () => {
  await memoryStore.clearCoreMemory()
  showClearCoreConfirm.value = false
}

const clearRecallMemories = async () => {
  await memoryStore.clearRecallMemories()
  showClearRecallConfirm.value = false
}

const clearArchivalMemories = async () => {
  await memoryStore.clearArchivalMemories()
  showClearArchivalConfirm.value = false
}

const onNoteSaved = () => {
  showNoteEditor.value = false
}

const formatTime = (timestamp: string): string => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return `${minutes}m ago`
    }
    return `${hours}h ago`
  } else if (days === 1) {
    return 'Yesterday'
  } else if (days < 7) {
    return `${days}d ago`
  } else {
    return date.toLocaleDateString()
  }
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

watch(activeTab, async (newTab) => {
  if (newTab === 'history' && memoryStore.recallMemories.length === 0) {
    await memoryStore.fetchRecallMemories()
  } else if (newTab === 'knowledge' && memoryStore.archivalMemories.length === 0) {
    await memoryStore.fetchArchivalMemories()
  }
})

onMounted(async () => {
  await memoryStore.init()
})

onActivated(async () => {
  await memoryStore.init()
  if (activeTab.value === 'history') {
    await memoryStore.fetchRecallMemories()
  } else if (activeTab.value === 'knowledge') {
    await memoryStore.fetchArchivalMemories()
  }
})

onBeforeRouteLeave(() => {
  memoryStore.searchResults = []
})
</script>

<style scoped>
.memory-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E91E63, #9C27B0);
  border-radius: 12px;
  color: white;
  flex-shrink: 0;
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-text h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.header-text .subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

.memory-content {
  padding: 0;
}

.memory-stats {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  margin-bottom: 24px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--accent-color);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.memory-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}

.tab-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.tab-btn.active {
  color: white;
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.tab-icon {
  width: 16px;
  height: 16px;
}

.tab-content {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.tab-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group.half {
  flex: 1;
}

.tags-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent-color);
  color: white;
  border-radius: 16px;
  font-size: 0.85rem;
}

.tag.domain {
  background: var(--success-color);
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.tag-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-row .tag-input {
  flex: 1;
}

.add-tag-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.add-tag-btn:hover:not(:disabled) {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.add-tag-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-tag-btn svg {
  width: 18px;
  height: 18px;
}

.form-select {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-textarea {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
  min-height: 80px;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
}

.toggle-setting {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  gap: 16px;
}

.toggle-info {
  flex: 1;
}

.toggle-info label {
  display: block;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.toggle-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary, #37474f);
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--accent-color);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.save-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-btn .spinner {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.knowledge-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.add-note-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.add-note-btn:hover {
  opacity: 0.9;
}

.add-note-btn svg {
  width: 16px;
  height: 16px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.knowledge-info {
  flex: 1;
  min-width: 0;
}

.knowledge-type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.knowledge-type-badge.note {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.knowledge-type-badge.insight {
  background: rgba(255, 193, 7, 0.1);
  color: #FFC107;
}

.knowledge-type-badge.summary {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.knowledge-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.knowledge-content {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0 0 8px 0;
}

.knowledge-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.knowledge-tags {
  display: flex;
  gap: 4px;
}

.knowledge-tag {
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
}

.knowledge-actions {
  display: flex;
  align-items: flex-start;
}

.delete-btn {
  padding: 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.delete-btn:hover {
  border-color: var(--danger-color);
  color: var(--danger-color);
  background: rgba(239, 68, 68, 0.1);
}

.delete-btn.small {
  padding: 4px;
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.no-results svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.no-results p {
  margin: 0 0 12px 0;
}

.clear-search-link {
  background: none;
  border: none;
  color: var(--accent-color);
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
}

.clear-search-link:hover {
  text-decoration: underline;
}

.search-input-wrapper {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.search-btn {
  padding: 12px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.search-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-btn svg {
  width: 18px;
  height: 18px;
}

.clear-search-btn {
  padding: 12px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.clear-search-btn:hover {
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.clear-search-btn svg {
  width: 18px;
  height: 18px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-results-header {
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.search-result-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.result-content {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: 8px;
}

.result-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.result-type {
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 4px;
}

.result-score {
  color: var(--accent-color);
  font-weight: 500;
}

.history-header {
  margin-bottom: 16px;
}

.history-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.history-count {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 400;
  margin-left: 8px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  position: relative;
  padding: 16px;
  padding-right: 44px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.history-content {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.history-item .delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
}

.danger-section {
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--danger-color);
}

.danger-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--danger-color);
  margin: 0 0 8px 0;
}

.danger-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
}

.danger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.danger-btn:hover:not(:disabled) {
  background: var(--danger-color);
  color: white;
}

.danger-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-btn svg {
  width: 16px;
  height: 16px;
}

.danger-action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  gap: 16px;
  margin-bottom: 12px;
}

.danger-action-info {
  flex: 1;
}

.danger-action-info h5 {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.danger-action-info p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.danger-divider {
  height: 1px;
  background: var(--border-color);
  margin: 24px 0;
}

.danger-section-all {
  padding: 16px;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid var(--danger-color);
  border-radius: 8px;
}

.danger-section-all h5 {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--danger-color);
}

.danger-section-all .danger-description {
  margin: 0 0 16px 0;
}

.danger-btn-all {
  background: var(--danger-color);
  color: white;
}

.danger-btn-all:hover:not(:disabled) {
  background: #d32f2f;
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
  padding: 24px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.modal-content p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.modal-content ul {
  margin: 0 0 16px 20px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.modal-content li {
  margin-bottom: 4px;
}

.modal-note {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-style: italic;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn.danger {
  background: var(--danger-color);
}

@media (max-width: 768px) {
  .header-icon {
    width: 40px;
    height: 40px;
  }

  .header-text h1 {
    font-size: 1.25rem;
  }

  .memory-stats {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .tab-content {
    padding: 16px;
  }

  .form-row {
    flex-direction: column;
  }
}
</style>
