import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBookmarkStore } from '@/stores/bookmark-store'
import { useConfigStore } from '@/stores/config-store'
import { useToastStore } from '@/stores/toast-store'
import { useThemeStore } from '@/stores/theme-store'
import { useDownloadHandler } from '@/composables/useDownloadHandler'
import { useMarkdown } from '@/composables/useMarkdown'
import { getCategoryColor, getTagStyle as getTagStyleUtil, categories } from '@/utils/categoryColors'

export interface BookmarkItem {
  id: string
  paper_id: string
  arxiv_id?: string
  title?: string
  abstract?: string
  comment?: string
  authors?: string[]
  primary_category?: string
  categories?: string[]
  pdf_url?: string
  abs_url?: string
  doi?: string
  published?: string
  updated?: string
  created_at?: string
}

export function useBookmarkActions() {
  const router = useRouter()
  const bookmarkStore = useBookmarkStore()
  const configStore = useConfigStore()
  const toastStore = useToastStore()
  const themeStore = useThemeStore()
  const { render, renderWithDefault } = useMarkdown()
  const { getStatus, getProgress, getStatusTitle, handleDownload } = useDownloadHandler()

  const isMinimal = computed(() => themeStore.iconStyle === 'minimal')

  const loading = ref(false)
  const searchQuery = ref('')
  const isDrawerOpen = ref(false)
  const selectedCategory = ref<string | null>(null)
  const currentPage = ref(0)
  const jumpPageInput = ref<string>('')

  const bookmarks = computed(() => bookmarkStore.bookmarks)
  const total = computed(() => bookmarkStore.total)
  const pageSize = computed(() => configStore.maxResults)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const categoryCounts = computed(() => {
    const counts: Record<string, number> = {}
    for (const bookmark of bookmarks.value) {
      const category = bookmark.primary_category
      if (category) {
        counts[category] = (counts[category] || 0) + 1
      }
    }
    return counts
  })

  const filteredBookmarks = computed(() => {
    if (!selectedCategory.value || selectedCategory.value === 'cs*') {
      return bookmarks.value
    }
    if (selectedCategory.value === 'other') {
      const csCategoryIds = categories.map(cat => cat.id)
      return bookmarks.value.filter(bookmark => !csCategoryIds.includes(bookmark.primary_category || ''))
    }
    return bookmarks.value.filter(bookmark => bookmark.primary_category === selectedCategory.value)
  })

  const fetchBookmarks = async () => {
    try {
      loading.value = true
      const offset = currentPage.value * pageSize.value
      await bookmarkStore.fetchBookmarks(pageSize.value, offset)
    } catch (error) {
      console.error('Failed to fetch bookmarks:', error)
      toastStore.showError('Failed to load bookmarks')
    } finally {
      loading.value = false
    }
  }

  const goToFirstPage = () => {
    currentPage.value = 0
    fetchBookmarks()
  }

  const goToPreviousPage = () => {
    if (currentPage.value > 0) {
      currentPage.value--
      fetchBookmarks()
    }
  }

  const goToNextPage = () => {
    if (currentPage.value < totalPages.value - 1) {
      currentPage.value++
      fetchBookmarks()
    }
  }

  const goToPage = (page: number) => {
    if (page >= 0 && page < totalPages.value) {
      currentPage.value = page
      fetchBookmarks()
    }
  }

  const handleGoToPage = () => {
    const targetPage = parseInt(jumpPageInput.value)
    if (targetPage && targetPage > 0) {
      goToPage(targetPage - 1)
      jumpPageInput.value = ''
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.value.trim()) {
      await fetchBookmarks()
      return
    }
    try {
      loading.value = true
      await bookmarkStore.searchBookmarks(searchQuery.value)
    } catch (error) {
      console.error('Failed to search bookmarks:', error)
      toastStore.showError('Search failed')
    } finally {
      loading.value = false
    }
  }

  const removeBookmark = async (paperId: string) => {
    try {
      await bookmarkStore.removeBookmark(paperId)
      toastStore.showSuccess('Bookmark removed')
    } catch (error) {
      console.error('Failed to remove bookmark:', error)
      toastStore.showError('Failed to remove bookmark')
    }
  }

  const goToDetail = (paperId: string) => {
    router.push({ name: 'PaperDetail', params: { id: paperId } })
  }

  const toggleDrawer = () => {
    isDrawerOpen.value = !isDrawerOpen.value
  }

  const closeDrawer = () => {
    isDrawerOpen.value = false
  }

  const handleCategorySelect = (categoryId: string | null) => {
    selectedCategory.value = categoryId
  }

  const openAbsUrl = (url?: string) => {
    if (url) window.open(url, '_blank')
  }

  const openPdfUrl = (url?: string) => {
    if (url) window.open(url, '_blank')
  }

  const openDoiUrl = (doi?: string) => {
    if (doi) window.open(`https://doi.org/${doi}`, '_blank')
  }

  const getRenderedAbstract = (abstract?: string) => {
    return renderWithDefault(abstract, 'No abstract available')
  }

  const getRenderedComment = (comment?: string) => {
    return render(comment)
  }

  const getCategoryStyle = (category?: string) => {
    if (isMinimal.value) {
      return {
        backgroundColor: 'var(--tag-primary-category-bg)',
        color: 'var(--tag-primary-category)',
        border: '1px solid var(--tag-primary-category-border)'
      }
    }
    const color = getCategoryColor(category || 'cs.AI')
    return {
      backgroundColor: color + '20',
      color: color,
      border: `1px solid ${color}40`
    }
  }

  const getTagStyle = (category: string) => {
    return getTagStyleUtil(category, isMinimal.value)
  }

  const handleDownloadClick = async (bookmark: BookmarkItem) => {
    await handleDownload({
      paperId: bookmark.paper_id,
      arxivId: bookmark.arxiv_id,
      title: bookmark.title || '',
      pdfUrl: bookmark.pdf_url || ''
    })
  }

  return {
    loading,
    searchQuery,
    isDrawerOpen,
    selectedCategory,
    bookmarks,
    categoryCounts,
    filteredBookmarks,
    total,
    currentPage,
    totalPages,
    pageSize,
    jumpPageInput,
    fetchBookmarks,
    handleSearch,
    removeBookmark,
    goToDetail,
    toggleDrawer,
    closeDrawer,
    handleCategorySelect,
    openAbsUrl,
    openPdfUrl,
    openDoiUrl,
    getRenderedAbstract,
    getRenderedComment,
    getCategoryStyle,
    getTagStyle,
    handleDownloadClick,
    goToFirstPage,
    goToPreviousPage,
    goToNextPage,
    goToPage,
    handleGoToPage,
    getDownloadStatus: getStatus,
    getDownloadProgress: getProgress,
    getDownloadTitle: getStatusTitle
  }
}
