import { apiRequest, API_BASE_URL } from '@/services/common'
import type {
  PdfAnnotation,
  CreateAnnotationData,
  UpdateAnnotationData,
  PdfReadingProgress,
  SaveProgressData,
  PdfOutlineItem,
} from '@/types/pdf'

export const pdfAnnotationAPI = {
  async getAnnotations(paperId: string): Promise<PdfAnnotation[]> {
    return apiRequest<PdfAnnotation[]>(`/pdf/${encodeURIComponent(paperId)}/annotations`)
  },

  async createAnnotation(data: CreateAnnotationData): Promise<PdfAnnotation> {
    return apiRequest<PdfAnnotation>(`/pdf/${encodeURIComponent(data.paper_id)}/annotations`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateAnnotation(id: string, data: UpdateAnnotationData): Promise<PdfAnnotation> {
    return apiRequest<PdfAnnotation>(`/pdf/annotations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  async deleteAnnotation(id: string): Promise<void> {
    await apiRequest(`/pdf/annotations/${id}`, {
      method: 'DELETE',
    })
  },

  async getReadingProgress(paperId: string): Promise<PdfReadingProgress | null> {
    try {
      return await apiRequest<PdfReadingProgress>(`/pdf/${encodeURIComponent(paperId)}/progress`)
    } catch {
      return null
    }
  },

  async saveReadingProgress(paperId: string, data: SaveProgressData): Promise<void> {
    await apiRequest(`/pdf/${encodeURIComponent(paperId)}/progress`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async getOutline(paperId: string): Promise<PdfOutlineItem[]> {
    return apiRequest<PdfOutlineItem[]>(`/pdf/${encodeURIComponent(paperId)}/outline`)
  },

  getPdfFileUrl(paperId: string): string {
    return `${API_BASE_URL}/api/pdf/${encodeURIComponent(paperId)}/file`
  },
}
