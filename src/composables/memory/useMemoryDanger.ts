import { ref } from 'vue'
import { useMemoryStore } from '@/stores/memory-store'

export function useMemoryDanger() {
  const memoryStore = useMemoryStore()
  
  const showClearConfirm = ref(false)
  const showClearCoreConfirm = ref(false)
  const showClearRecallConfirm = ref(false)
  const showClearArchivalConfirm = ref(false)
  
  const confirmClearCore = () => {
    showClearCoreConfirm.value = true
  }
  
  const confirmClearRecall = () => {
    showClearRecallConfirm.value = true
  }
  
  const confirmClearArchival = () => {
    showClearArchivalConfirm.value = true
  }
  
  const clearAllMemories = async () => {
    await memoryStore.clearAllMemories()
    showClearConfirm.value = false
  }
  
  const clearCoreMemory = async () => {
    await memoryStore.clearCoreMemory()
    showClearCoreConfirm.value = false
  }
  
  const clearRecallMemories = async () => {
    await memoryStore.clearRecallMemories()
    showClearRecallConfirm.value = false
  }
  
  const clearArchivalMemories = async () => {
    await memoryStore.clearArchivalMemories()
    showClearArchivalConfirm.value = false
  }
  
  return {
    showClearConfirm,
    showClearCoreConfirm,
    showClearRecallConfirm,
    showClearArchivalConfirm,
    confirmClearCore,
    confirmClearRecall,
    confirmClearArchival,
    clearAllMemories,
    clearCoreMemory,
    clearRecallMemories,
    clearArchivalMemories,
  }
}
