import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Note, NotePanelPosition, NotePanelSize, ExportFormat } from '@/types/note'

const generateId = () => `note_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

export const useNoteStore = defineStore('note', () => {
  const notes = ref<Note[]>([])
  const position = ref<NotePanelPosition>({ x: 20, y: 80 })
  const size = ref<NotePanelSize>({ width: 340, height: 450 })
  const isMinimized = ref(false)
  const isVisible = ref(false)
  const selectedIds = ref<string[]>([])
  const filterTag = ref<string | null>(null)
  const searchQuery = ref('')
  const editingNoteId = ref<string | null>(null)
  const noteBtnPosition = ref({ x: 0, y: 0 })
  const hasUserMovedPanel = ref(false)

  const allTags = computed(() => {
    const tagSet = new Set<string>()
    notes.value.forEach(note => {
      note.tags.forEach(tag => tagSet.add(tag))
    })
    return Array.from(tagSet).sort()
  })

  const filteredNotes = computed(() => {
    let result = [...notes.value]

    if (filterTag.value) {
      result = result.filter(note => note.tags.includes(filterTag.value!))
    }

    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(note =>
        note.content.toLowerCase().includes(query) ||
        note.tags.some(tag => tag.toLowerCase().includes(query)) ||
        note.source?.toLowerCase().includes(query)
      )
    }

    return result.sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  })

  const isAllSelected = computed(() => {
    if (filteredNotes.value.length === 0) return false
    return filteredNotes.value.every(note => selectedIds.value.includes(note.id))
  })

  const addNote = (content: string, tags: string[] = [], source?: string, color?: string) => {
    const now = new Date().toISOString()
    const note: Note = {
      id: generateId(),
      content,
      createdAt: now,
      updatedAt: now,
      tags,
      source,
      color
    }
    notes.value.unshift(note)
    return note
  }

  const updateNote = (id: string, content: string, tags?: string[]) => {
    const index = notes.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notes.value[index] = {
        ...notes.value[index],
        content,
        tags: tags ?? notes.value[index].tags,
        updatedAt: new Date().toISOString()
      }
    }
  }

  const deleteNote = (id: string) => {
    const index = notes.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notes.value.splice(index, 1)
      selectedIds.value = selectedIds.value.filter(sid => sid !== id)
    }
  }

  const deleteSelected = () => {
    notes.value = notes.value.filter(n => !selectedIds.value.includes(n.id))
    selectedIds.value = []
  }

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {
      return false
    }
  }

  const formatNoteForCopy = (note: Note, includeTimestamps = false, includeTags = true, includeSource = true): string => {
    let result = note.content
    if (includeTimestamps) {
      result = `[${formatDate(new Date(note.createdAt))}] ${result}`
    }
    if (includeTags && note.tags.length > 0) {
      result += `\nTags: ${note.tags.join(', ')}`
    }
    if (includeSource && note.source) {
      result += `\nSource: ${note.source}`
    }
    return result
  }

  const copyNote = async (id: string): Promise<boolean> => {
    const note = notes.value.find(n => n.id === id)
    if (note) {
      const text = formatNoteForCopy(note)
      return copyToClipboard(text)
    }
    return false
  }

  const copySelected = async (): Promise<boolean> => {
    const selectedNotes = notes.value.filter(n => selectedIds.value.includes(n.id))
    if (selectedNotes.length > 0) {
      const text = selectedNotes.map(n => formatNoteForCopy(n)).join('\n\n---\n\n')
      return copyToClipboard(text)
    }
    return false
  }

  const copyAll = async (): Promise<boolean> => {
    if (notes.value.length > 0) {
      const text = notes.value.map(n => formatNoteForCopy(n)).join('\n\n---\n\n')
      return copyToClipboard(text)
    }
    return false
  }

  const toggleSelection = (id: string) => {
    const index = selectedIds.value.indexOf(id)
    if (index === -1) {
      selectedIds.value.push(id)
    } else {
      selectedIds.value.splice(index, 1)
    }
  }

  const selectAll = () => {
    selectedIds.value = filteredNotes.value.map(n => n.id)
  }

  const deselectAll = () => {
    selectedIds.value = []
  }

  const toggleSelectAll = () => {
    if (isAllSelected.value) {
      selectedIds.value = []
    } else {
      selectedIds.value = filteredNotes.value.map(n => n.id)
    }
  }

  const clearSelection = () => {
    selectedIds.value = []
  }

  const setFilter = (tag: string | null) => {
    filterTag.value = tag
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const exportNotes = (format: ExportFormat, noteIds?: string[]): string => {
    const notesToExport = noteIds
      ? notes.value.filter(n => noteIds.includes(n.id))
      : notes.value

    switch (format) {
      case 'json':
        return JSON.stringify(notesToExport, null, 2)

      case 'markdown':
        return notesToExport.map(n => {
          let md = `## ${formatDate(new Date(n.createdAt))}\n\n${n.content}`
          if (n.tags.length > 0) {
            md += `\n\n**Tags:** ${n.tags.map(t => `\`${t}\``).join(' ')}`
          }
          if (n.source) {
            md += `\n\n**Source:** ${n.source}`
          }
          return md
        }).join('\n\n---\n\n')

      case 'text':
      default:
        return notesToExport.map(n => formatNoteForCopy(n)).join('\n\n---\n\n')
    }
  }

  const importNotes = (data: string): boolean => {
    try {
      const parsed = JSON.parse(data)
    const notesToImport = Array.isArray(parsed) ? parsed : [parsed]

      notesToImport.forEach((n: Partial<Note>) => {
        if (n.content) {
          addNote(n.content, n.tags || [], n.source, n.color)
        }
      })
      return true
    } catch {
      return false
    }
  }

  const togglePanel = () => {
    isVisible.value = !isVisible.value
  }

  const showPanel = () => {
    isVisible.value = true
  }

  const hidePanel = () => {
    isVisible.value = false
  }

  const updatePosition = (x: number, y: number) => {
    position.value = { x, y }
    hasUserMovedPanel.value = true
  }

  const updateSize = (width: number, height: number) => {
    size.value = { width, height }
  }

  const setNoteBtnPosition = (x: number, y: number) => {
    noteBtnPosition.value = { x, y }
  }

  const resetToDefaultPosition = () => {
    const panelWidth = size.value.width
    const newX = Math.max(10, noteBtnPosition.value.x - panelWidth)
    const newY = noteBtnPosition.value.y + 8
    position.value = { x: newX, y: newY }
    hasUserMovedPanel.value = false
  }

  const toggleMinimize = () => {
    isMinimized.value = !isMinimized.value
  }

  const startEditing = (id: string | null) => {
    editingNoteId.value = id
  }

  const getNoteById = (id: string): Note | undefined => {
    return notes.value.find(n => n.id === id)
  }

  return {
    notes,
    position,
    size,
    isMinimized,
    isVisible,
    selectedIds,
    filterTag,
    searchQuery,
    editingNoteId,
    noteBtnPosition,
    hasUserMovedPanel,
    allTags,
    filteredNotes,
    isAllSelected,
    addNote,
    updateNote,
    deleteNote,
    deleteSelected,
    copyNote,
    copySelected,
    copyAll,
    toggleSelection,
    selectAll,
    deselectAll,
    toggleSelectAll,
    clearSelection,
    setFilter,
    setSearchQuery,
    exportNotes,
    importNotes,
    togglePanel,
    showPanel,
    hidePanel,
    updatePosition,
    updateSize,
    setNoteBtnPosition,
    resetToDefaultPosition,
    toggleMinimize,
    startEditing,
    getNoteById
  }
}, {
  persist: {
    key: 'xivmind-notes',
    paths: ['notes', 'position', 'size', 'isMinimized']
  }
})
