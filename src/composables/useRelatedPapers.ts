import { ref } from 'vue'
import { arxivBackendAPI } from '@/services/arxivBackend'

export interface RelatedPaper {
  id: string
  title: string
  similarity_score: number
}

export function useRelatedPapers() {
  const papers = ref<RelatedPaper[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchRelatedPapers = async (
    paperId: string,
    paperTitle: string,
    paperAbstract: string
  ) => {
    if (!paperTitle || !paperAbstract) return

    loading.value = true
    error.value = null

    try {
      const query = `${paperTitle} ${paperAbstract.slice(0, 500)}`
      const result = await arxivBackendAPI.semanticSearch(query, 6)

      if (result.error) {
        error.value = result.error
        return
      }

      papers.value = result.papers
        .filter((p: { id: string }) => p.id !== paperId)
        .slice(0, 5)
        .map((p: { id: string; title: string; similarity_score?: number }) => ({
          id: p.id,
          title: p.title,
          similarity_score: p.similarity_score ?? 0
        }))
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to find related papers'
      console.error('Error fetching related papers:', err)
    } finally {
      loading.value = false
    }
  }

  const clear = () => {
    papers.value = []
    error.value = null
  }

  return {
    papers,
    loading,
    error,
    fetchRelatedPapers,
    clear,
  }
}
