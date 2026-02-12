const API_BASE_URL = 'http://localhost:8000/api'

export interface BookmarkData {
  paper_id: string
  arxiv_id?: string
  title: string
  authors?: string[]
  abstract?: string
  comment?: string
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
  primary_category: string
  categories: string[]
  pdf_url: string
  abs_url: string
  published?: string
  updated?: string
  created_at: string
}

export interface DownloadTaskData {
  paper_id: string
  arxiv_id?: string
  title: string
  pdf_url: string
}

export interface DownloadTask {
  id: string
  paper_id: string
  arxiv_id?: string
  title: string
  pdf_url: string
  status: 'pending' | 'downloading' | 'completed' | 'failed'
  progress: number
  file_path?: string
  file_size?: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface BookmarkListResponse {
  total: number
  items: Bookmark[]
}

export interface DownloadTaskListResponse {
  total: number
  items: DownloadTask[]
}

export interface MessageResponse {
  message: string
  success: boolean
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async addBookmark(data: BookmarkData): Promise<Bookmark> {
    return this.request<Bookmark>('/bookmarks', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async removeBookmark(paperId: string): Promise<MessageResponse> {
    return this.request<MessageResponse>(`/bookmarks/${encodeURIComponent(paperId)}`, {
      method: 'DELETE',
    })
  }

  async checkBookmark(paperId: string): Promise<{ paper_id: string; is_bookmarked: boolean }> {
    return this.request(`/bookmarks/check/${encodeURIComponent(paperId)}`)
  }

  async getBookmarks(limit: number = 100, offset: number = 0): Promise<BookmarkListResponse> {
    return this.request<BookmarkListResponse>(`/bookmarks?limit=${limit}&offset=${offset}`)
  }

  async searchBookmarks(query: string, limit: number = 10): Promise<BookmarkListResponse> {
    return this.request<BookmarkListResponse>(`/bookmarks/search?query=${encodeURIComponent(query)}&limit=${limit}`)
  }

  async createDownloadTask(data: DownloadTaskData): Promise<DownloadTask> {
    return this.request<DownloadTask>('/downloads', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getDownloadTasks(limit: number = 100, offset: number = 0): Promise<DownloadTaskListResponse> {
    return this.request<DownloadTaskListResponse>(`/downloads?limit=${limit}&offset=${offset}`)
  }

  async getDownloadTask(taskId: string): Promise<DownloadTask> {
    return this.request<DownloadTask>(`/downloads/${taskId}`)
  }

  async deleteDownloadTask(taskId: string): Promise<MessageResponse> {
    return this.request<MessageResponse>(`/downloads/${taskId}`, {
      method: 'DELETE',
    })
  }

  async retryDownloadTask(taskId: string): Promise<DownloadTask> {
    return this.request<DownloadTask>(`/downloads/${taskId}/retry`, {
      method: 'POST',
    })
  }

  async cancelDownloadTask(taskId: string): Promise<DownloadTask> {
    return this.request<DownloadTask>(`/downloads/${taskId}/cancel`, {
      method: 'POST',
    })
  }

  async openDownloadFile(taskId: string): Promise<MessageResponse> {
    return this.request<MessageResponse>(`/downloads/${taskId}/open`, {
      method: 'POST',
    })
  }
}

export const apiService = new ApiService()
