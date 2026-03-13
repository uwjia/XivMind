<template>
  <div class="note-toolbar">
    <div class="toolbar-left">
      <button class="toolbar-btn add-btn" @click="$emit('add')" title="Add note">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
      </button>
      <div class="search-wrapper">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="search-icon">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          :value="searchQuery"
          @input="$emit('search', ($event.target as HTMLInputElement).value)"
          placeholder="Search notes..."
          class="search-input"
        />
        <button
          v-if="searchQuery"
          class="clear-btn"
          @click="$emit('search', '')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="toolbar-right">
      <div v-if="allTags.length > 0" class="tag-filter">
        <select
          :value="filterTag || ''"
          @change="$emit('filter', ($event.target as HTMLSelectElement).value || null)"
          class="tag-select"
        >
          <option value="">All tags</option>
          <option v-for="tag in allTags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
      </div>
      <button
        v-if="selectedCount > 0"
        class="toolbar-btn"
        @click="$emit('copy-selected')"
        title="Copy selected"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
        </svg>
        <span class="count">{{ selectedCount }}</span>
      </button>
      <button
        v-if="selectedCount > 0"
        class="toolbar-btn danger"
        @click="$emit('delete-selected')"
        title="Delete selected"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
      <button class="toolbar-btn" @click="$emit('export')" title="Export">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  searchQuery: string
  filterTag: string | null
  allTags: string[]
  selectedCount: number
}>()

defineEmits<{
  (e: 'add'): void
  (e: 'search', query: string): void
  (e: 'filter', tag: string | null): void
  (e: 'copy-selected'): void
  (e: 'delete-selected'): void
  (e: 'export'): void
}>()
</script>

<style scoped>
.note-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  gap: 8px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
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
  position: relative;
}

.toolbar-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.toolbar-btn.add-btn {
  background: var(--accent-color);
  color: white;
}

.toolbar-btn.add-btn:hover {
  background: var(--accent-hover);
}

.toolbar-btn.danger:hover {
  color: var(--danger-color);
}

.toolbar-btn svg {
  width: 16px;
  height: 16px;
}

.count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--accent-color);
  color: white;
  font-size: 0.65rem;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 14px;
  text-align: center;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 8px;
  flex: 1;
  max-width: 160px;
}

.search-icon {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.8rem;
  outline: none;
  padding: 0 4px;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  color: var(--text-muted);
  padding: 0;
}

.clear-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.clear-btn svg {
  width: 12px;
  height: 12px;
}

.tag-filter {
  position: relative;
}

.tag-select {
  appearance: none;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 24px 4px 8px;
  font-size: 0.8rem;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  font-family: inherit;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
}

.tag-select:hover {
  border-color: var(--accent-color);
}
</style>
