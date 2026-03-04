<template>
  <div class="history-tab">
    
    <div class="history-actions">
      <button @click="openStoreMemory" class="action-btn primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>Store Memory</span>
      </button>
    </div>

    <div class="search-input-wrapper">
      <input
        v-model="searchQuery"
        @keydown.enter="recallMemories"
        placeholder="Search memories..."
        class="search-input"
      />
      <button @click="recallMemories" class="search-btn" :disabled="memoryStore.isLoading">
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
      <button 
        v-if="searchQuery" 
        @click="getMemoryContextForQuery" 
        class="context-btn" 
        title="Get memory context"
        :disabled="isGettingContext"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </button>
    </div>

    <div v-if="memoryContextResult" class="memory-context-result">
      <div class="context-header">
        <h5>Memory Context</h5>
        <button @click="clearContextResult" class="clear-context-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <pre class="context-content">{{ memoryContextResult }}</pre>
    </div>

    <div v-if="memoryStore.searchResults.length > 0" class="search-results">
      <div class="search-results-header">
        <span>Search Results ({{ memoryStore.searchResults.length }})</span>
        <button @click="forgetSelectedMemory()" class="forget-all-btn" title="Forget all auto-created memories">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>Forget Auto-Created</span>
        </button>
      </div>
      <div v-for="result in memoryStore.searchResults" :key="result.memory_id" class="history-item">
        <div class="history-content">{{ result.content?.slice(0, 150) }}{{ result.content?.length > 150 ? '...' : '' }}</div>
        <div class="history-meta">
          <span class="result-type">{{ result.memory_type }}</span>
          <span class="result-category">{{ result.category }}</span>
          <span class="result-score">Similarity: {{ (result.similarity_score * 100).toFixed(1) }}%</span>
          <span class="history-time">{{ formatTime(result.timestamp) }}</span>
        </div>
        <button @click="forgetSelectedMemory(result.memory_id)" class="delete-btn small" title="Delete">
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

    <Teleport to="body">
      <div v-if="showStoreMemory" class="modal-overlay" @click.self="closeStoreMemory">
        <StoreMemoryModal 
          v-model="showStoreMemory"
          :is-storing="isStoringMemory"
          @store="handleStoreMemory"
        />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useMemoryHistory } from '@/composables/memory'
import { useMemoryStore } from '@/stores/memory-store'
import StoreMemoryModal from './StoreMemoryModal.vue'

const memoryStore = useMemoryStore()
const {
  searchQuery,
  hasSearched,
  showStoreMemory,
  isStoringMemory,
  memoryContextResult,
  isGettingContext,
  recallMemories,
  clearSearch,
  openStoreMemory,
  closeStoreMemory,
  storeNewMemory,
  forgetSelectedMemory,
  getMemoryContextForQuery,
  clearContextResult,
  deleteHistory,
  formatTime,
} = useMemoryHistory()

const handleStoreMemory = async () => {
  await storeNewMemory()
}
</script>

<style scoped>
.history-tab {
  padding: 0;
}

.history-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.action-btn.primary {
  background: var(--accent-color);
  color: white;
}

.action-btn.primary:hover {
  opacity: 0.9;
}

.action-btn svg {
  width: 18px;
  height: 18px;
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

.context-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.context-btn:hover:not(:disabled) {
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.context-btn:hover:not(:disabled) svg {
  stroke: white;
}

.context-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.context-btn svg {
  width: 18px;
  height: 18px;
  stroke: var(--text-secondary);
}

.memory-context-result {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.context-header h5 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.clear-context-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition);
}

.clear-context-btn:hover {
  background: var(--bg-tertiary);
}

.clear-context-btn svg {
  width: 16px;
  height: 16px;
  stroke: var(--text-secondary);
}

.context-content {
  font-size: 0.85rem;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.forget-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  color: var(--danger-color);
  font-size: 0.8rem;
  cursor: pointer;
  transition: var(--transition);
}

.forget-all-btn:hover {
  background: var(--danger-color);
  color: white;
}

.forget-all-btn svg {
  width: 14px;
  height: 14px;
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

.result-type,
.result-category {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: capitalize;
}

.result-score {
  color: var(--accent-color);
  font-weight: 500;
}

.history-item .delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.history-item .delete-btn:hover {
  border-color: var(--danger-color);
  color: var(--danger-color);
  background: rgba(239, 68, 68, 0.1);
}

.history-item .delete-btn.small {
  padding: 4px;
}

.history-item .delete-btn svg {
  width: 16px;
  height: 16px;
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

.history-importance {
  color: var(--accent-color);
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
</style>
