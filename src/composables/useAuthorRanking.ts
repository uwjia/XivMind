import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { CATEGORY_IDS, getCategoryColor } from '@/utils/categoryColors'
import type { AuthorRank, AnalysisStatus, AuthorMetricType, PageRankAlgorithm } from '@/types/authorAnalysis'

export function useAuthorRanking() {
  const router = useRouter()

  const authors = ref<AuthorRank[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedMetric = ref<AuthorMetricType>('pagerank')
  const selectedCategory = ref('')
  const currentPage = ref(1)
  const pageSize = ref(50)
  const totalAuthors = ref(0)
  const authorSearchQuery = ref('')

  const analysisStatus = ref<AnalysisStatus>({
    running: false,
    progress: 0,
    total: 0,
    result: null,
    error: null,
    algorithm: null,
  })

  const showRebuildOptions = ref(false)
  const rebuilding = ref(false)
  const rebuildError = ref<string | null>(null)
  const rebuildOptions = ref({
    minPapers: 3,
    alpha: 0.85,
    useDisambiguation: true,
    similarityThreshold: 0.1,
    algorithm: 'networkx' as PageRankAlgorithm,
  })

  const jumpPageInput = ref<number | null>(null)

  const totalPages = computed(() => {
    if (totalAuthors.value <= 0) return 1
    return Math.ceil(totalAuthors.value / pageSize.value)
  })

  const progressPercent = computed(() => {
    if (analysisStatus.value.total === 0) return 0
    return (analysisStatus.value.progress / analysisStatus.value.total) * 100
  })

  async function fetchAuthors() {
    loading.value = true
    error.value = null

    try {
      const offset = (currentPage.value - 1) * pageSize.value
      const result = await apiService.getTopAuthors(
        selectedMetric.value,
        selectedCategory.value || undefined,
        authorSearchQuery.value || undefined,
        pageSize.value,
        offset
      )
      authors.value = result.authors
      totalAuthors.value = result.total
    } catch (e: any) {
      error.value = e.message || 'Failed to load author rankings'
    } finally {
      loading.value = false
    }
  }

  async function fetchAnalysisStatus() {
    try {
      analysisStatus.value = await apiService.getAnalysisStatus()
    } catch (e) {
      console.error('Failed to fetch analysis status:', e)
    }
  }

  async function confirmRebuild() {
    rebuilding.value = true
    rebuildError.value = null
    try {
      await apiService.rebuildAnalysis(
        rebuildOptions.value.minPapers,
        rebuildOptions.value.alpha,
        rebuildOptions.value.useDisambiguation,
        rebuildOptions.value.similarityThreshold,
        rebuildOptions.value.algorithm
      )
      showRebuildOptions.value = false
      await fetchAnalysisStatus()
      pollAnalysisStatus()
    } catch (e: any) {
      rebuildError.value = e.message || 'Failed to start rebuild'
    } finally {
      rebuilding.value = false
    }
  }

  function openRebuildOptions() {
    rebuildError.value = null
    showRebuildOptions.value = true
  }

  function pollAnalysisStatus() {
    const poll = async () => {
      if (!analysisStatus.value.running) return
      await fetchAnalysisStatus()
      if (analysisStatus.value.running) {
        setTimeout(poll, 2000)
      } else {
        await fetchAuthors()
      }
    }
    poll()
  }

  function handleAuthorSearch() {
    currentPage.value = 1
    fetchAuthors()
  }

  function handleJumpPageInput() {
    const value = jumpPageInput.value
    if (typeof value === 'number' && value > totalPages.value) {
      jumpPageInput.value = totalPages.value
    }
  }

  function handleGoToPage() {
    const targetPage = jumpPageInput.value
    if (targetPage && targetPage > 0 && targetPage <= totalPages.value) {
      currentPage.value = targetPage
      jumpPageInput.value = null
    }
  }

  function goToFirstPage() {
    currentPage.value = 1
  }

  function goToPreviousPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  function goToNextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  function formatMetric(value: number): string {
    if (value === 0) return '0'
    if (value < 0.0001) return value.toExponential(4)
    if (value < 0.01) return value.toFixed(6)
    return value.toFixed(4)
  }

  function goToAuthor(author: AuthorRank) {
    router.push({
      name: 'AuthorProfile',
      params: { authorName: encodeURIComponent(author.name) }
    })
  }

  function viewPapers(author: AuthorRank) {
    router.push({
      name: 'AuthorPapers',
      params: { authorName: encodeURIComponent(author.name) }
    })
  }

  watch([selectedMetric, selectedCategory], () => {
    currentPage.value = 1
    fetchAuthors()
  })

  watch(currentPage, () => {
    fetchAuthors()
  })

  onMounted(async () => {
    await fetchAnalysisStatus()
    await fetchAuthors()
  })

  return {
    authors,
    loading,
    error,
    selectedMetric,
    selectedCategory,
    currentPage,
    pageSize,
    totalAuthors,
    authorSearchQuery,
    analysisStatus,
    showRebuildOptions,
    rebuilding,
    rebuildError,
    rebuildOptions,
    jumpPageInput,
    categories: CATEGORY_IDS,
    totalPages,
    progressPercent,
    fetchAuthors,
    fetchAnalysisStatus,
    confirmRebuild,
    openRebuildOptions,
    handleAuthorSearch,
    handleJumpPageInput,
    handleGoToPage,
    goToFirstPage,
    goToPreviousPage,
    goToNextPage,
    formatMetric,
    getCategoryColor,
    goToAuthor,
    viewPapers,
  }
}
