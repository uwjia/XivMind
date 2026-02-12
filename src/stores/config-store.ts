import { defineStore } from 'pinia'
import { ref } from 'vue'
// 导入 TypeScript 版本的配置文件
import { config as defaultConfig } from '../config/app'

export const useConfigStore = defineStore('config', () => {
  const maxResults = ref<number>(defaultConfig.maxResults)
  const defaultCategory = ref<string>(defaultConfig.defaultCategory)
  const defaultDateFilter = ref<string>(defaultConfig.defaultDateFilter)
  const useSimpleCard = ref<boolean>(false)

  const setMaxResults = (value: number) => {
    maxResults.value = value
    localStorage.setItem('maxResults', value.toString())
  }

  const setDefaultCategory = (value: string) => {
    defaultCategory.value = value
    localStorage.setItem('defaultCategory', value)
  }

  const setDefaultDateFilter = (value: string) => {
    defaultDateFilter.value = value
    localStorage.setItem('defaultDateFilter', value)
  }

  const setUseSimpleCard = (value: boolean) => {
    useSimpleCard.value = value
    localStorage.setItem('useSimpleCard', value.toString())
  }

  const resetToDefaults = () => {
    maxResults.value = defaultConfig.maxResults
    defaultCategory.value = defaultConfig.defaultCategory
    defaultDateFilter.value = defaultConfig.defaultDateFilter
    useSimpleCard.value = false
    localStorage.setItem('maxResults', defaultConfig.maxResults.toString())
    localStorage.setItem('defaultCategory', defaultConfig.defaultCategory)
    localStorage.setItem('defaultDateFilter', defaultConfig.defaultDateFilter)
    localStorage.setItem('useSimpleCard', 'false')
  }

  const initConfig = () => {
    const savedMaxResults = localStorage.getItem('maxResults')
    if (savedMaxResults) {
      maxResults.value = parseInt(savedMaxResults)
    }

    const savedCategory = localStorage.getItem('defaultCategory')
    if (savedCategory) {
      defaultCategory.value = savedCategory
    }

    const savedDateFilter = localStorage.getItem('defaultDateFilter')
    if (savedDateFilter) {
      defaultDateFilter.value = savedDateFilter
    }

    const savedUseSimpleCard = localStorage.getItem('useSimpleCard')
    if (savedUseSimpleCard) {
      useSimpleCard.value = savedUseSimpleCard === 'true'
    }
  }

  return {
    maxResults,
    defaultCategory,
    defaultDateFilter,
    useSimpleCard,
    setMaxResults,
    setDefaultCategory,
    setDefaultDateFilter,
    setUseSimpleCard,
    resetToDefaults,
    initConfig
  }
})
