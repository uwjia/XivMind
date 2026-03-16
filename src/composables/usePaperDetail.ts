import { ref, computed } from 'vue'
import { usePaperStore } from '@/stores/paper-store'
import { useBookmarkStore } from '@/stores/bookmark-store'
import { useDownloadStore } from '@/stores/download-store'
import { useToastStore } from '@/stores/toast-store'
import { arxivBackendAPI } from '@/services/arxivBackend'
import { useDownloadHandler } from '@/composables/useDownloadHandler'
import type { Paper } from '@/types'

export interface RelatedPaper {
  id: string
  title: string
  similarity_score: number
}

export function usePaperDetail() {
  const paperStore = usePaperStore()
  const bookmarkStore = useBookmarkStore()
  const downloadStore = useDownloadStore()
  const toastStore = useToastStore()
  const { getStatus: getDownloadStatus, getProgress: getDownloadProgress, handleDownload } = useDownloadHandler()

  const loading = ref(false)
  const error = ref<string | null>(null)
  const paper = ref<Paper | null>(null)
  const isBookmarked = ref(false)
  const isDownloaded = ref(false)

  const relatedPapers = ref<RelatedPaper[]>([])
  const relatedLoading = ref(false)
  const relatedError = ref<string | null>(null)

  const downloadStatus = computed(() => {
    if (!paper.value?.id) return 'none'
    const status = getDownloadStatus(paper.value.id)
    if (status === 'none' && isDownloaded.value) {
      return 'completed'
    }
    return status
  })

  const downloadProgress = computed(() => {
    if (!paper.value?.id) return 0
    return getDownloadProgress(paper.value.id)
  })

  const fetchPaperById = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const paperOne = await paperStore.fetchPaperById(id)
      paper.value = paperOne
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load paper'
      console.error('Error fetching paper:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchRelatedPapers = async () => {
    if (!paper.value?.title || !paper.value?.abstract) return

    relatedLoading.value = true
    relatedError.value = null

    try {
      const query = `${paper.value.title} ${paper.value.abstract.slice(0, 500)}`
      const result = await arxivBackendAPI.semanticSearch(query, 6)

      if (result.error) {
        relatedError.value = result.error
        return
      }

      relatedPapers.value = result.papers
        .filter((p: { id: string }) => p.id !== paper.value?.id)
        .slice(0, 5)
        .map((p: { id: string; title: string; similarity_score?: number }) => ({
          id: p.id,
          title: p.title,
          similarity_score: p.similarity_score ?? 0
        }))
    } catch (err) {
      relatedError.value = err instanceof Error ? err.message : 'Failed to find related papers'
      console.error('Error fetching related papers:', err)
    } finally {
      relatedLoading.value = false
    }
  }

  const checkBookmark = async () => {
    if (paper.value?.id) {
      isBookmarked.value = await bookmarkStore.checkBookmark(paper.value.id)
    }
  }

  const checkDownload = async () => {
    if (paper.value?.id) {
      isDownloaded.value = await downloadStore.checkDownload(paper.value.id)
    }
  }

  const toggleBookmark = async () => {
    if (!paper.value?.id) return
    try {
      const result = await bookmarkStore.toggleBookmark({
        paper_id: paper.value.id,
        arxiv_id: paper.value.arxivId,
        title: paper.value.title,
        authors: paper.value.authors,
        abstract: paper.value.abstract,
        comment: paper.value.comment,
        primary_category: paper.value.primaryCategory,
        categories: paper.value.categories,
        pdf_url: paper.value.pdfUrl,
        abs_url: paper.value.absUrl,
        published: paper.value.published?.toString(),
        updated: paper.value.updated?.toString(),
      })
      isBookmarked.value = result
      toastStore.showSuccess(result ? 'Added to bookmarks' : 'Removed from bookmarks')
    } catch (err) {
      console.error('Failed to toggle bookmark:', err)
      toastStore.showError('Failed to update bookmark')
    }
  }

  const downloadPdf = async () => {
    if (!paper.value?.pdfUrl || !paper.value?.id) return
    await handleDownload({
      paperId: paper.value.id,
      arxivId: paper.value.arxivId,
      title: paper.value.title,
      pdfUrl: paper.value.pdfUrl
    })
  }

  return {
    loading,
    error,
    paper,
    isBookmarked,
    isDownloaded,
    downloadStatus,
    downloadProgress,
    relatedPapers,
    relatedLoading,
    relatedError,
    fetchPaperById,
    fetchRelatedPapers,
    checkBookmark,
    checkDownload,
    toggleBookmark,
    downloadPdf,
  }
}
