import { useNoteStore } from '@/stores/note-store'

export function useNoteSelection() {
  const noteStore = useNoteStore()

  const toggleSelection = (id: string) => {
    noteStore.toggleSelection(id)
  }

  const toggleSelectAll = () => {
    noteStore.toggleSelectAll()
  }

  const clearSelection = () => {
    noteStore.clearSelection()
  }

  return {
    toggleSelection,
    toggleSelectAll,
    clearSelection
  }
}
