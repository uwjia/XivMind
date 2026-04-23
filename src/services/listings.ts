import { API_BASE_URL } from './config'
import type { Paper, CodeUrlInfo } from '@/types'
import { TransformBackendPaper } from '@/types'

const LISTINGS_API_BASE = `${API_BASE_URL}/api/listings`

export const listingsAPI = {
  async fetchNewListings(): Promise<{
    success: boolean
    date: string
    new_count: number
    cross_count: number
    replacement_count: number
    total_count: number
    error?: string
  }> {
    const response = await fetch(`${LISTINGS_API_BASE}/fetch`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getListingsIndexes(): Promise<{
    indexes: Array<{
      date: string
      new_count: number
      cross_count: number
      replacement_count: number
      fetched_at: string
    }>
  }> {
    const response = await fetch(`${LISTINGS_API_BASE}/indexes`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getListingsByDate(
    date: string,
    listingType: 'new' | 'cross' | 'replacement' = 'new',
    start: number = 0,
    maxResults: number = 50
  ): Promise<{
    papers: Paper[]
    total: number
    date: string
    listing_type: string
    start: number
    max_results: number
  }> {
    const params = new URLSearchParams({
      listing_type: listingType,
      start: start.toString(),
      max_results: maxResults.toString()
    })
    
    const response = await fetch(`${LISTINGS_API_BASE}/${date}?${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return {
      ...data,
      papers: (data.papers || []).map(TransformBackendPaper)
    }
  },

  async getLatestListings(date?: string): Promise<{
    date: string
    new: Paper[]
    cross: Paper[]
    replacement: Paper[]
    auto_refreshed: boolean
    error?: string
  }> {
    let url = `${LISTINGS_API_BASE}/new`
    if (date) {
      url += `?date=${date}`
    }
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return {
      ...data,
      new: (data.new || []).map(TransformBackendPaper),
      cross: (data.cross || []).map(TransformBackendPaper),
      replacement: (data.replacement || []).map(TransformBackendPaper)
    }
  },

  async checkPapersWithCode(paperIds: string[]): Promise<Record<string, boolean>> {
    if (!paperIds || paperIds.length === 0) {
      return {}
    }
    
    const response = await fetch(`${LISTINGS_API_BASE}/codes/check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ paper_ids: paperIds })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data.codes || {}
  },

  async getCodesForPapers(paperIds: string[]): Promise<Record<string, CodeUrlInfo | null>> {
    if (!paperIds || paperIds.length === 0) {
      return {}
    }
    
    const response = await fetch(`${LISTINGS_API_BASE}/codes/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ paper_ids: paperIds })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    const result: Record<string, CodeUrlInfo | null> = {}
    
    for (const [paperId, code] of Object.entries(data)) {
      if (code) {
        result[paperId] = {
          id: (code as Record<string, unknown>).id as string,
          paperId: (code as Record<string, unknown>).paper_id as string,
          url: (code as Record<string, unknown>).url as string,
          platform: (code as Record<string, unknown>).platform as string,
          owner: (code as Record<string, unknown>).owner as string | undefined,
          repo: (code as Record<string, unknown>).repo as string | undefined,
          isOfficial: (code as Record<string, unknown>).is_official as boolean,
          stars: (code as Record<string, unknown>).stars as number | undefined,
          language: (code as Record<string, unknown>).language as string | undefined,
          fetchedAt: (code as Record<string, unknown>).fetched_at as string | undefined,
        }
      } else {
        result[paperId] = null
      }
    }
    
    return result
  },

  async getPapersWithCode(date: string): Promise<{
    date: string
    new: Paper[]
    cross: Paper[]
    replacement: Paper[]
  }> {
    const response = await fetch(`${LISTINGS_API_BASE}/codes/papers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ date })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return {
      ...data,
      new: (data.new || []).map(TransformBackendPaper),
      cross: (data.cross || []).map(TransformBackendPaper),
      replacement: (data.replacement || []).map(TransformBackendPaper)
    }
  }
}
