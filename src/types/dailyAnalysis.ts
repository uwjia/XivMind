export interface Trend {
  name: string
  description: string
  paper_count: number
  paper_ids: string[]
}

export interface HighValuePaper {
  paper_id: string
  title: string
  innovation_type: string
  innovation_description: string
  confidence: number
}

export interface RecommendedPaper {
  paper_id: string
  title: string
  relevance_score: number
  matched_interests: string[]
  reason: string
}

export interface DailyAnalysisResult {
  date: string
  total_papers: number
  summary: string | null
  main_themes: string[] | null
  trends: Trend[] | null
  high_value_papers: HighValuePaper[] | null
  recommendations: RecommendedPaper[] | null
}

export type AnalysisMode = 'summary' | 'trends' | 'high_value' | 'recommend' | 'full' | 'semantic_search'
export type AnalysisLanguage = 'en' | 'zh'

export interface SemanticSearchPaper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  pdf_url: string
  abs_url: string
  published?: string
  similarity_score: number
}

export interface SemanticSearchResult {
  papers: SemanticSearchPaper[]
  total: number
  query: string
  model?: string
  error?: string
}
