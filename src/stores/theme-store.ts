import { defineStore } from 'pinia'
import { ref } from 'vue'

export type IconStyle = 'colorful' | 'minimal'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref<boolean>(false)
  const iconStyle = ref<IconStyle>('colorful')

  const toggleTheme = () => {
    isDark.value = !isDark.value

    document.documentElement.style.opacity = '0'

    requestAnimationFrame(() => {
      document.documentElement.classList.toggle('dark', isDark.value)
      document.documentElement.style.opacity = '1'
    })
  }

  const toggleIconStyle = () => {
    iconStyle.value = iconStyle.value === 'colorful' ? 'minimal' : 'colorful'
  }

  const initTheme = () => {
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  return {
    isDark,
    iconStyle,
    toggleTheme,
    toggleIconStyle,
    initTheme
  }
}, {
  persist: {
    key: 'theme-store',
    storage: localStorage,
    paths: ['isDark', 'iconStyle']
  }
})
