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
  MemoryConfig,
  MemoryCategory,
  MemoryContextResult,
} from '@/types/memory'

const DEFAULT_CONFIG: MemoryConfig = {
  auto_capture: true,
  auto_recall: true,
  capture_max_chars: 500,
  recall_top_k: 5,
  recall_min_score: 0.7,
  auto_forget_days: 30,
  importance_threshold: 0.3,
  extract: false,
}

export const useMemoryStore = defineStore('memory', () => {
  const coreMemory = ref<CoreMemory | null>(null)
  const stats = ref<MemoryStats | null>(null)
  const recallMemories = ref<RecallMemory[]>([])
  const archivalMemories = ref<ArchivalMemory[]>([])
  const searchResults = ref<MemorySearchResult[]>([])
  const recommendedSkills = ref<string[]>([])
  const config = ref<MemoryConfig>(DEFAULT_CONFIG)
  
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  const hasCoreMemory = computed(() => coreMemory.value !== null)
  const totalMemories = computed(() => stats.value?.total_memories || 0)
  const researchInterests = computed(() => coreMemory.value?.research_interests || [])
  const languagePreference = computed(() => coreMemory.value?.language_preference || 'en-US')
  const autoCaptureEnabled = computed(() => config.value.auto_capture)
  const autoRecallEnabled = computed(() => config.value.auto_recall)

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
          auto_created_count: 0,
          by_category: {},
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

  async function fetchConfig(): Promise<void> {
    try {
      config.value = await memoryService.getMemoryConfig()
    } catch (e) {
      console.error('Failed to fetch memory config:', e)
    }
  }

  async function updateConfig(newConfig: Partial<MemoryConfig>): Promise<boolean> {
    try {
      config.value = await memoryService.updateMemoryConfig(newConfig)
      return true
    } catch (e) {
      console.error('Failed to update memory config:', e)
      return false
    }
  }

  async function storeMemory(
    text: string,
    category?: MemoryCategory,
    importance?: number
  ): Promise<RecallMemory | null> {
    try {
      const memory = await memoryService.storeMemory(text, category, importance)
      recallMemories.value.unshift(memory)
      await fetchStats()
      return memory
    } catch (e) {
      console.error('Failed to store memory:', e)
      return null
    }
  }

  async function recallMemoriesByQuery(query: string, limit?: number): Promise<MemorySearchResult[]> {
    try {
      return await memoryService.recallMemories(query, limit)
    } catch (e) {
      console.error('Failed to recall memories:', e)
      return []
    }
  }

  async function forgetMemory(memoryId?: string): Promise<boolean> {
    try {
      const success = await memoryService.forgetMemory(memoryId)
      if (success && memoryId) {
        recallMemories.value = recallMemories.value.filter(m => m.memory_id !== memoryId)
        await fetchStats()
      }
      return success
    } catch (e) {
      console.error('Failed to forget memory:', e)
      return false
    }
  }

  async function getMemoryContext(query: string): Promise<MemoryContextResult> {
    try {
      return await memoryService.getMemoryContextResult(query)
    } catch (e) {
      console.error('Failed to get memory context:', e)
      return { memories: [], context_string: '' }
    }
  }

  async function cleanupExpiredMemories(): Promise<number> {
    try {
      const result = await memoryService.cleanupExpiredMemories()
      await fetchStats()
      return result.deleted
    } catch (e) {
      console.error('Failed to cleanup expired memories:', e)
      return 0
    }
  }

  async function init(): Promise<void> {
    await Promise.all([
      fetchCoreMemory(),
      fetchStats(),
      fetchConfig(),
    ])
  }

  function $reset(): void {
    coreMemory.value = null
    stats.value = null
    recallMemories.value = []
    archivalMemories.value = []
    searchResults.value = []
    recommendedSkills.value = []
    config.value = DEFAULT_CONFIG
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
    config,
    isLoading,
    isSaving,
    error,
    hasCoreMemory,
    totalMemories,
    researchInterests,
    languagePreference,
    autoCaptureEnabled,
    autoRecallEnabled,
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
    fetchConfig,
    updateConfig,
    storeMemory,
    recallMemoriesByQuery,
    forgetMemory,
    getMemoryContext,
    cleanupExpiredMemories,
    init,
    $reset,
  }
})
