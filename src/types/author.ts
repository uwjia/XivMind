export interface CategoryDistribution {
  category: string
  name: string
  count: number
  percentage: number
}

export interface YearlyPaperCount {
  year: number
  count: number
}

export interface CollaboratorInfo {
  name: string
  collaboration_count: number
}

export interface KeywordInfo {
  word: string
  frequency: number
}

export interface AuthorProfile {
  name: string
  total_papers: number
  first_paper_year: number | null
  latest_paper_year: number | null
  active_years: number
  categories: CategoryDistribution[]
  yearly_papers: YearlyPaperCount[]
  collaborators: CollaboratorInfo[]
  keywords: KeywordInfo[]
  title_keywords: KeywordInfo[]
  error?: string
}
