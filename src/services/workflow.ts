import type { 
  Workflow, 
  WorkflowNode,
  SubtasksCreatedEvent,
  DynamicNodeCreatedEvent,
  DynamicEdgeCreatedEvent,
  ExecutionPhaseEvent,
} from '@/types/workflow'
import { API_BASE_URL } from './config'

export interface WorkflowExecuteRequest {
  workflow: Workflow
  input: {
    instruction: string
    paperIds?: string[]
    context?: Record<string, unknown>
  }
}

export interface WorkflowExecuteResponse {
  session_id: string
  status: string
  message: string
}

export interface WorkflowValidationResponse {
  valid: boolean
  errors: string[]
}

export interface NodeStatusEvent {
  nodeId: string
  status: 'idle' | 'pending' | 'running' | 'success' | 'error'
  result?: unknown
  error?: string
  progress?: number
  timestamp: string
}

export interface SessionCompletedEvent {
  sessionId: string
  output?: string
  error?: string
  timestamp: string
}

export interface LogEvent {
  level: 'info' | 'warn' | 'error'
  message: string
  nodeId?: string
  timestamp: string
}

export interface SubtaskStatusEvent {
  subtaskId: string
  status: string
  agentId?: string
  timestamp: string
}

export type ProgressEventHandler = (event: string, data: unknown) => void

const API_BASE = `${API_BASE_URL}/api/team/workflow`

class WorkflowAPI {
  private eventSource: EventSource | null = null
  private handlers: ProgressEventHandler[] = []

  async validate(workflow: Workflow): Promise<WorkflowValidationResponse> {
    const response = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: this._serializeWorkflow(workflow),
        input: { instruction: '' },
      }),
    })
    
    if (!response.ok) {
      throw new Error(`Validation failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  async execute(
    workflow: Workflow,
    input: { instruction: string; paperIds?: string[]; context?: Record<string, unknown> }
  ): Promise<WorkflowExecuteResponse> {
    const response = await fetch(`${API_BASE}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: this._serializeWorkflow(workflow),
        input,
      }),
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || 'Execution failed')
    }
    
    return response.json()
  }

  connectProgressStream(sessionId: string): void {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
    
    const url = `${API_BASE}/stream/${sessionId}`
    this.eventSource = new EventSource(url)
    
    this.eventSource.onopen = () => {
      console.log('[WorkflowAPI] SSE connection opened')
    }
    
    this.eventSource.onerror = (error) => {
      console.error('[WorkflowAPI] SSE error:', error)
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        console.log('[WorkflowAPI] SSE connection closed')
      }
    }
    
    this.eventSource.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data)
      this._notifyHandlers('connected', data)
    })
    
    this.eventSource.addEventListener('node_status', (event) => {
      const data: NodeStatusEvent = JSON.parse(event.data)
      this._notifyHandlers('node_status', data)
    })
    
    this.eventSource.addEventListener('session_created', (event) => {
      const data = JSON.parse(event.data)
      this._notifyHandlers('session_created', data)
    })
    
    this.eventSource.addEventListener('session_completed', (event) => {
      const data: SessionCompletedEvent = JSON.parse(event.data)
      this._notifyHandlers('session_completed', data)
    })
    
    this.eventSource.addEventListener('subtask_status', (event) => {
      const data: SubtaskStatusEvent = JSON.parse(event.data)
      this._notifyHandlers('subtask_status', data)
    })
    
    this.eventSource.addEventListener('log', (event) => {
      const data: LogEvent = JSON.parse(event.data)
      this._notifyHandlers('log', data)
    })
    
    this.eventSource.addEventListener('heartbeat', (event) => {
      const data = JSON.parse(event.data)
      this._notifyHandlers('heartbeat', data)
    })
    
    this.eventSource.addEventListener('subtasks_created', (event) => {
      const data: SubtasksCreatedEvent = JSON.parse(event.data)
      this._notifyHandlers('subtasks_created', data)
    })
    
    this.eventSource.addEventListener('dynamic_node_created', (event) => {
      const data: DynamicNodeCreatedEvent = JSON.parse(event.data)
      this._notifyHandlers('dynamic_node_created', data)
    })
    
    this.eventSource.addEventListener('dynamic_edge_created', (event) => {
      const data: DynamicEdgeCreatedEvent = JSON.parse(event.data)
      this._notifyHandlers('dynamic_edge_created', data)
    })
    
    this.eventSource.addEventListener('execution_phase', (event) => {
      const data: ExecutionPhaseEvent = JSON.parse(event.data)
      this._notifyHandlers('execution_phase', data)
    })
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
    this.handlers = []
  }

  onProgress(handler: ProgressEventHandler): () => void {
    this.handlers.push(handler)
    
    return () => {
      const index = this.handlers.indexOf(handler)
      if (index > -1) {
        this.handlers.splice(index, 1)
      }
    }
  }

  private _notifyHandlers(event: string, data: unknown): void {
    for (const handler of this.handlers) {
      try {
        handler(event, data)
      } catch (error) {
        console.error('[WorkflowAPI] Handler error:', error)
      }
    }
  }

  async cancel(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/cancel/${sessionId}`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`Cancel failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  async executeDynamic(
    workflow: Workflow,
    input: { instruction: string; paperIds?: string[]; context?: Record<string, unknown> }
  ): Promise<WorkflowExecuteResponse> {
    const response = await fetch(`${API_BASE}/dynamic/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: this._serializeWorkflow(workflow),
        input,
      }),
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || 'Dynamic execution failed')
    }
    
    return response.json()
  }

  async cancelDynamic(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/dynamic/cancel/${sessionId}`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`Cancel failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  private _serializeWorkflow(workflow: Workflow): Record<string, unknown> {
    return {
      id: workflow.id,
      name: workflow.name,
      description: workflow.description,
      nodes: workflow.nodes.map(node => this._serializeNode(node)),
      edges: workflow.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourcePort: edge.sourcePort,
        targetPort: edge.targetPort,
        label: edge.label,
      })),
      variables: workflow.variables,
    }
  }

  private _serializeNode(node: WorkflowNode): Record<string, unknown> {
    return {
      id: node.id,
      type: node.type,
      label: node.label,
      position: node.position,
      config: node.config,
      status: node.status,
      inputs: node.inputs,
      outputs: node.outputs,
      result: node.result,
      error: node.error,
    }
  }
}

export const workflowAPI = new WorkflowAPI()
