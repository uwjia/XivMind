import type { KnowledgeGraphData, SimilarityPair, GraphNode, GraphEdge, GraphStatistics, CategoryCount } from '../types/graph'
import type { Paper } from '../types'
import { getCategoryColor, truncateLabel } from '../types/graph'
import { arxivBackendAPI } from './arxivBackend'

const GRAPH_API_BASE = '/api/graph'
const DEFAULT_MAX_PAPERS = 1000

interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
  statistics: GraphStatistics
  date: string
}

interface SimilarityResponse {
  date: string
  similarities: SimilarityPair[]
  total_papers: number
  threshold: number
}

function transformPaperToNode(paper: Paper, nodeSizeFactor: number = 1): GraphNode {
  return {
    id: paper.id,
    label: truncateLabel(paper.title, 25),
    title: paper.title,
    group: paper.primaryCategory || 'other',
    value: Math.max(1, (paper.citations ?? 1)) * nodeSizeFactor,
    color: getCategoryColor(paper.primaryCategory || 'other'),
    paper
  }
}

function calculateSimilarity(abstract1: string, abstract2: string): number {
  const words1 = new Set(abstract1.toLowerCase().split(/\s+/).filter(w => w.length > 3))
  const words2 = new Set(abstract2.toLowerCase().split(/\s+/).filter(w => w.length > 3))
  
  const intersection = new Set([...words1].filter(x => words2.has(x)))
  const union = new Set([...words1, ...words2])
  
  return union.size > 0 ? intersection.size / union.size : 0
}

function calculateCategorySimilarity(paper1: Paper, paper2: Paper): number {
  const cats1 = new Set(paper1.categories || [paper1.primaryCategory])
  const cats2 = new Set(paper2.categories || [paper2.primaryCategory])
  
  const intersection = new Set([...cats1].filter(x => cats2.has(x)))
  
  if (intersection.size > 0) {
    return 0.3
  }
  
  const mainCat1 = paper1.primaryCategory?.split('.')[0]
  const mainCat2 = paper2.primaryCategory?.split('.')[0]
  
  if (mainCat1 && mainCat1 === mainCat2) {
    return 0.15
  }
  
  return 0
}

function buildSimilarities(papers: Paper[], threshold: number = 0.3): SimilarityPair[] {
  const similarities: SimilarityPair[] = []
  
  for (let i = 0; i < papers.length; i++) {
    for (let j = i + 1; j < papers.length; j++) {
      const p1 = papers[i]
      const p2 = papers[j]
      
      const textSimilarity = calculateSimilarity(p1.abstract, p2.abstract)
      const categorySimilarity = calculateCategorySimilarity(p1, p2)
      
      const totalSimilarity = Math.min(1, textSimilarity * 0.7 + categorySimilarity * 0.3)
      
      if (totalSimilarity >= threshold) {
        similarities.push({
          paper1_id: p1.id,
          paper2_id: p2.id,
          score: totalSimilarity
        })
      }
    }
  }
  
  return similarities
}

function buildStatistics(papers: Paper[], edges: GraphEdge[]): GraphStatistics {
  const categoryCount = new Map<string, number>()
  papers.forEach(p => {
    const cat = p.primaryCategory || 'other'
    categoryCount.set(cat, (categoryCount.get(cat) ?? 0) + 1)
  })
  
  const topCategories: CategoryCount[] = Array.from(categoryCount.entries())
    .map(([categoryId, count]) => ({
      categoryId,
      categoryName: categoryId,
      count
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
  
  const avgSimilarity = edges.length > 0
    ? edges.reduce((sum, e) => sum + e.value, 0) / edges.length
    : 0
  
  return {
    totalPapers: papers.length,
    totalConnections: edges.length,
    topCategories,
    avgSimilarity,
    clusters: []
  }
}

export const graphAPI = {
  async fetchGraphData(date: string, threshold: number = 0.6, category?: string): Promise<KnowledgeGraphData | null> {
    try {
      const params = new URLSearchParams({
        threshold: threshold.toString(),
        max_papers: DEFAULT_MAX_PAPERS.toString()
      })
      if (category && category !== 'all' && category !== 'cs*') {
        params.append('category', category)
      }
      
      const response = await fetch(`${GRAPH_API_BASE}/${date}?${params}`)
      
      if (response.ok) {
        const data: GraphResponse = await response.json()
        return {
          nodes: data.nodes,
          edges: data.edges,
          date: data.date,
          statistics: data.statistics
        }
      }
      
      if (response.status === 404) {
        return null
      }
      
      throw new Error(`HTTP error! status: ${response.status}`)
    } catch (error) {
      console.error('Error fetching graph data:', error)
      return null
    }
  },

  async fetchSimilarities(date: string, threshold: number = 0.3, category?: string): Promise<SimilarityPair[]> {
    try {
      const params = new URLSearchParams({
        threshold: threshold.toString(),
        max_papers: DEFAULT_MAX_PAPERS.toString()
      })
      if (category && category !== 'all' && category !== 'cs*') {
        params.append('category', category)
      }
      
      const response = await fetch(`${GRAPH_API_BASE}/similarity/${date}?${params}`)
      
      if (response.ok) {
        const data: SimilarityResponse = await response.json()
        return data.similarities
      }
      
      return []
    } catch (error) {
      console.error('Error fetching similarities:', error)
      return []
    }
  },

  async buildGraphFromPapers(
    papers: Paper[], 
    date: string, 
    threshold: number = 0.3,
    nodeSizeFactor: number = 1
  ): Promise<KnowledgeGraphData> {
    const nodes: GraphNode[] = papers.map(p => transformPaperToNode(p, nodeSizeFactor))
    
    const similarities = buildSimilarities(papers, threshold)
    
    const edges: GraphEdge[] = similarities.map((s, index) => ({
      id: `edge-${index}`,
      from: s.paper1_id,
      to: s.paper2_id,
      value: s.score,
      title: `Similarity: ${(s.score * 100).toFixed(1)}%`
    }))
    
    const statistics = buildStatistics(papers, edges)
    
    return {
      nodes,
      edges,
      date,
      statistics
    }
  },

  async buildGraphForDate(
    date: string, 
    threshold: number = 0.5,
    category?: string
  ): Promise<KnowledgeGraphData> {
    const graphData = await this.fetchGraphData(date, threshold, category)
    if (graphData) {
      return graphData
    }
    
    const papers = await arxivBackendAPI.queryPapers(date, undefined, DEFAULT_MAX_PAPERS, 0, category || 'cs*')
    return this.buildGraphFromPapers(papers, date, threshold)
  },

  async getOrBuildGraph(
    date: string, 
    threshold: number = 0.5,
    category?: string,
    forceRebuild: boolean = false
  ): Promise<KnowledgeGraphData> {
    if (!forceRebuild) {
      const existingGraph = await this.fetchGraphData(date, threshold, category)
      if (existingGraph) {
        return existingGraph
      }
    }
    
    return this.buildGraphForDate(date, threshold, category)
  }
}
