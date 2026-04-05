import { API_BASE_URL } from './config'

const API_BASE = `${API_BASE_URL}/api/pdf`

export interface ReadingHistoryItem {
  paper_id: string
  title: string
  authors: string[]
  primary_category: string
  categories: string[]
  current_page: number
  total_pages: number
  progress_percent: number
  last_read_at: string
  pdf_url: string
  abs_url: string
  published: string
}

export const readingHistoryAPI = {
  async getReadingHistory(limit: number = 20): Promise<ReadingHistoryItem[]> {
    const response = await fetch(`${API_BASE}/reading-history?limit=${limit}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch reading history: ${response.statusText}`)
    }
    return response.json()
  },
}
