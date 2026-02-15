<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed, 'mobile-open': isMobileOpen }">

    <div class="sidebar-content">
      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          @click="goToHome"
          :title="isCollapsed ? 'Home' : ''"
        >
          <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
            <path d="M3 9l9-7 9 7v11h-6v-6h-6v6h-6v-11z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <div v-else class="picker-trigger-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="#4CAF50">
              <path d="M3 9l9-7 9 7v11h-6v-6h-6v6h-6v-11z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            <span class="picker-label">Home</span>
          </div>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          @click="goToBookmarks"
          :title="isCollapsed ? 'Bookmarks' : ''"
        >
          <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#FFD700">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
          <div v-else class="picker-trigger-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="#FFD700">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="picker-label">Bookmarks</span>
          </div>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          @click="goToDownloads"
          :title="isCollapsed ? 'Downloads' : ''"
        >
          <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#2196F3">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7,10 12,15 17,10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <div v-else class="picker-trigger-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2196F3">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span class="picker-label">Downloads</span>
          </div>
        </button>
      </div>

      <div class="sidebar-section">
        <button
          class="picker-trigger-btn"
          @click="goToAssistant"
          :title="isCollapsed ? 'Assistant' : ''"
        >
          <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#10B981">
            <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
          </svg>
          <div v-else class="picker-trigger-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17c-2 0-3 1-3 1v1h6v-1s-1-1-3-1z"/>
            </svg>
            <span class="picker-label">Assistant</span>
          </div>
        </button>
      </div>
    </div>

    <div class="sidebar-footer">
      <button
        class="picker-trigger-btn"
        @click="goToSettings"
        :title="isCollapsed ? 'Settings' : ''"
      >
        <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#2196F3">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.83.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.83-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <div v-else class="picker-trigger-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2196F3">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.83.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.83-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          <span class="picker-label">Settings</span>
        </div>
      </button>
      <button
        class="picker-trigger-btn"
        @click="toggleTheme"
        :title="isCollapsed ? 'Toggle Theme' : ''"
      >
        <svg v-if="isCollapsed" viewBox="0 0 24 24" fill="none" stroke="#FFC107">
          <circle v-if="isDark" cx="12" cy="12" r="5"/>
          <path v-if="isDark" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          <path v-else d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <div v-else class="picker-trigger-content">
          <svg viewBox="0 0 24 24" fill="none" stroke="#FFC107">
            <circle v-if="isDark" cx="12" cy="12" r="5"/>
            <path v-if="isDark" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            <path v-else d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
          <span class="picker-label">{{ isDark ? 'Light' : 'Dark' }}</span>
        </div>
      </button>
    </div>

    <div class="mobile-overlay" v-if="isMobileOpen" @click="closeMobileSidebar"></div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSidebarStore } from '../stores/sidebar-store'
import { useThemeStore } from '../stores/theme-store'

const router = useRouter()
const sidebarStore = useSidebarStore()
const themeStore = useThemeStore()
const windowWidth = ref<number>(window.innerWidth)

const isCollapsed = computed(() => sidebarStore.isCollapsed)
const isMobileOpen = computed(() => sidebarStore.isMobileOpen)
const isDark = computed(() => themeStore.isDark)

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (windowWidth.value < 1024 && !sidebarStore.isCollapsed) {
    sidebarStore.collapseSidebar()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const goToHome = () => {
  router.push('/')
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const goToSettings = () => {
  router.push('/settings')
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToBookmarks = () => {
  router.push('/bookmarks')
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToDownloads = () => {
  router.push('/downloads')
  if (isMobileOpen.value) {
    sidebarStore.closeMobileSidebar()
  }
}

const goToAssistant = () => {
  router.push('/assistant')
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
}

.sidebar-section {
  margin-bottom: 24px;
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
  transition: var(--transition);
  text-align: left;
  width: 100%;
}

.picker-trigger-btn:hover {
  background: var(--bg-secondary);
  color: var(--accent-color);
}

.picker-trigger-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.picker-label {
  flex: 1;
  font-size: 0.9rem;
}

.picker-trigger-btn svg {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.sidebar.collapsed .picker-trigger-btn {
  justify-content: center;
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
