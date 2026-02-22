export interface Skill {
  id: string
  name: string
  description: string
  icon: string
  category: string
  requires_paper: boolean
  available: boolean
  input_schema: InputSchema | null
  source?: 'dynamic' | 'builtin'
  file_path?: string
  loaded_at?: string
}

export interface InputSchema {
  type: 'object'
  properties: Record<string, SchemaProperty>
  required?: string[]
}

export interface SchemaProperty {
  type: 'string' | 'integer' | 'boolean' | 'text'
  description?: string
  enum?: string[]
  default?: string | number | boolean
  minimum?: number
  maximum?: number
}

export interface SkillsResponse {
  skills: Skill[]
  total: number
}

export interface RelatedPaper {
  id: string
  title: string
  authors: string[]
  abstract?: string
  similarity_score: number
}

export interface SkillExecuteResponse {
  success: boolean
  error?: string
  skill_id?: string
  skill_name?: string
  paper_id?: string
  paper_title?: string
  result?: string
  summary?: string
  translation?: string
  target_language?: string
  citations?: Record<string, string>
  related_papers?: RelatedPaper[]
  total?: number
  [key: string]: unknown
}

export interface SkillRawResponse {
  skill_id: string
  content: string
}

export interface SkillReloadResponse {
  success: boolean
  unloaded?: number
  loaded?: number
  skill_id?: string
  message?: string
}

export interface FormField {
  key: string
  label: string
  type: 'string' | 'integer' | 'boolean' | 'text' | 'select'
  description?: string
  enum?: string[]
  default?: string | number | boolean
  minimum?: number
  maximum?: number
  required: boolean
}
