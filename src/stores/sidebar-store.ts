import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref<boolean>(false)
  const isMobileOpen = ref<boolean>(false)

  const toggleSidebar = () => {
    isCollapsed.value = !isCollapsed.value
  }

  const collapseSidebar = () => {
    isCollapsed.value = true
  }

  const expandSidebar = () => {
    isCollapsed.value = false
  }

  const toggleMobileSidebar = () => {
    isMobileOpen.value = !isMobileOpen.value
  }

  const closeMobileSidebar = () => {
    isMobileOpen.value = false
  }

  return {
    isCollapsed,
    isMobileOpen,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    toggleMobileSidebar,
    closeMobileSidebar
  }
}, {
  persist: {
    key: 'sidebar-store',
    storage: localStorage,
    paths: ['isCollapsed']
  }
})
