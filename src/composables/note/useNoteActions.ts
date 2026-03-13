import { useNoteStore } from '@/stores/note-store'
import { useToastStore } from '@/stores/toast-store'

export function useNoteActions() {
  const noteStore = useNoteStore()
  const toastStore = useToastStore()

  const deleteNote = (id: string) => {
    noteStore.deleteNote(id)
    toastStore.showInfo('Note deleted')
  }

  const deleteSelected = () => {
    const count = noteStore.selectedIds.length
    noteStore.deleteSelected()
    toastStore.showInfo(`${count} notes deleted`)
  }

  const copyNote = async (id: string) => {
    const success = await noteStore.copyNote(id)
    if (success) {
      toastStore.showSuccess('Copied to clipboard')
    }
    return success
  }

  const copySelected = async () => {
    const success = await noteStore.copySelected()
    if (success) {
      toastStore.showSuccess('Copied to clipboard')
    }
    return success
  }

  const setSearchQuery = (query: string) => {
    noteStore.setSearchQuery(query)
  }

  const setFilter = (tag: string | null) => {
    noteStore.setFilter(tag)
  }

  return {
    deleteNote,
    deleteSelected,
    copyNote,
    copySelected,
    setSearchQuery,
    setFilter
  }
}
