import { defineStore } from 'pinia'
import { ref } from 'vue'

export type SearchSource = 'arxiv' | 'backend' | 'semantic'
export type BackendSearchType = 'keyword' | 'author'

export interface ArxivSearchOptions {
  category: string
  maxResults: number
}

export interface BackendSearchOptions {
  category: string
  maxResults: number
  dateFrom: string
  dateTo: string
  searchType: BackendSearchType
  titleOnly: boolean
  exactPhrase: boolean
}

export interface SemanticSearchOptions {
  topK: number
  category: string
  dateFrom: string
  dateTo: string
}

export type SearchOptions = ArxivSearchOptions | BackendSearchOptions | SemanticSearchOptions

const defaultArxivOptions: ArxivSearchOptions = {
  category: 'cs*',
  maxResults: 50
}

const defaultBackendOptions: BackendSearchOptions = {
  category: 'cs*',
  maxResults: 50,
  dateFrom: '',
  dateTo: '',
  searchType: 'keyword',
  titleOnly: false,
  exactPhrase: false
}

const defaultSemanticOptions: SemanticSearchOptions = {
  topK: 50,
  category: '',
  dateFrom: '',
  dateTo: ''
}

export const useSearchPanelStore = defineStore('searchPanel', () => {
  const isVisible = ref(false)
  const isMinimized = ref(false)
  const position = ref({ x: 20, y: 80 })
  const size = ref({ width: 360, height: 400 })
  const hasUserMovedPanel = ref(false)
  const searchBtnPosition = ref({ x: 0, y: 0 })
  const searchSource = ref<SearchSource>('backend')
  const searchQuery = ref('')
  const arxivOptions = ref<ArxivSearchOptions>({ ...defaultArxivOptions })
  const backendOptions = ref<BackendSearchOptions>({ ...defaultBackendOptions })
  const semanticOptions = ref<SemanticSearchOptions>({ ...defaultSemanticOptions })

  const showPanel = () => {
    isVisible.value = true
  }

  const hidePanel = () => {
    isVisible.value = false
  }

  const togglePanel = () => {
    if (isVisible.value) {
      hidePanel()
    } else {
      showPanel()
    }
  }

  const toggleMinimize = () => {
    isMinimized.value = !isMinimized.value
  }

  const updatePosition = (x: number, y: number) => {
    position.value = { x, y }
    hasUserMovedPanel.value = true
  }

  const updateSize = (width: number, height: number) => {
    size.value = { width, height }
  }

  const setSearchBtnPosition = (x: number, y: number) => {
    searchBtnPosition.value = { x, y }
  }

  const resetToDefaultPosition = () => {
    const panelWidth = size.value.width
    const newX = Math.max(10, searchBtnPosition.value.x - panelWidth)
    const newY = searchBtnPosition.value.y + 8
    position.value = { x: newX, y: newY }
    hasUserMovedPanel.value = false
  }

  const setSearchSource = (source: SearchSource) => {
    searchSource.value = source
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const setArxivOptions = (options: Partial<ArxivSearchOptions>) => {
    arxivOptions.value = { ...arxivOptions.value, ...options }
  }

  const setBackendOptions = (options: Partial<BackendSearchOptions>) => {
    backendOptions.value = { ...backendOptions.value, ...options }
  }

  const setSemanticOptions = (options: Partial<SemanticSearchOptions>) => {
    semanticOptions.value = { ...semanticOptions.value, ...options }
  }

  const getCurrentOptions = () => {
    switch (searchSource.value) {
      case 'arxiv':
        return arxivOptions.value
      case 'backend':
        return backendOptions.value
      case 'semantic':
        return semanticOptions.value
      default:
        return backendOptions.value
    }
  }

  const resetOptions = () => {
    arxivOptions.value = { ...defaultArxivOptions }
    backendOptions.value = { ...defaultBackendOptions }
    semanticOptions.value = { ...defaultSemanticOptions }
  }

  return {
    isVisible,
    isMinimized,
    position,
    size,
    hasUserMovedPanel,
    searchBtnPosition,
    searchSource,
    searchQuery,
    arxivOptions,
    backendOptions,
    semanticOptions,
    showPanel,
    hidePanel,
    togglePanel,
    toggleMinimize,
    updatePosition,
    updateSize,
    setSearchBtnPosition,
    resetToDefaultPosition,
    setSearchSource,
    setSearchQuery,
    setArxivOptions,
    setBackendOptions,
    setSemanticOptions,
    getCurrentOptions,
    resetOptions
  }
})
