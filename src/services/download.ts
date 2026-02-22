import { apiRequest } from './common'

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

export interface DownloadTaskListResponse {
  total: number
  items: DownloadTask[]
}

export const downloadAPI = {
  async create(data: DownloadTaskData): Promise<DownloadTask> {
    return apiRequest<DownloadTask>('/downloads', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async list(limit: number = 100, offset: number = 0): Promise<DownloadTaskListResponse> {
    return apiRequest<DownloadTaskListResponse>(`/downloads?limit=${limit}&offset=${offset}`)
  },

  async get(taskId: string): Promise<DownloadTask> {
    return apiRequest<DownloadTask>(`/downloads/${taskId}`)
  },

  async delete(taskId: string): Promise<{ message: string; success: boolean }> {
    return apiRequest(`/downloads/${taskId}`, {
      method: 'DELETE',
    })
  },

  async retry(taskId: string): Promise<DownloadTask> {
    return apiRequest<DownloadTask>(`/downloads/${taskId}/retry`, {
      method: 'POST',
    })
  },

  async cancel(taskId: string): Promise<DownloadTask> {
    return apiRequest<DownloadTask>(`/downloads/${taskId}/cancel`, {
      method: 'POST',
    })
  },

  async openFile(taskId: string): Promise<{ message: string; success: boolean }> {
    return apiRequest(`/downloads/${taskId}/open`, {
      method: 'POST',
    })
  }
}
