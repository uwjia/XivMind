import { ref } from 'vue'
import { arxivBackendAPI } from '@/services/arxivBackend'

export interface RelatedPaper {
  id: string
  title: string
  similarity_score: number
  abstract: string
  authors: string[]
  categories: string[]
  primary_category: string
  published: string
  updated: string
  doi: string | null
  pdf_url: string
  abs_url: string
}

export function useRelatedPapers() {
  const papers = ref<RelatedPaper[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const top_k = ref<number>(5)

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
      const result = await arxivBackendAPI.semanticSearch(query, top_k.value + 1)

      if (result.error) {
        error.value = result.error
        return
      }

      papers.value = result.papers
        .filter((p) => p.id !== paperId)
        .slice(0, top_k.value)
        .map((p) => ({
          id: p.id,
          title: p.title,
          similarity_score: p.similarity_score ?? 0,
          abstract: p.abstract || '',
          authors: p.authors || [],
          categories: p.categories || [],
          primary_category: p.primary_category || '',
          published: p.published || '',
          updated: p.updated || '',
          doi: p.doi || null,
          pdf_url: p.pdf_url || '',
          abs_url: p.abs_url || ''
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
    top_k,
    fetchRelatedPapers,
    clear,
  }
}
