import { ref } from 'vue'
import { semanticSearchAPI, type SearchOptions } from '@/services/semanticSearch'
import type { SemanticSearchPaper, SemanticSearchResult } from '@/types/dailyAnalysis'

export function useSemanticSearch() {
  const isSearching = ref(false)
  const searchError = ref<string | null>(null)
  const searchResults = ref<SemanticSearchPaper[]>([])
  const totalResults = ref(0)

  const searchPapers = async (
    query: string,
    options: SearchOptions = {}
  ): Promise<SemanticSearchResult | null> => {
    isSearching.value = true
    clearResults()

    try {
      const data = await semanticSearchAPI.searchPapers(query, options)

      if (data.error) {
        searchError.value = data.error
        return null
      }

      searchResults.value = data.papers || []
      totalResults.value = data.total

      return {
        papers: data.papers,
        total: data.total,
        query: data.query,
        model: data.model,
      }
    } catch (e) {
      searchError.value = e instanceof Error ? e.message : 'Search failed'
      return null
    } finally {
      isSearching.value = false
    }
  }

  const clearResults = () => {
    searchResults.value = []
    totalResults.value = 0
    searchError.value = null
  }

  return {
    isSearching,
    searchError,
    searchResults,
    totalResults,
    searchPapers,
    clearResults,
  }
}
