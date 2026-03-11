export type TaskComplexity = 'simple' | 'standard' | 'moderate' | 'high'

export type TeamTaskStatus = 
  | 'pending' 
  | 'analyzing' 
  | 'decomposing' 
  | 'dispatching' 
  | 'executing' 
  | 'synthesizing' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'

export type SubTaskStatus = 
  | 'pending' 
  | 'queued' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'

export interface SubTask {
  id: string
  parent_task_id: string
  instruction: string
  assigned_agent: string | null
  dependencies: string[]
  status: SubTaskStatus
  result: string | null
  error: string | null
  started_at: string | null
  completed_at: string | null
  metadata: Record<string, any>
}

export interface TeamTask {
  id: string
  instruction: string
  complexity: TaskComplexity
  subtasks: SubTask[]
  status: TeamTaskStatus
  context: Record<string, any>
  paper_ids: string[] | null
  provider: string | null
  model: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface TeamMessage {
  role: 'user' | 'lead' | 'subagent' | 'system'
  content: string
  agent_id: string | null
  subtask_id: string | null
  timestamp: string
  metadata: Record<string, any>
}

export interface SubTaskResult {
  subtask_id: string
  agent_id: string
  status: SubTaskStatus
  result: string | null
  error: string | null
  started_at: string | null
  completed_at: string | null
}

export interface TeamResult {
  task_id: string
  session_id: string
  status: TeamTaskStatus
  output: string
  subtask_results: SubTaskResult[]
  messages: TeamMessage[]
  error: string | null
  complexity: TaskComplexity
  total_subtasks: number
  completed_subtasks: number
  failed_subtasks: number
  started_at: string | null
  completed_at: string | null
}

export interface TeamExecuteRequest {
  instruction: string
  context?: Record<string, any>
  paper_ids?: string[]
  provider?: string
  model?: string
  force_team_mode?: boolean
}

export interface TaskAnalysisResult {
  complexity: TaskComplexity
  use_team_mode: boolean
  subtasks: Array<{
    instruction: string
    assigned_agent: string
    task_type: string
    dependencies?: number[]
    metadata?: Record<string, any>
  }>
  reasoning: string
}

export interface SessionSummary {
  session_id: string
  task_id: string | null
  instruction: string | null
  status: string | null
  total_subtasks: number
  completed_subtasks: number
  failed_subtasks: number
  message_count: number
}

export interface TeamStats {
  initialized: boolean
  orchestrator_stats: {
    active_sessions: number
    executor_stats: {
      max_concurrent: number
      timeout: number
      active_tasks: number
    }
  }
  available_agents: string[]
}
