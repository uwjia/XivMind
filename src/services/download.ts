import { apiRequest } from '@/services/common'

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
  completed_count: number
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
  },

  async openContainingFolder(taskId: string): Promise<{ message: string; success: boolean }> {
    return apiRequest(`/downloads/${taskId}/open-folder`, {
      method: 'POST',
    })
  },

  async checkBatch(paperIds: string[]): Promise<{ downloads: Record<string, boolean> }> {
    return apiRequest<{ downloads: Record<string, boolean> }>('/downloads/check-batch', {
      method: 'POST',
      body: JSON.stringify({ paper_ids: paperIds }),
    })
  },

  async openFileByPaperId(paperId: string): Promise<{ message: string; success: boolean }> {
    return apiRequest(`/downloads/open-by-paper-id/${encodeURIComponent(paperId)}`, {
      method: 'POST',
    })
  },

  async check(paperId: string): Promise<{ is_downloaded: boolean }> {
    return apiRequest<{ is_downloaded: boolean }>(`/downloads/check/${encodeURIComponent(paperId)}`)
  },

  async syncLocalFiles(): Promise<SyncLocalFilesResponse> {
    return apiRequest<SyncLocalFilesResponse>('/downloads/sync', {
      method: 'POST',
    })
  },

  async getMissingFiles(limit: number = 100, offset: number = 0): Promise<DownloadTaskListResponse> {
    return apiRequest<DownloadTaskListResponse>(`/downloads/missing-files?limit=${limit}&offset=${offset}`)
  },

  async getIncomplete(limit: number = 100, offset: number = 0): Promise<DownloadTaskListResponse> {
    return apiRequest<DownloadTaskListResponse>(`/downloads/incomplete?limit=${limit}&offset=${offset}`)
  }
}

export interface SyncResultDetail {
  paper_id: string
  status: string
  file_path: string
  reason?: string
}

export interface SyncLocalFilesResponse {
  added: number
  skipped: number
  errors: number
  details: SyncResultDetail[]
}
