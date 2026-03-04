import { ref } from 'vue'
import { useMemoryStore } from '@/stores/memory-store'
import type { MemoryCategory } from '@/types/memory'

export function useMemoryHistory() {
  const memoryStore = useMemoryStore()
  
  const searchQuery = ref('')
  const hasSearched = ref(false)
  
  const showStoreMemory = ref(false)
  const newMemoryText = ref('')
  const newMemoryCategory = ref<MemoryCategory>('fact')
  const newMemoryImportance = ref(0.7)
  const isStoringMemory = ref(false)
  
  const memoryContextResult = ref('')
  const isGettingContext = ref(false)
  
  const memoryCategories: { value: MemoryCategory; label: string }[] = [
    { value: 'fact', label: 'Fact' },
    { value: 'preference', label: 'Preference' },
    { value: 'context', label: 'Context' },
    { value: 'insight', label: 'Insight' },
    { value: 'task', label: 'Task' },
  ]
  
  const recallMemories = async () => {
    if (!searchQuery.value.trim()) return
    
    hasSearched.value = true
    memoryStore.searchResults = await memoryStore.recallMemoriesByQuery(
      searchQuery.value.trim(),
      10
    )
  }
  
  const clearSearch = () => {
    searchQuery.value = ''
    memoryStore.searchResults = []
    hasSearched.value = false
  }
  
  const openStoreMemory = () => {
    showStoreMemory.value = true
    newMemoryText.value = ''
    newMemoryCategory.value = 'fact'
    newMemoryImportance.value = 0.7
  }
  
  const closeStoreMemory = () => {
    showStoreMemory.value = false
  }
  
  const storeNewMemory = async () => {
    if (!newMemoryText.value.trim()) return
    
    isStoringMemory.value = true
    try {
      await memoryStore.storeMemory(
        newMemoryText.value.trim(),
        newMemoryCategory.value,
        newMemoryImportance.value
      )
      showStoreMemory.value = false
      newMemoryText.value = ''
      await memoryStore.fetchRecallMemories()
    } finally {
      isStoringMemory.value = false
    }
  }
  
  const forgetSelectedMemory = async (memoryId?: string) => {
    await memoryStore.forgetMemory(memoryId)
    await memoryStore.fetchRecallMemories()
  }
  
  const getMemoryContextForQuery = async () => {
    if (!searchQuery.value.trim()) return
    
    isGettingContext.value = true
    try {
      const result = await memoryStore.getMemoryContext(searchQuery.value.trim())
      memoryContextResult.value = result.context_string
    } finally {
      isGettingContext.value = false
    }
  }
  
  const clearContextResult = () => {
    memoryContextResult.value = ''
  }
  
  const deleteHistory = async (memoryId: string) => {
    await memoryStore.deleteRecallMemory(memoryId)
  }
  
  const formatTime = (timestamp: string): string => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) {
      const hours = Math.floor(diff / (1000 * 60 * 60))
      if (hours === 0) {
        const minutes = Math.floor(diff / (1000 * 60))
        return `${minutes}m ago`
      }
      return `${hours}h ago`
    } else if (days === 1) {
      return 'Yesterday'
    } else if (days < 7) {
      return `${days}d ago`
    } else {
      return date.toLocaleDateString()
    }
  }
  
  return {
    searchQuery,
    hasSearched,
    showStoreMemory,
    newMemoryText,
    newMemoryCategory,
    newMemoryImportance,
    isStoringMemory,
    memoryContextResult,
    isGettingContext,
    memoryCategories,
    recallMemories,
    clearSearch,
    openStoreMemory,
    closeStoreMemory,
    storeNewMemory,
    forgetSelectedMemory,
    getMemoryContextForQuery,
    clearContextResult,
    deleteHistory,
    formatTime,
  }
}
