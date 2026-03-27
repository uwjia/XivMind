export interface AuthorRank {
  author_id: string
  name: string
  paper_count: number
  pagerank: number
  degree_centrality: number
  betweenness_centrality: number
  clustering_coeff: number
  primary_category: string | null
  first_year: number | null
  latest_year: number | null
  collaborator_count: number
  calculated_at: string
  rank?: number
}

export interface AuthorAnalysisResult {
  total_papers: number
  total_authors: number
  total_edges: number
  top_authors: AuthorRank[]
  status: 'success' | 'error' | 'running'
  message: string
}

export interface AnalysisStatus {
  running: boolean
  progress: number
  total: number
  result: AuthorAnalysisResult | null
  error: string | null
}

export interface AuthorAnalysisStatistics {
  total_papers: number
  total_analyzed_authors: number
}

export type AuthorMetricType = 
  | 'pagerank' 
  | 'degree_centrality' 
  | 'betweenness_centrality' 
  | 'paper_count' 
  | 'clustering_coeff'
