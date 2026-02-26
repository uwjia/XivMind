export interface SubAgent {
  id: string
  name: string
  description: string
  icon: string
  skills: string[]
  tools: string[]
  max_turns: number
  temperature: number
  model?: string
  provider?: string
  available: boolean
  source: 'builtin' | 'dynamic'
  file_path?: string
  loaded_at?: string
  language: 'en' | 'zh'
}

export interface SubAgentListResponse {
  agents: SubAgent[]
  total: number
}

export interface SubAgentExecuteRequest {
  instruction: string
  paper_ids?: string[]
  context?: Record<string, unknown>
  provider?: string
  model?: string
  max_turns?: number
}

export interface SubAgentMessage {
  role: string
  content: string
  name?: string
  tool_call_id?: string
  timestamp?: string
}

export interface SubAgentExecuteResponse {
  task_id: string
  agent_id: string
  status: string
  output: string
  messages: SubAgentMessage[]
  error?: string
  model?: string
  provider?: string
  turns_used: number
}

export interface SubAgentResult {
  task_id: string
  agent_id: string
  status: 'running' | 'completed' | 'failed'
  output: string
  messages: SubAgentMessage[]
  error?: string
  model?: string
  provider?: string
  turns_used: number
}

export interface SubAgentCreateRequest {
  id: string
  name: string
  description?: string
  skills?: string[]
  tools?: string[]
  system_prompt?: string
}

export interface SubAgentSaveRequest {
  content: string
}

export interface SubAgentReloadResponse {
  success: boolean
  unloaded: number
  loaded: number
  message?: string
}

export interface SubAgentRawResponse {
  agent_id: string
  content: string
}

export type SubAgentStatus = 'idle' | 'running' | 'completed' | 'failed' | 'cancelled'
