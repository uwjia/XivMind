import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref<boolean>(false)
  const isMobileOpen = ref<boolean>(false)
  const forceCollapsed = ref<boolean>(false)

  const effectiveCollapsed = computed(() => {
    return forceCollapsed.value || isCollapsed.value
  })

  const toggleSidebar = () => {
    if (!forceCollapsed.value) {
      isCollapsed.value = !isCollapsed.value
    }
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

  const enterForceCollapse = () => {
    forceCollapsed.value = true
  }

  const exitForceCollapse = () => {
    forceCollapsed.value = false
  }

  return {
    isCollapsed,
    isMobileOpen,
    forceCollapsed,
    effectiveCollapsed,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    enterForceCollapse,
    exitForceCollapse
  }
}, {
  persist: {
    key: 'sidebar-store',
    storage: localStorage,
    paths: ['isCollapsed']
  }
})
