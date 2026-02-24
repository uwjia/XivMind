import type { Paper } from './index'

export interface GraphNode {
  id: string
  label: string
  title: string
  group: string
  value: number
  color?: string
  paper: Paper
}

export interface GraphEdge {
  id: string
  from: string
  to: string
  value: number
  title?: string
}

export interface CategoryCount {
  categoryId: string
  categoryName: string
  count: number
}

export interface ClusterInfo {
  id: string
  name: string
  nodeCount: number
  category: string
}

export interface GraphStatistics {
  totalPapers: number
  totalConnections: number
  topCategories: CategoryCount[]
  avgSimilarity: number
  clusters: ClusterInfo[]
}

export interface KnowledgeGraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  date: string
  statistics: GraphStatistics
}

export interface SimilarityPair {
  paper1_id: string
  paper2_id: string
  score: number
}

export interface SimilarityMatrix {
  date: string
  similarities: SimilarityPair[]
}

export interface GraphConfig {
  similarityThreshold: number
  nodeSizeFactor: number
  showLabels: boolean
  layoutType: 'force' | 'circular' | 'hierarchical'
  selectedCategories: string[]
}

export interface GraphFilter {
  categories: string[]
  minSimilarity: number
  minCitations: number
}

export const CATEGORY_COLORS: Record<string, string> = {
  'cs.AI': '#FF6B6B',
  'cs.CL': '#4ECDC4',
  'cs.CV': '#45B7D1',
  'cs.LG': '#96CEB4',
  'cs.NE': '#FFEAA7',
  'cs.RO': '#DDA0DD',
  'cs.CR': '#98D8C8',
  'cs.DB': '#F7DC6F',
  'cs.DC': '#BB8FCE',
  'cs.IR': '#85C1E9',
  'cs.SE': '#F8B500',
  'cs.HC': '#FF8C00',
  'cs.MA': '#00CED1',
  'cs.SY': '#9370DB',
  'cs.GT': '#20B2AA',
  'cs.DS': '#FF69B4',
  'cs.CG': '#7B68EE',
  'cs.CY': '#48D1CC',
  'cs.ET': '#C71585',
  'cs.FL': '#00FA9A',
  'cs.GL': '#DAA520',
  'cs.GR': '#E6E6FA',
  'cs.AR': '#87CEEB',
  'cs.CC': '#FFA07A',
  'cs.CE': '#20B2AA',
  'math': '#9B59B6',
  'physics': '#3498DB',
  'stat': '#E74C3C',
  'q-bio': '#2ECC71',
  'q-fin': '#F39C12',
  'eess': '#1ABC9C',
  'econ': '#E91E63',
  'other': '#95A5A6'
}

export function getCategoryColor(category: string): string {
  if (CATEGORY_COLORS[category]) {
    return CATEGORY_COLORS[category]
  }
  
  const mainCategory = category.split('.')[0]
  if (CATEGORY_COLORS[mainCategory]) {
    return CATEGORY_COLORS[mainCategory]
  }
  
  return CATEGORY_COLORS['other']
}

export function truncateLabel(text: string, maxLength: number = 25): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
