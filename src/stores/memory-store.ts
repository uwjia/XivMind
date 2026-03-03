import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { memoryService } from '@/services/memory'
import type {
  CoreMemory,
  CoreMemoryUpdate,
  RecallMemory,
  ArchivalMemory,
  ArchivalMemoryCreate,
  MemoryStats,
  MemorySearchResult,
} from '@/types/memory'

export const useMemoryStore = defineStore('memory', () => {
  const coreMemory = ref<CoreMemory | null>(null)
  const stats = ref<MemoryStats | null>(null)
  const recallMemories = ref<RecallMemory[]>([])
  const archivalMemories = ref<ArchivalMemory[]>([])
  const searchResults = ref<MemorySearchResult[]>([])
  const recommendedSkills = ref<string[]>([])
  
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  const hasCoreMemory = computed(() => coreMemory.value !== null)
  const totalMemories = computed(() => stats.value?.total_memories || 0)
  const researchInterests = computed(() => coreMemory.value?.research_interests || [])
  const languagePreference = computed(() => coreMemory.value?.language_preference || 'en-US')

  async function fetchCoreMemory(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      coreMemory.value = await memoryService.getCoreMemory()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch core memory'
      console.error('Failed to fetch core memory:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function updateCoreMemory(update: CoreMemoryUpdate): Promise<boolean> {
    try {
      isSaving.value = true
      error.value = null
      const updated = await memoryService.updateCoreMemory(update)
      coreMemory.value = updated
      await fetchStats()
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update core memory'
      console.error('Failed to update core memory:', e)
      return false
    } finally {
      isSaving.value = false
    }
  }

  async function fetchStats(): Promise<void> {
    try {
      stats.value = await memoryService.getMemoryStats()
    } catch (e) {
      console.error('Failed to fetch memory stats:', e)
    }
  }

  async function fetchRecallMemories(limit: number = 20, offset: number = 0): Promise<void> {
    try {
      isLoading.value = true
      recallMemories.value = await memoryService.getRecallMemories(limit, offset)
    } catch (e) {
      console.error('Failed to fetch recall memories:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function searchMemories(query: string, topK: number = 5): Promise<MemorySearchResult[]> {
    try {
      isLoading.value = true
      searchResults.value = await memoryService.searchMemories(query, topK)
      return searchResults.value
    } catch (e) {
      console.error('Failed to search memories:', e)
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRecallMemory(memoryId: string): Promise<boolean> {
    try {
      const success = await memoryService.deleteRecallMemory(memoryId)
      if (success) {
        recallMemories.value = recallMemories.value.filter(m => m.memory_id !== memoryId)
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to delete recall memory:', e)
      return false
    }
  }

  async function fetchArchivalMemories(limit: number = 50, offset: number = 0): Promise<void> {
    try {
      isLoading.value = true
      archivalMemories.value = await memoryService.getArchivalMemories(limit, offset)
    } catch (e) {
      console.error('Failed to fetch archival memories:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function createArchivalMemory(data: ArchivalMemoryCreate): Promise<ArchivalMemory | null> {
    try {
      isSaving.value = true
      const memory = await memoryService.createArchivalMemory(data)
      archivalMemories.value.unshift(memory)
      await fetchStats()
      return memory
    } catch (e) {
      console.error('Failed to create archival memory:', e)
      return null
    } finally {
      isSaving.value = false
    }
  }

  async function deleteArchivalMemory(memoryId: string): Promise<boolean> {
    try {
      const success = await memoryService.deleteArchivalMemory(memoryId)
      if (success) {
        archivalMemories.value = archivalMemories.value.filter(m => m.memory_id !== memoryId)
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to delete archival memory:', e)
      return false
    }
  }

  async function clearAllMemories(): Promise<boolean> {
    try {
      isLoading.value = true
      const success = await memoryService.clearAllMemories()
      if (success) {
        coreMemory.value = null
        recallMemories.value = []
        archivalMemories.value = []
        searchResults.value = []
        stats.value = {
          core_memory_exists: false,
          recall_memory_count: 0,
          archival_memory_count: 0,
          total_memories: 0,
        }
      }
      return success
    } catch (e) {
      console.error('Failed to clear all memories:', e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function clearCoreMemory(): Promise<boolean> {
    try {
      isLoading.value = true
      const success = await memoryService.clearCoreMemory()
      if (success) {
        coreMemory.value = null
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to clear core memory:', e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function clearRecallMemories(): Promise<boolean> {
    try {
      isLoading.value = true
      const success = await memoryService.clearRecallMemories()
      if (success) {
        recallMemories.value = []
        searchResults.value = []
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to clear recall memories:', e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function clearArchivalMemories(): Promise<boolean> {
    try {
      isLoading.value = true
      const success = await memoryService.clearArchivalMemories()
      if (success) {
        archivalMemories.value = []
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to clear archival memories:', e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRecommendedSkills(): Promise<void> {
    try {
      recommendedSkills.value = await memoryService.getRecommendedSkills()
    } catch (e) {
      console.error('Failed to fetch recommended skills:', e)
    }
  }

  async function addResearchInterest(interest: string): Promise<boolean> {
    if (!interest.trim()) return false
    const currentInterests = coreMemory.value?.research_interests || []
    if (currentInterests.includes(interest.trim())) return false
    
    return updateCoreMemory({
      research_interests: [...currentInterests, interest.trim()],
    })
  }

  async function removeResearchInterest(interest: string): Promise<boolean> {
    const currentInterests = coreMemory.value?.research_interests || []
    return updateCoreMemory({
      research_interests: currentInterests.filter(i => i !== interest),
    })
  }

  async function setLanguagePreference(preference: string): Promise<boolean> {
    return updateCoreMemory({ language_preference: preference })
  }

  async function setSummaryStyle(style: 'detailed' | 'brief' | 'bullet_points'): Promise<boolean> {
    return updateCoreMemory({ summary_style: style })
  }

  async function init(): Promise<void> {
    await Promise.all([
      fetchCoreMemory(),
      fetchStats(),
    ])
  }

  function $reset(): void {
    coreMemory.value = null
    stats.value = null
    recallMemories.value = []
    archivalMemories.value = []
    searchResults.value = []
    recommendedSkills.value = []
    isLoading.value = false
    isSaving.value = false
    error.value = null
  }

  return {
    coreMemory,
    stats,
    recallMemories,
    archivalMemories,
    searchResults,
    recommendedSkills,
    isLoading,
    isSaving,
    error,
    hasCoreMemory,
    totalMemories,
    researchInterests,
    languagePreference,
    fetchCoreMemory,
    updateCoreMemory,
    fetchStats,
    fetchRecallMemories,
    searchMemories,
    deleteRecallMemory,
    fetchArchivalMemories,
    createArchivalMemory,
    deleteArchivalMemory,
    clearAllMemories,
    clearCoreMemory,
    clearRecallMemories,
    clearArchivalMemories,
    fetchRecommendedSkills,
    addResearchInterest,
    removeResearchInterest,
    setLanguagePreference,
    setSummaryStyle,
    init,
    $reset,
  }
})
