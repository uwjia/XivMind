export interface ConversationMeta {
  session_id: string
  user_id: string
  title: string
  mode: string
  created_at: string
  updated_at: string
  starred: boolean
  pinned: boolean
  message_count: number
}

export interface ConversationCreate {
  title?: string
  mode?: string
}

export interface ConversationUpdate {
  title?: string
  starred?: boolean
  pinned?: boolean
  mode?: string
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  papers?: PaperInfo[]
  answer?: string
  references?: ReferenceInfo[]
}

export interface PaperInfo {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  similarity_score: number
}

export interface ReferenceInfo {
  id: string
  title: string
  authors: string[]
  published?: string
  relevance_score: number
}

export interface ConversationMessagesResponse {
  session_id: string
  messages: ConversationMessage[]
}
