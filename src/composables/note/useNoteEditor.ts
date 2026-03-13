import { ref, computed } from 'vue'
import { useNoteStore } from '@/stores/note-store'
import { useToastStore } from '@/stores/toast-store'

export function useNoteEditor() {
  const noteStore = useNoteStore()
  const toastStore = useToastStore()

  const isEditing = ref(false)
  const editingNoteId = ref<string | null>(null)
  const editingContent = ref('')
  const editingTags = ref<string[]>([])

  const isEditingExisting = computed(() => !!editingNoteId.value)

  const startAdd = () => {
    isEditing.value = true
    editingNoteId.value = null
    editingContent.value = ''
    editingTags.value = []
  }

  const startEdit = (id: string) => {
    const note = noteStore.getNoteById(id)
    if (note) {
      isEditing.value = true
      editingNoteId.value = id
      editingContent.value = note.content
      editingTags.value = [...note.tags]
    }
  }

  const cancel = () => {
    isEditing.value = false
    editingNoteId.value = null
    editingContent.value = ''
    editingTags.value = []
  }

  const save = (content: string, tags: string[]) => {
    if (editingNoteId.value) {
      noteStore.updateNote(editingNoteId.value, content, tags)
      toastStore.showSuccess('Note updated')
    } else {
      noteStore.addNote(content, tags)
      toastStore.showSuccess('Note added')
    }
    cancel()
  }

  return {
    isEditing,
    editingNoteId,
    editingContent,
    editingTags,
    isEditingExisting,
    startAdd,
    startEdit,
    cancel,
    save
  }
}
