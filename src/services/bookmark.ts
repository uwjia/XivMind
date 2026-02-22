import { apiRequest } from './common'

export interface BookmarkData {
  paper_id: string
  arxiv_id?: string
  title: string
  authors?: string[]
  abstract?: string
  comment?: string
  journal_ref?: string
  doi?: string
  primary_category?: string
  categories?: string[]
  pdf_url?: string
  abs_url?: string
  published?: string
  updated?: string
}

export interface Bookmark {
  id: string
  paper_id: string
  arxiv_id?: string
  title: string
  authors: string[]
  abstract: string
  comment?: string
  journal_ref?: string
  doi?: string
  primary_category: string
  categories: string[]
  pdf_url: string
  abs_url: string
  published?: string
  updated?: string
  created_at: string
}

export interface BookmarkListResponse {
  total: number
  items: Bookmark[]
}

export const bookmarkAPI = {
  async add(data: BookmarkData): Promise<Bookmark> {
    return apiRequest<Bookmark>('/bookmarks', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async remove(paperId: string): Promise<{ message: string; success: boolean }> {
    return apiRequest(`/bookmarks/${encodeURIComponent(paperId)}`, {
      method: 'DELETE',
    })
  },

  async check(paperId: string): Promise<{ paper_id: string; is_bookmarked: boolean }> {
    return apiRequest(`/bookmarks/check/${encodeURIComponent(paperId)}`)
  },

  async list(limit: number = 100, offset: number = 0): Promise<BookmarkListResponse> {
    return apiRequest<BookmarkListResponse>(`/bookmarks?limit=${limit}&offset=${offset}`)
  },

  async search(query: string, limit: number = 10): Promise<BookmarkListResponse> {
    return apiRequest<BookmarkListResponse>(`/bookmarks/search?query=${encodeURIComponent(query)}&limit=${limit}`)
  }
}
