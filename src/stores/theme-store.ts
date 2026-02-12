import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref<boolean>(false)

  const toggleTheme = () => {
    isDark.value = !isDark.value

    document.documentElement.style.opacity = '0'

    requestAnimationFrame(() => {
      document.documentElement.classList.toggle('dark', isDark.value)
      document.documentElement.style.opacity = '1'
    })
  }

  const initTheme = () => {
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  return {
    isDark,
    toggleTheme,
    initTheme
  }
}, {
  persist: {
    key: 'theme-store',
    storage: localStorage,
    pick: ['isDark']
  }
})
