import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSearchPanelStore, type SearchSource, type ArxivSearchOptions, type BackendSearchOptions, type SemanticSearchOptions } from '@/stores/search-panel-store'
import { ROUTES } from '@/constants/routes'

export function useSearchPanel() {
  const router = useRouter()
  const searchPanelStore = useSearchPanelStore()

  const position = ref({ ...searchPanelStore.position })
  const size = ref({ ...searchPanelStore.size })
  const isDragging = ref(false)
  const localQuery = ref(searchPanelStore.searchQuery)
  const localSource = ref<SearchSource>(searchPanelStore.searchSource)
  const localArxivOptions = ref<ArxivSearchOptions>({ ...searchPanelStore.arxivOptions })
  const localBackendOptions = ref<BackendSearchOptions>({ ...searchPanelStore.backendOptions })
  const localSemanticOptions = ref<SemanticSearchOptions>({ ...searchPanelStore.semanticOptions })

  const isVisible = computed(() => searchPanelStore.isVisible)
  const isMinimized = computed(() => searchPanelStore.isMinimized)

  const panelStyle = computed(() => ({
    left: `${position.value.x}px`,
    top: `${position.value.y}px`,
    width: `${size.value.width}px`,
    height: isMinimized.value ? 'auto' : `${size.value.height}px`
  }))

  const handleMouseDown = (e: MouseEvent) => {
    if ((e.target as HTMLElement).closest('.header-actions')) return
    
    isDragging.value = true
    const startX = e.clientX - position.value.x
    const startY = e.clientY - position.value.y

    const handleMouseMove = (moveEvent: MouseEvent) => {
      position.value = {
        x: Math.max(0, Math.min(window.innerWidth - size.value.width, moveEvent.clientX - startX)),
        y: Math.max(0, Math.min(window.innerHeight - 100, moveEvent.clientY - startY))
      }
    }

    const handleMouseUp = () => {
      isDragging.value = false
      searchPanelStore.updatePosition(position.value.x, position.value.y)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const toggleMinimize = () => {
    searchPanelStore.toggleMinimize()
  }

  const hidePanel = () => {
    searchPanelStore.hidePanel()
  }

  const handleSearch = () => {
    if (!localQuery.value.trim()) return

    searchPanelStore.setSearchQuery(localQuery.value)
    searchPanelStore.setSearchSource(localSource.value)
    searchPanelStore.setArxivOptions(localArxivOptions.value)
    searchPanelStore.setBackendOptions(localBackendOptions.value)
    searchPanelStore.setSemanticOptions(localSemanticOptions.value)

    const query: Record<string, string> = {
      q: localQuery.value,
      source: localSource.value
    }

    if (localSource.value === 'arxiv') {
      query.category = localArxivOptions.value.category
      query.maxResults = String(localArxivOptions.value.maxResults)
    } else if (localSource.value === 'backend') {
      query.searchType = localBackendOptions.value.searchType
      if (localBackendOptions.value.searchType === 'keyword') {
        if (localBackendOptions.value.titleOnly) {
          query.titleOnly = 'true'
        }
        if (localBackendOptions.value.exactPhrase) {
          query.exactPhrase = 'true'
        }
        query.category = localBackendOptions.value.category
        query.maxResults = String(localBackendOptions.value.maxResults)
        if (localBackendOptions.value.dateFrom) {
          query.dateFrom = localBackendOptions.value.dateFrom
        }
        if (localBackendOptions.value.dateTo) {
          query.dateTo = localBackendOptions.value.dateTo
        }
      } else if (localBackendOptions.value.searchType === 'author') {
        query.maxResults = String(localBackendOptions.value.maxResults)
      }
    } else if (localSource.value === 'semantic') {
      query.topK = String(localSemanticOptions.value.topK)
      if (localSemanticOptions.value.category) {
        query.category = localSemanticOptions.value.category
      }
      if (localSemanticOptions.value.dateFrom) {
        query.dateFrom = localSemanticOptions.value.dateFrom
      }
      if (localSemanticOptions.value.dateTo) {
        query.dateTo = localSemanticOptions.value.dateTo
      }
    }

    router.push({ path: ROUTES.SEARCH, query })
    hidePanel()
  }

  watch(() => searchPanelStore.position, (newPos) => {
    position.value = { ...newPos }
  }, { deep: true })

  watch(() => searchPanelStore.size, (newSize) => {
    size.value = { ...newSize }
  }, { deep: true })

  watch(() => searchPanelStore.searchQuery, (newQuery) => {
    localQuery.value = newQuery
  })

  watch(() => searchPanelStore.searchSource, (newSource) => {
    localSource.value = newSource
  })

  watch(() => searchPanelStore.arxivOptions, (newOptions) => {
    localArxivOptions.value = { ...newOptions }
  }, { deep: true })

  watch(() => searchPanelStore.backendOptions, (newOptions) => {
    localBackendOptions.value = { ...newOptions }
  }, { deep: true })

  watch(() => searchPanelStore.semanticOptions, (newOptions) => {
    localSemanticOptions.value = { ...newOptions }
  }, { deep: true })

  watch(() => searchPanelStore.isVisible, async (visible) => {
    if (visible && !searchPanelStore.hasUserMovedPanel) {
      await nextTick()
      searchPanelStore.resetToDefaultPosition()
      position.value = { ...searchPanelStore.position }
    }
  })

  return {
    position,
    size,
    isDragging,
    localQuery,
    localSource,
    localArxivOptions,
    localBackendOptions,
    localSemanticOptions,
    isVisible,
    isMinimized,
    panelStyle,
    handleMouseDown,
    toggleMinimize,
    hidePanel,
    handleSearch
  }
}
