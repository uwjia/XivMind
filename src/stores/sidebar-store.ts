import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref<boolean>(false)
  const isMobileOpen = ref<boolean>(false)
  const forceCollapsed = ref<boolean>(false)
  const userCollapsed = ref<boolean>(false)

  const effectiveCollapsed = computed(() => {
    return forceCollapsed.value || isCollapsed.value
  })

  const toggleSidebar = () => {
    if (!forceCollapsed.value) {
      isCollapsed.value = !isCollapsed.value
      userCollapsed.value = isCollapsed.value
    }
  }

  const collapseSidebar = () => {
    isCollapsed.value = true
    userCollapsed.value = true
  }

  const expandSidebar = () => {
    isCollapsed.value = false
    userCollapsed.value = false
  }

  const autoExpand = () => {
    if (!userCollapsed.value && !forceCollapsed.value) {
      isCollapsed.value = false
    }
  }

  const autoCollapse = () => {
    isCollapsed.value = true
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
    userCollapsed,
    effectiveCollapsed,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    autoExpand,
    autoCollapse,
    toggleMobileSidebar,
    closeMobileSidebar,
    enterForceCollapse,
    exitForceCollapse
  }
}, {
  persist: {
    key: 'sidebar-store',
    storage: localStorage,
    paths: ['isCollapsed', 'userCollapsed']
  }
})
