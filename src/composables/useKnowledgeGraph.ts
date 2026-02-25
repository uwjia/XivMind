import { ref, computed, type Ref } from 'vue'
import { useGraphStore } from '../stores/graph-store'
import { graphAPI } from '../services/graphAPI'
import type { GraphNode, GraphConfig } from '../types/graph'
import { storeToRefs } from 'pinia'
import { useDateIndexes } from './useDateIndexes'

export function useKnowledgeGraph(
  selectedDate: Ref<Date | string | { startDate: string; endDate: string }>,
  selectedCategory: Ref<string>
) {
  const graphStore = useGraphStore()
  const { hasEmbedding, generateEmbedding } = useDateIndexes()
  
  const isGraphView = ref(false)
  const graphDate = ref(new Date().toISOString().split('T')[0])
  
  const { config: graphConfig, statistics: graphStatistics, loading: graphLoading, error: graphError } = storeToRefs(graphStore)
  
  const graphCategories = computed(() => graphStore.categories)

  const toggleGraphView = async () => {
    isGraphView.value = !isGraphView.value
    if (isGraphView.value) {
      await buildGraph()
    }
  }

  const buildGraph = async () => {
    graphStore.loading = true
    graphStore.error = null
    
    try {
      let date: string
      if (selectedDate.value instanceof Date) {
        const d = selectedDate.value
        date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      } else if (typeof selectedDate.value === 'string') {
        date = selectedDate.value
      } else if (typeof selectedDate.value === 'object' && 'startDate' in selectedDate.value) {
        date = selectedDate.value.startDate
      } else {
        date = graphDate.value
      }
      
      graphDate.value = date
      
      if (!hasEmbedding(date)) {
        const result = await generateEmbedding(date, true)
        if (!result.success) {
          throw new Error(result.error || 'Failed to generate embeddings')
        }
      }
      
      const graphData = await graphAPI.getOrBuildGraph(
        date, 
        graphConfig.value.similarityThreshold,
        selectedCategory.value === 'all' ? undefined : selectedCategory.value
      )
      graphStore.setGraphData(graphData)
    } catch (err) {
      graphStore.error = err instanceof Error ? err.message : 'Failed to build graph'
    } finally {
      graphStore.loading = false
    }
  }

  const handleNodeClick = (node: GraphNode) => {
    console.log('Node clicked:', node)
  }

  const handleGraphReady = () => {
    console.log('Graph ready')
  }

  const handleGraphConfigChange = (newConfig: Partial<GraphConfig>) => {
    graphStore.updateConfig(newConfig)
  }

  const handleLayoutChange = (layout: GraphConfig['layoutType']) => {
    graphStore.updateConfig({ layoutType: layout })
  }

  const handleGraphReset = () => {
    graphStore.resetConfig()
    buildGraph()
  }

  return {
    isGraphView,
    graphDate,
    graphConfig,
    graphStatistics,
    graphLoading,
    graphError,
    graphCategories,
    toggleGraphView,
    buildGraph,
    handleNodeClick,
    handleGraphReady,
    handleGraphConfigChange,
    handleLayoutChange,
    handleGraphReset
  }
}
