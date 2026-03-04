import { ref } from 'vue'
import { useMemoryStore } from '@/stores/memory-store'

export function useMemoryKnowledge() {
  const memoryStore = useMemoryStore()
  
  const showNoteEditor = ref(false)
  
  const deleteKnowledge = async (memoryId: string) => {
    await memoryStore.deleteArchivalMemory(memoryId)
  }
  
  const onNoteSaved = () => {
    showNoteEditor.value = false
  }
  
  const formatDate = (dateStr: string): string => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
  }
  
  return {
    showNoteEditor,
    deleteKnowledge,
    onNoteSaved,
    formatDate,
  }
}
