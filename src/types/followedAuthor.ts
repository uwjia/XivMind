export interface FollowedAuthor {
  id: string
  author_name: string
  paper_count: number
  latest_published: string | null
  notes: string | null
  followed_at: string
}

export interface FollowedAuthorListResponse {
  total: number
  items: FollowedAuthor[]
}

export interface FollowedAuthorCheckResponse {
  author_name: string
  is_followed: boolean
}
