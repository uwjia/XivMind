import { API_BASE_URL } from './config'
import type { Paper } from '@/types'
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
  }
}
