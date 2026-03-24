import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PdfAnnotation, CreateAnnotationData, ViewMode } from '@/types/pdf'
import { pdfAnnotationAPI } from '@/services/pdf-annotation'
import { useToastStore } from '@/stores/toast-store'

export const usePdfAnnotationStore = defineStore('pdf-annotation', () => {
  const annotations = ref<PdfAnnotation[]>([])
  const currentPaperId = ref<string>('')
  const loading = ref(false)
  const error = ref<string | null>(null)

  const annotationsByPage = computed(() => {
    const map = new Map<number, PdfAnnotation[]>()
    for (const annotation of annotations.value) {
      const page = annotation.page_number
      if (!map.has(page)) {
        map.set(page, [])
      }
      map.get(page)!.push(annotation)
    }
    return map
  })

  function showError(message: string) {
    error.value = message
    const toast = useToastStore()
    toast.showError(message)
  }

  async function loadAnnotations(paperId: string) {
    if (currentPaperId.value === paperId && annotations.value.length > 0) {
      return
    }

    loading.value = true
    error.value = null
    currentPaperId.value = paperId

    try {
      annotations.value = await pdfAnnotationAPI.getAnnotations(paperId)
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to load annotations'
      showError(message)
      annotations.value = []
    } finally {
      loading.value = false
    }
  }

  async function createAnnotation(data: CreateAnnotationData): Promise<PdfAnnotation | null> {
    try {
      const annotation = await pdfAnnotationAPI.createAnnotation(data)
      annotations.value.push(annotation)
      return annotation
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to create annotation'
      showError(message)
      return null
    }
  }

  async function updateAnnotation(id: string, data: Partial<CreateAnnotationData>): Promise<boolean> {
    try {
      const updated = await pdfAnnotationAPI.updateAnnotation(id, data)
      const index = annotations.value.findIndex(a => a.id === id)
      if (index !== -1) {
        annotations.value[index] = updated
      }
      return true
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to update annotation'
      showError(message)
      return false
    }
  }

  async function deleteAnnotation(id: string): Promise<boolean> {
    try {
      await pdfAnnotationAPI.deleteAnnotation(id)
      annotations.value = annotations.value.filter(a => a.id !== id)
      return true
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to delete annotation'
      showError(message)
      return false
    }
  }

  function getAnnotationsForPage(pageNumber: number): PdfAnnotation[] {
    return annotationsByPage.value.get(pageNumber) || []
  }

  function clearAnnotations() {
    annotations.value = []
    currentPaperId.value = ''
  }

  return {
    annotations,
    currentPaperId,
    loading,
    error,
    annotationsByPage,
    loadAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    getAnnotationsForPage,
    clearAnnotations,
  }
})

export const usePdfProgressStore = defineStore('pdf-progress', () => {
  const progressMap = ref<Map<string, { page: number; zoom: number; viewMode: ViewMode }>>(new Map())

  function getProgress(paperId: string) {
    return progressMap.value.get(paperId)
  }

  function setProgress(paperId: string, page: number, zoom: number, viewMode: ViewMode) {
    progressMap.value.set(paperId, { page, zoom, viewMode })
  }

  async function loadProgress(paperId: string): Promise<{ page: number; zoom: number; viewMode: ViewMode } | null> {
    try {
      const progress = await pdfAnnotationAPI.getReadingProgress(paperId)
      if (progress) {
        setProgress(paperId, progress.current_page, progress.zoom_level, progress.view_mode)
        return { page: progress.current_page, zoom: progress.zoom_level, viewMode: progress.view_mode }
      }
      return null
    } catch {
      return null
    }
  }

  async function saveProgress(paperId: string, page: number, totalPages: number, zoom: number, viewMode: ViewMode) {
    try {
      await pdfAnnotationAPI.saveReadingProgress(paperId, {
        current_page: page,
        total_pages: totalPages,
        zoom_level: zoom,
        view_mode: viewMode,
      })
      setProgress(paperId, page, zoom, viewMode)
    } catch (e) {
      console.error('Failed to save reading progress:', e)
    }
  }

  return {
    progressMap,
    getProgress,
    setProgress,
    loadProgress,
    saveProgress,
  }
})
