export type MemoryType = 'core' | 'recall' | 'archival'

export type MemoryCategory = 'fact' | 'preference' | 'context' | 'insight' | 'task'

export interface MemoryConfig {
  auto_capture: boolean
  auto_recall: boolean
  capture_max_chars: number
  recall_top_k: number
  recall_min_score: number
  auto_forget_days: number
  importance_threshold: number
  extract: boolean
}

export interface SoulMemory {
  user_id: string
  core_instructions: string
  behavior_rules: string[]
  created_at: string
  version: string
}

export interface ToolsMemory {
  user_id: string
  enabled_tools: string[]
  tool_preferences: Record<string, unknown>
  last_updated: string
}

export interface CoreMemory {
  user_id: string
  research_interests: string[]
  preferred_domains: string[]
  frequently_used_skills: string[]
  language_preference: string
  summary_style: 'detailed' | 'brief' | 'bullet_points'
  custom_instructions: string
  created_at: string
  updated_at: string
}

export interface RecallMemory {
  memory_id: string
  user_id: string
  session_id: string
  timestamp: string
  content: string
  embedding?: number[]
  metadata: Record<string, unknown>
  importance_score: number
  access_count: number
  category: MemoryCategory
  ttl_days?: number
  auto_created: boolean
}

export interface ArchivalMemory {
  memory_id: string
  user_id: string
  content_type: 'note' | 'insight' | 'summary'
  title: string
  content: string
  embedding?: number[]
  source_papers: string[]
  tags: string[]
  created_at: string
  last_accessed: string
}

export interface MemoryStats {
  core_memory_exists: boolean
  recall_memory_count: number
  archival_memory_count: number
  total_memories: number
  oldest_memory?: string
  newest_memory?: string
  auto_created_count: number
  by_category: Record<string, number>
}

export interface MemorySearchResult {
  memory_id: string
  content: string
  similarity_score: number
  memory_type: MemoryType
  timestamp: string
  metadata: Record<string, unknown>
  category: MemoryCategory
  importance_score: number
}

export interface MemoryContextResult {
  memories: MemorySearchResult[]
  context_string: string
}

export interface CoreMemoryUpdate {
  research_interests?: string[]
  preferred_domains?: string[]
  frequently_used_skills?: string[]
  language_preference?: string
  summary_style?: 'detailed' | 'brief' | 'bullet_points'
  custom_instructions?: string
}

export interface RecallMemoryCreate {
  content: string
  session_id?: string
  metadata?: Record<string, unknown>
  importance_score?: number
}

export interface ArchivalMemoryCreate {
  content_type?: 'note' | 'insight' | 'summary'
  title?: string
  content: string
  source_papers?: string[]
  tags?: string[]
}

export interface MemoryContext {
  core_memory: CoreMemory | null
  relevant_memories: MemorySearchResult[]
  context_string: string
}

export interface ProcessConversationRequest {
  session_id: string
  user_message: string
  assistant_message: string
  extract?: boolean
}

export interface MemoryExtractionResult {
  status: 'processing'
  task_id: string
  message: string
}

export interface MemoryExtractionData {
  user_preferences: string[]
  research_interests: string[]
  important_facts: string[]
  should_update_core: boolean
  importance_score: number
}
