<template>
  <header class="header">
    <div class="header-container">
      <div class="header-left">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg v-if="!isCollapsed" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        <router-link :to="ROUTES.HOME" class="logo">
          <svg viewBox="0 0 24 24" class="logo-icon">
            <path d="M12 2C12 2 4 8 4 14C4 20 8 22 12 22C16 22 20 20 20 14C20 8 12 2 12 2Z" fill="none" stroke="#00BCD4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 2V22" stroke="#00BCD4" stroke-width="1" stroke-linecap="round"/>
            <path d="M12 14Q6 10 4.5 13" stroke="#00BCD4" stroke-width="0.8" stroke-linecap="round" fill="none"/>
            <path d="M12 14Q18 10 19.5 13" stroke="#00BCD4" stroke-width="0.8" stroke-linecap="round" fill="none"/>
          </svg>
          <span class="logo-text">XivMind</span>
        </router-link>
      </div>

      <div class="header-right">
        <button ref="searchBtnRef" class="search-panel-btn" @click="toggleSearchPanel" title="Search Papers">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-search)">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
        </button>
        <button ref="historyBtnRef" class="history-btn" @click="toggleHistoryPanel" title="Recent Reading">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-history)">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </button>
        <button ref="noteBtnRef" class="note-btn" @click="toggleNotePanel" title="Notes Panel">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-note)">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <span v-if="noteCount > 0" class="note-badge">{{ noteCount }}</span>
        </button>
        <button class="icon-style-btn" @click="toggleIconStyle" :title="isIconColorful ? 'Switch to Minimal Icons' : 'Switch to Colorful Icons'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="6" cy="6" r="3" fill="var(--icon-style-dot-1)"/>
            <circle cx="18" cy="6" r="3" fill="var(--icon-style-dot-2)"/>
            <circle cx="6" cy="18" r="3" fill="var(--icon-style-dot-3)"/>
            <circle cx="18" cy="18" r="3" fill="var(--icon-style-dot-4)"/>
          </svg>
        </button>
      </div>
    </div>
    <NotePanel />
    <ReadingHistoryPanel />
    <SearchPanel />
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSidebarStore } from '@/stores/sidebar-store'
import { useNoteStore } from '@/stores/note-store'
import { useThemeStore } from '@/stores/theme-store'
import { useReadingHistoryStore } from '@/stores/reading-history-store'
import { useSearchPanelStore } from '@/stores/search-panel-store'
import { ROUTES } from '@/constants/routes'
import NotePanel from '@/components/note/NotePanel.vue'
import ReadingHistoryPanel from '@/components/reading-history/ReadingHistoryPanel.vue'
import SearchPanel from '@/components/search/SearchPanel.vue'

const sidebarStore = useSidebarStore()
const noteStore = useNoteStore()
const themeStore = useThemeStore()
const historyStore = useReadingHistoryStore()
const searchPanelStore = useSearchPanelStore()

const isCollapsed = computed(() => sidebarStore.effectiveCollapsed)
const noteCount = computed(() => noteStore.notes.length)
const noteBtnRef = ref<HTMLElement | null>(null)
const historyBtnRef = ref<HTMLElement | null>(null)
const searchBtnRef = ref<HTMLElement | null>(null)
const isIconColorful = computed(() => themeStore.iconStyle === 'colorful')

const toggleSidebar = () => {
  sidebarStore.toggleSidebar()
}

const closeOtherPanels = (exclude: 'note' | 'history' | 'search') => {
  if (exclude !== 'note') {
    noteStore.hidePanel()
  }
  if (exclude !== 'history') {
    historyStore.hidePanel()
  }
  if (exclude !== 'search') {
    searchPanelStore.hidePanel()
  }
}

const updateNoteBtnPosition = () => {
  if (noteBtnRef.value) {
    const rect = noteBtnRef.value.getBoundingClientRect()
    noteStore.setNoteBtnPosition(rect.right, rect.bottom)
  }
}

const toggleNotePanel = () => {
  updateNoteBtnPosition()
  if (!noteStore.isVisible) {
    closeOtherPanels('note')
  }
  noteStore.togglePanel()
}

const updateHistoryBtnPosition = () => {
  if (historyBtnRef.value) {
    const rect = historyBtnRef.value.getBoundingClientRect()
    historyStore.setHistoryBtnPosition(rect.right, rect.bottom)
  }
}

const toggleHistoryPanel = () => {
  updateHistoryBtnPosition()
  if (!historyStore.isVisible) {
    closeOtherPanels('history')
  }
  historyStore.togglePanel()
}

const updateSearchBtnPosition = () => {
  if (searchBtnRef.value) {
    const rect = searchBtnRef.value.getBoundingClientRect()
    searchPanelStore.setSearchBtnPosition(rect.right, rect.bottom)
  }
}

const toggleSearchPanel = () => {
  updateSearchBtnPosition()
  if (!searchPanelStore.isVisible) {
    closeOtherPanels('search')
  }
  searchPanelStore.togglePanel()
}

const toggleIconStyle = () => {
  themeStore.toggleIconStyle()
}

defineExpose({
  noteBtnRef,
  historyBtnRef,
  updateNoteBtnPosition
})
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  z-index: 1000;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.header-container {
  width: 100%;
  margin: 0;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 0;
  padding-left: 0;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.sidebar-toggle svg {
  width: 18px;
  height: 18px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 700;
}

.logo-icon {
  width: 40px;
  height: 40px;
  fill: var(--accent-color);
}

.logo-text {
  background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.5rem;
  font-weight: 700;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.search-panel-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.search-panel-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.search-panel-btn svg {
  width: 20px;
  height: 20px;
}

.history-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.history-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.history-btn svg {
  width: 20px;
  height: 20px;
}

.note-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.note-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.note-btn svg {
  width: 20px;
  height: 20px;
}

.note-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--accent-color);
  color: white;
  font-size: 0.65rem;
  padding: 2px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  font-weight: 600;
}

.icon-style-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
}

.icon-style-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.icon-style-btn svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }
}
</style>
