import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref<boolean>(false)
  const isMobileOpen = ref<boolean>(false)
  const isDatePickerOpen = ref<boolean>(false)
  const isCategoryPickerOpen = ref<boolean>(false)

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

  const openDatePicker = () => {
    isDatePickerOpen.value = true
  }

  const closeDatePicker = () => {
    isDatePickerOpen.value = false
  }

  const toggleDatePicker = () => {
    isDatePickerOpen.value = !isDatePickerOpen.value
  }

  const openCategoryPicker = () => {
    isCategoryPickerOpen.value = true
  }

  const closeCategoryPicker = () => {
    isCategoryPickerOpen.value = false
  }

  const toggleCategoryPicker = () => {
    isCategoryPickerOpen.value = !isCategoryPickerOpen.value
  }

  return {
    isCollapsed,
    isMobileOpen,
    isDatePickerOpen,
    isCategoryPickerOpen,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    openDatePicker,
    closeDatePicker,
    toggleDatePicker,
    openCategoryPicker,
    closeCategoryPicker,
    toggleCategoryPicker
  }
}, {
  persist: {
    key: 'sidebar-store',
    storage: localStorage,
    pick: ['isCollapsed']
  }
})
