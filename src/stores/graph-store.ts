import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  GraphNode, 
  GraphEdge, 
  KnowledgeGraphData, 
  GraphStatistics,
  GraphConfig,
  SimilarityPair 
} from '../types/graph'
import type { Paper } from '../types'
import { getCategoryColor, truncateLabel } from '../types/graph'

export const useGraphStore = defineStore('graph', () => {
  const graphData = ref<KnowledgeGraphData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentDate = ref<string>('')
  
  const config = ref<GraphConfig>({
    similarityThreshold: 0.6,
    nodeSizeFactor: 1,
    showLabels: true,
    layoutType: 'force',
    selectedCategories: []
  })

  const nodes = computed(() => graphData.value?.nodes ?? [])
  const edges = computed(() => graphData.value?.edges ?? [])
  const statistics = computed(() => graphData.value?.statistics ?? null)

  const filteredNodes = computed(() => {
    if (config.value.selectedCategories.length === 0) {
      return nodes.value
    }
    return nodes.value.filter(node => 
      config.value.selectedCategories.includes(node.group)
    )
  })

  const filteredEdges = computed(() => {
    const filteredNodeIds = new Set(filteredNodes.value.map(n => n.id))
    return edges.value.filter(edge => 
      filteredNodeIds.has(edge.from) && 
      filteredNodeIds.has(edge.to) &&
      edge.value >= config.value.similarityThreshold
    )
  })

  const categories = computed(() => {
    const categoryMap = new Map<string, { name: string; count: number; color: string }>()
    nodes.value.forEach(node => {
      const existing = categoryMap.get(node.group)
      if (existing) {
        existing.count++
      } else {
        categoryMap.set(node.group, {
          name: node.group,
          count: 1,
          color: getCategoryColor(node.group)
        })
      }
    })
    return Array.from(categoryMap.values()).sort((a, b) => b.count - a.count)
  })

  const setGraphData = (data: KnowledgeGraphData) => {
    graphData.value = data
    currentDate.value = data.date
  }

  const updateConfig = (newConfig: Partial<GraphConfig>) => {
    config.value = { ...config.value, ...newConfig }
  }

  const resetConfig = () => {
    config.value = {
      similarityThreshold: 0.6,
      nodeSizeFactor: 1,
      showLabels: true,
      layoutType: 'force',
      selectedCategories: []
    }
  }

  const clearGraph = () => {
    graphData.value = null
    currentDate.value = ''
    error.value = null
  }

  const buildGraphFromPapers = (
    papers: Paper[], 
    similarities: SimilarityPair[],
    date: string
  ) => {
    const graphNodes: GraphNode[] = papers.map(paper => ({
      id: paper.id,
      label: truncateLabel(paper.title, 25),
      title: paper.title,
      group: paper.primaryCategory || 'other',
      value: (paper.citations ?? 1) * config.value.nodeSizeFactor,
      color: getCategoryColor(paper.primaryCategory || 'other'),
      paper
    }))

    const graphEdges: GraphEdge[] = similarities
      .filter(s => s.score >= config.value.similarityThreshold)
      .map((s, index) => ({
        id: `edge-${index}`,
        from: s.paper1_id,
        to: s.paper2_id,
        value: s.score,
        title: `Similarity: ${(s.score * 100).toFixed(1)}%`
      }))

    const categoryCount = new Map<string, number>()
    papers.forEach(p => {
      const cat = p.primaryCategory || 'other'
      categoryCount.set(cat, (categoryCount.get(cat) ?? 0) + 1)
    })

    const topCategories = Array.from(categoryCount.entries())
      .map(([categoryId, count]) => ({
        categoryId,
        categoryName: categoryId,
        count
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)

    const stats: GraphStatistics = {
      totalPapers: papers.length,
      totalConnections: graphEdges.length,
      topCategories,
      avgSimilarity: similarities.length > 0 
        ? similarities.reduce((sum, s) => sum + s.score, 0) / similarities.length 
        : 0,
      clusters: []
    }

    const data: KnowledgeGraphData = {
      nodes: graphNodes,
      edges: graphEdges,
      date,
      statistics: stats
    }

    setGraphData(data)
    return data
  }

  return {
    graphData,
    loading,
    error,
    currentDate,
    config,
    nodes,
    edges,
    statistics,
    filteredNodes,
    filteredEdges,
    categories,
    setGraphData,
    updateConfig,
    resetConfig,
    clearGraph,
    buildGraphFromPapers
  }
})
