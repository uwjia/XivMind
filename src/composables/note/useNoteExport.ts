import { ref, computed, type Ref } from 'vue'
import type { ExportFormat, Note } from '@/types/note'

export interface ExportOptions {
  includeTimestamps: Ref<boolean>
  includeTags: Ref<boolean>
  includeSource: Ref<boolean>
}

const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

export function useNoteExport() {
  const format = ref<ExportFormat>('text')
  const includeTimestamps = ref(true)
  const includeTags = ref(true)
  const includeSource = ref(true)

  const generateContent = (notes: Note[]): string => {
    switch (format.value) {
      case 'json':
        return JSON.stringify(notes, null, 2)

      case 'markdown':
        return notes.map(n => {
          let md = `## ${formatDate(new Date(n.createdAt))}\n\n${n.content}`
          if (includeTags.value && n.tags.length > 0) {
            md += `\n\n**Tags:** ${n.tags.map(t => `\`${t}\``).join(' ')}`
          }
          if (includeSource.value && n.source) {
            md += `\n\n**Source:** ${n.source}`
          }
          return md
        }).join('\n\n---\n\n')

      case 'text':
      default:
        return notes.map(n => {
          let text = n.content
          if (includeTimestamps.value) {
            text = `[${formatDate(new Date(n.createdAt))}] ${text}`
          }
          if (includeTags.value && n.tags.length > 0) {
            text += `\nTags: ${n.tags.join(', ')}`
          }
          if (includeSource.value && n.source) {
            text += `\nSource: ${n.source}`
          }
          return text
        }).join('\n\n---\n\n')
    }
  }

  const generatePreview = (notes: Note[], maxNotes: number = 3): string => {
    return generateContent(notes.slice(0, maxNotes))
  }

  const copyToClipboard = async (notes: Note[]): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(generateContent(notes))
      return true
    } catch {
      return false
    }
  }

  const downloadFile = (notes: Note[], filename?: string): void => {
    const content = generateContent(notes)
    const extension = format.value === 'json' ? 'json' : format.value === 'markdown' ? 'md' : 'txt'
    const mimeType = format.value === 'json' ? 'application/json' : 'text/plain'

    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `xivmind-notes-${new Date().toISOString().slice(0, 10)}.${extension}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const createPreviewComputed = (notes: Ref<Note[]>, maxNotes: number = 3) => {
    return computed(() => generatePreview(notes.value, maxNotes))
  }

  return {
    format,
    includeTimestamps,
    includeTags,
    includeSource,
    generateContent,
    generatePreview,
    copyToClipboard,
    downloadFile,
    createPreviewComputed
  }
}
