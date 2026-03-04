import { ref } from 'vue'
import { useMemoryStore } from '@/stores/memory-store'
import { useToastStore } from '@/stores/toast-store'

export function useMemoryConfig() {
  const memoryStore = useMemoryStore()
  const toastStore = useToastStore()
  
  const isSaving = ref(false)
  const isCleaningUp = ref(false)
  const cleanupResult = ref<number | null>(null)
  
  const saveConfig = async () => {
    isSaving.value = true
    try {
      await memoryStore.updateConfig(memoryStore.config)
      toastStore.showSuccess('Configuration saved successfully')
    } catch {
      toastStore.showError('Failed to save configuration')
    } finally {
      isSaving.value = false
    }
  }
  
  const runCleanup = async () => {
    isCleaningUp.value = true
    cleanupResult.value = null
    try {
      const deleted = await memoryStore.cleanupExpiredMemories()
      cleanupResult.value = deleted
      if (deleted > 0) {
        toastStore.showSuccess(`Cleaned up ${deleted} expired memories`)
      } else {
        toastStore.showInfo('No expired memories to clean up')
      }
    } catch {
      toastStore.showError('Failed to cleanup expired memories')
    } finally {
      isCleaningUp.value = false
    }
  }
  
  return {
    isSaving,
    isCleaningUp,
    cleanupResult,
    saveConfig,
    runCleanup,
  }
}
