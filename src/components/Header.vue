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
        <router-link to="/" class="logo">
          <svg viewBox="0 0 24 24" class="logo-icon">
            <path d="M12 2C12 2 4 8 4 14C4 20 8 22 12 22C16 22 20 20 20 14C20 8 12 2 12 2Z" fill="none" stroke="#00BCD4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 4V20" stroke="#00BCD4" stroke-width="1" stroke-linecap="round"/>
            <path d="M12 14L9 12" stroke="#00BCD4" stroke-width="0.8" stroke-linecap="round"/>
            <path d="M12 14L15 12" stroke="#00BCD4" stroke-width="0.8" stroke-linecap="round"/>
          </svg>
          <span class="logo-text">XivMind</span>
        </router-link>
      </div>

      <div class="header-center">
        <div class="search-bar">
          <input
            type="text"
            placeholder="Search papers..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          />
          <button class="search-icon-btn" @click="handleSearch">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSidebarStore } from '../stores/sidebar-store'

const router = useRouter()
const route = useRoute()
const sidebarStore = useSidebarStore()

const searchQuery = ref<string>('')
const isCollapsed = computed(() => sidebarStore.isCollapsed)

watch(() => route.query?.q, (newQuery) => {
  if (newQuery !== undefined) {
    searchQuery.value = newQuery as string
  }
}, { immediate: true })

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } })
  }
}

const toggleSidebar = () => {
  sidebarStore.toggleSidebar()
}
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

.header-center {
  flex: 1;
  max-width: 600px;
  margin: 0 40px;
}

.search-bar {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 8px 16px;
  transition: var(--transition);
}

.search-bar:focus-within {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.search-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-muted);
  margin-left: 8px;
}

.search-icon-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-color);
}

.search-icon {
  width: 20px;
  height: 20px;
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  color: var(--text-primary);
  outline: none;
}

.search-bar input::placeholder {
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .header-center {
    display: none;
  }

  .header-container {
    padding: 0 16px;
  }
}
</style>
