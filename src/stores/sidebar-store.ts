import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref<boolean>(false)
  const isMobileOpen = ref<boolean>(false)
  const forceCollapsed = ref<boolean>(false)
  const previousCollapsedState = ref<boolean | null>(null)

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
    previousCollapsedState.value = isCollapsed.value
    forceCollapsed.value = true
  }

  const exitForceCollapse = () => {
    forceCollapsed.value = false
    if (previousCollapsedState.value !== null) {
      isCollapsed.value = previousCollapsedState.value
      previousCollapsedState.value = null
    }
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
