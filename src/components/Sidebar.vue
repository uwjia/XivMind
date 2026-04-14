<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed, 'mobile-open': isMobileOpen }">

    <div class="sidebar-content">
      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.HOME) }"
          @click="goToHome"
          :title="isCollapsed ? 'Home' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-home)">
              <path d="M3 9l9-7 9 7v11h-6v-6h-6v6h-6v-11z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </span>
          <span class="picker-label">Home</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.LISTINGS) }"
          @click="goToListings"
          :title="isCollapsed ? 'Listings' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-listings)">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="7" y1="8" x2="17" y2="8"/>
              <line x1="7" y1="12" x2="17" y2="12"/>
              <line x1="7" y1="16" x2="13" y2="16"/>
            </svg>
          </span>
          <span class="picker-label">Listings</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.BOOKMARKS) }"
          @click="goToBookmarks"
          :title="isCollapsed ? 'Bookmarks' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-bookmarks)">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </span>
          <span class="picker-label">Bookmarks</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.DOWNLOADS) }"
          @click="goToDownloads"
          :title="isCollapsed ? 'Downloads' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-downloads)">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </span>
          <span class="picker-label">Downloads</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.FOLLOWED_AUTHORS) }"
          @click="goToFollowedAuthors"
          :title="isCollapsed ? 'Followed Authors' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-followed)">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </span>
          <span class="picker-label">Followed</span>
        </button>
      </div>
      
      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.ASSISTANT) }"
          @click="goToAssistant"
          :title="isCollapsed ? 'Assistant' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-assistant)">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
            </svg>
          </span>
          <span class="picker-label">Assistant</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.SKILLS) }"
          @click="goToSkills"
          :title="isCollapsed ? 'Skills' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-skills)">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </span>
          <span class="picker-label">Skills</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.SUBAGENTS) }"
          @click="goToSubAgents"
          :title="isCollapsed ? 'SubAgents' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-subagents)">
              <rect x="3" y="11" width="18" height="10" rx="2"/>
              <circle cx="12" cy="5" r="2"/>
              <path d="M12 7v4"/>
              <line x1="8" y1="16" x2="8" y2="16"/>
              <line x1="16" y1="16" x2="16" y2="16"/>
            </svg>
          </span>
          <span class="picker-label">SubAgents</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.TEAM) }"
          @click="goToTeam"
          :title="isCollapsed ? 'Team' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-team)">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </span>
          <span class="picker-label">Team</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.MEMORY) }"
          @click="goToMemory"
          :title="isCollapsed ? 'Memory' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-memory)">
              <ellipse cx="12" cy="5" rx="9" ry="3"/>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
          </span>
          <span class="picker-label">Memory</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.AUTHOR_RANKING) }"
          @click="goToAuthorRanking"
          :title="isCollapsed ? 'Ranking' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-ranking)">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </span>
          <span class="picker-label">Ranking</span>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          :class="{ active: isActive(ROUTES.DATA_MANAGER) }"
          @click="goToDataManager"
          :title="isCollapsed ? 'Data Manager' : ''"
        >
          <span class="picker-trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-dataManager)">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </span>
          <span class="picker-label">Data Manager</span>
        </button>
      </div>
    </div>

    <div class="sidebar-footer">
      <button
        class="picker-trigger-btn"
        :class="{ active: isActive(ROUTES.SETTINGS) }"
        @click="goToSettings"
        :title="isCollapsed ? 'Settings' : ''"
      >
        <span class="picker-trigger-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-settings)">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.83.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.83-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </span>
        <span class="picker-label">Settings</span>
      </button>
      <button
        class="picker-trigger-btn"
        @click="toggleTheme"
        :title="isCollapsed ? 'Toggle Theme' : ''"
      >
        <span class="picker-trigger-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--icon-theme)">
            <circle v-if="isDark" cx="12" cy="12" r="5"/>
            <path v-if="isDark" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            <path v-else d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </span>
        <span class="picker-label">{{ isDark ? 'Light' : 'Dark' }}</span>
      </button>
    </div>

    <div class="mobile-overlay" v-if="isMobileOpen" @click="closeMobileSidebar"></div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSidebarStore } from '@/stores/sidebar-store'
import { useThemeStore } from '@/stores/theme-store'
import { ROUTES } from '@/constants/routes'

const router = useRouter()
const route = useRoute()
const sidebarStore = useSidebarStore()
const themeStore = useThemeStore()
const windowWidth = ref<number>(window.innerWidth)

const isCollapsed = computed(() => sidebarStore.effectiveCollapsed)
const isMobileOpen = computed(() => sidebarStore.isMobileOpen)
const isDark = computed(() => themeStore.isDark)

const isActive = (path: string) => route.path === path

const EXPAND_THRESHOLD = 1280
const COLLAPSE_THRESHOLD = 1024

let resizeTimeout: ReturnType<typeof setTimeout> | null = null

const handleResize = () => {
  windowWidth.value = window.innerWidth

  if (windowWidth.value < COLLAPSE_THRESHOLD) {
    sidebarStore.autoCollapse()
    if (sidebarStore.isMobileOpen) {
      sidebarStore.closeMobileSidebar()
    }
  } else if (windowWidth.value >= EXPAND_THRESHOLD) {
    sidebarStore.autoExpand()
  }
}

const debouncedResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  resizeTimeout = setTimeout(handleResize, 100)
}

onMounted(() => {
  window.addEventListener('resize', debouncedResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', debouncedResize)
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
})

const goToHome = () => {
  router.push(ROUTES.HOME)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToListings = () => {
  router.push(ROUTES.LISTINGS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const goToSettings = () => {
  router.push(ROUTES.SETTINGS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToBookmarks = () => {
  router.push(ROUTES.BOOKMARKS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToFollowedAuthors = () => {
  router.push(ROUTES.FOLLOWED_AUTHORS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToDownloads = () => {
  router.push(ROUTES.DOWNLOADS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToAuthorRanking = () => {
  router.push(ROUTES.AUTHOR_RANKING)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToAssistant = () => {
  router.push(ROUTES.ASSISTANT)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToDataManager = () => {
  router.push(ROUTES.DATA_MANAGER)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToSkills = () => {
  router.push(ROUTES.SKILLS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToSubAgents = () => {
  router.push(ROUTES.SUBAGENTS)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToTeam = () => {
  router.push(ROUTES.TEAM)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToMemory = () => {
  router.push(ROUTES.MEMORY)
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const closeMobileSidebar = () => {
  sidebarStore.closeMobileSidebar()
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  width: 224px;
  height: calc(100vh - 64px);
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 900;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition);
}

.logo:hover {
  color: var(--accent-color);
}

.logo-icon {
  width: 28px;
  height: 28px;
  fill: var(--accent-color);
  flex-shrink: 0;
}

.logo-text {
  background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.sidebar-content::-webkit-scrollbar {
  display: none;
}

.sidebar-section {
  margin-bottom: 8px;
}

.picker-trigger-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  text-align: left;
  width: 100%;
}

.picker-trigger-btn:hover {
  background: var(--bg-secondary);
  color: var(--accent-color);
}

.picker-trigger-btn:hover .picker-trigger-icon svg {
  stroke: var(--accent-color);
}

.picker-trigger-btn.active {
  background: var(--bg-secondary);
  color: var(--accent-color);
}

.picker-trigger-btn.active .picker-trigger-icon svg {
  stroke: var(--accent-color);
}

.picker-trigger-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.picker-label {
  flex: 1;
  font-size: 0.9rem;
  line-height: 20px;
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 0.2s, width 0.3s;
}

.picker-trigger-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.picker-trigger-btn svg circle[fill] {
  stroke: none;
}

.sidebar.collapsed .picker-trigger-btn {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .picker-label {
  display: none;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 899;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 64px;
  }

  .sidebar:not(.collapsed) {
    width: 224px;
  }

  .mobile-overlay {
    display: block;
  }
}

@media (max-width: 768px) {
  .sidebar-header {
    padding: 12px;
  }

  .sidebar-content {
    padding: 12px;
  }

  .sidebar-footer {
    padding: 12px;
  }
}
</style>
