import type { FollowedAuthor, FollowedAuthorListResponse, FollowedAuthorCheckResponse } from '@/types/followedAuthor'

import { API_BASE_URL } from './config'

const API_BASE = `${API_BASE_URL}/api/followed-authors`

export const followedAuthorApi = {
  async followAuthor(
    authorName: string,
    notes: string | null = null
  ): Promise<FollowedAuthor> {
    const response = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author_name: authorName,
        notes,
      }),
    })
    if (!response.ok) throw new Error(`Failed to follow author: ${response.statusText}`)
    return response.json()
  },

  async unfollowAuthor(authorName: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/${encodeURIComponent(authorName)}`, {
      method: 'DELETE',
    })
    if (!response.ok) throw new Error(`Failed to unfollow author: ${response.statusText}`)
    return response.json()
  },

  async getFollowedAuthors(limit: number = 2000, offset: number = 0): Promise<FollowedAuthorListResponse> {
    const response = await fetch(`${API_BASE}?limit=${limit}&offset=${offset}`)
    if (!response.ok) throw new Error(`Failed to get followed authors: ${response.statusText}`)
    return response.json()
  },

  async isFollowed(authorName: string): Promise<FollowedAuthorCheckResponse> {
    const response = await fetch(`${API_BASE}/check/${encodeURIComponent(authorName)}`)
    if (!response.ok) throw new Error(`Failed to check if followed: ${response.statusText}`)
    return response.json()
  },

  async updateNotes(authorName: string, notes: string): Promise<FollowedAuthor> {
    const response = await fetch(`${API_BASE}/${encodeURIComponent(authorName)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes }),
    })
    if (!response.ok) throw new Error(`Failed to update notes: ${response.statusText}`)
    return response.json()
  },
}
