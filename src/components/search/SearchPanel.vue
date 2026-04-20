<template>
  <Teleport to="body">
    <Transition name="panel">
      <div
        v-if="isVisible"
        class="search-panel"
        :class="{ minimized: isMinimized, dragging: isDragging }"
        :style="panelStyle"
      >
        <div class="search-panel-header" @mousedown="handleMouseDown">
          <div class="header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="header-icon">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            <span class="header-title">Search Papers</span>
          </div>
          <div class="header-actions">
            <button class="header-btn" @click.stop="toggleMinimize" title="Minimize">
              <svg v-if="!isMinimized" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="18 15 12 9 6 15"/>
              </svg>
            </button>
            <button class="header-btn close" @click.stop="hidePanel" title="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <template v-if="!isMinimized">
          <div class="search-panel-body">
            <div class="search-input-group">
              <input
                type="text"
                v-model="localQuery"
                placeholder="Enter search query..."
                class="search-input"
                @keyup.enter="handleSearch"
              />
              <button class="search-btn" @click="handleSearch" :disabled="!localQuery.trim()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
              </button>
            </div>

            <div class="search-options">
              <div class="option-group">
                <label class="option-label">Search Source</label>
                <select v-model="localSource" class="option-select">
                  <option value="arxiv">arXiv API Direct</option>
                  <option value="backend">Backend Database</option>
                  <option value="semantic">Semantic Search</option>
                </select>
              </div>

              <template v-if="localSource === 'arxiv'">
                <div class="option-group">
                  <label class="option-label">Category</label>
                  <input
                    type="text"
                    v-model="localArxivOptions.category"
                    placeholder="e.g., cs.AI, cs.LG"
                    class="option-input"
                  />
                </div>
                <div class="option-group">
                  <label class="option-label">Max Results</label>
                  <input
                    type="number"
                    v-model.number="localArxivOptions.maxResults"
                    min="1"
                    max="100"
                    class="option-input"
                  />
                </div>
              </template>

              <template v-if="localSource === 'backend'">
                <div class="option-group">
                  <label class="option-label">Search Type</label>
                  <select v-model="localBackendOptions.searchType" class="option-select">
                    <option value="keyword">Keyword (Title/Abstract/ID)</option>
                    <option value="author">Author</option>
                  </select>
                </div>
                <template v-if="localBackendOptions.searchType === 'keyword'">
                  <div class="option-group checkbox-group">
                    <label class="checkbox-label">
                      <input
                        type="checkbox"
                        v-model="localBackendOptions.titleOnly"
                        class="checkbox-input"
                      />
                      <span>Search in title only</span>
                    </label>
                  </div>
                  <div class="option-group checkbox-group">
                    <label class="checkbox-label">
                      <input
                        type="checkbox"
                        v-model="localBackendOptions.exactPhrase"
                        class="checkbox-input"
                      />
                      <span>Exact phrase match</span>
                    </label>
                  </div>
                  <div class="option-group">
                    <label class="option-label">Category</label>
                    <input
                      type="text"
                      v-model="localBackendOptions.category"
                      placeholder="e.g., cs.AI, cs.LG"
                      class="option-input"
                    />
                  </div>
                  <div class="option-group">
                    <label class="option-label">Max Results</label>
                    <input
                      type="number"
                      v-model.number="localBackendOptions.maxResults"
                      min="1"
                      max="100"
                      class="option-input"
                    />
                  </div>
                  <div class="option-group">
                    <label class="option-label">Date From (optional)</label>
                    <input
                      type="date"
                      v-model="localBackendOptions.dateFrom"
                      class="option-input"
                    />
                  </div>
                  <div class="option-group">
                    <label class="option-label">Date To (optional)</label>
                    <input
                      type="date"
                      v-model="localBackendOptions.dateTo"
                      class="option-input"
                    />
                  </div>
                </template>
                <template v-else-if="localBackendOptions.searchType === 'author'">
                  <div class="option-group">
                    <label class="option-label">Max Results</label>
                    <input
                      type="number"
                      v-model.number="localBackendOptions.maxResults"
                      min="1"
                      max="100"
                      class="option-input"
                    />
                  </div>
                </template>
              </template>

              <template v-if="localSource === 'semantic'">
                <div class="option-group">
                  <label class="option-label">Top K</label>
                  <input
                    type="number"
                    v-model.number="localSemanticOptions.topK"
                    min="1"
                    max="100"
                    class="option-input"
                  />
                </div>
                <div class="option-group">
                  <label class="option-label">Category (optional)</label>
                  <input
                    type="text"
                    v-model="localSemanticOptions.category"
                    placeholder="e.g., cs.AI"
                    class="option-input"
                  />
                </div>
                <div class="option-group">
                  <label class="option-label">Date From (optional)</label>
                  <input
                    type="date"
                    v-model="localSemanticOptions.dateFrom"
                    class="option-input"
                  />
                </div>
                <div class="option-group">
                  <label class="option-label">Date To (optional)</label>
                  <input
                    type="date"
                    v-model="localSemanticOptions.dateTo"
                    class="option-input"
                  />
                </div>
              </template>
            </div>
          </div>
        </template>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useSearchPanel } from '@/composables/useSearchPanel'

const {
  isDragging,
  localQuery,
  localSource,
  localArxivOptions,
  localBackendOptions,
  localSemanticOptions,
  isVisible,
  isMinimized,
  panelStyle,
  handleMouseDown,
  toggleMinimize,
  hidePanel,
  handleSearch
} = useSearchPanel()
</script>

<style scoped>
.search-panel {
  position: fixed;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-panel.dragging {
  user-select: none;
  cursor: move;
}

.search-panel.minimized {
  height: auto !important;
}

.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.search-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  cursor: move;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  width: 18px;
  height: 18px;
  color: var(--accent-color);
}

.header-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.header-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.header-btn.close:hover {
  background: rgba(220, 53, 69, 0.15);
  color: var(--danger-color);
}

.header-btn svg {
  width: 16px;
  height: 16px;
}

.search-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.search-input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: none;
  background: var(--accent-color);
  border-radius: 8px;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
}

.search-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-btn svg {
  width: 20px;
  height: 20px;
}

.search-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.option-select,
.option-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.option-select {
  padding-right: 32px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  cursor: pointer;
}

.option-select:focus,
.option-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.option-input::placeholder {
  color: var(--text-muted);
}

.option-input[type="date"] {
  position: relative;
  cursor: pointer;
}

.option-input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  cursor: pointer;
  opacity: 0;
}

.option-input[type="date"]::-webkit-datetime-edit {
  cursor: pointer;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--accent-color);
}
</style>
