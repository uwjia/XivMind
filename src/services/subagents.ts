import type {
  SubAgent,
  SubAgentListResponse,
  SubAgentExecuteRequest,
  SubAgentExecuteResponse,
  SubAgentCreateRequest,
  SubAgentReloadResponse,
  SubAgentRawResponse,
} from '../types/subagent'

export type {
  SubAgent,
  SubAgentListResponse,
  SubAgentExecuteRequest,
  SubAgentExecuteResponse,
  SubAgentCreateRequest,
  SubAgentReloadResponse,
  SubAgentRawResponse,
}

const SUBAGENTS_API_BASE = '/api/subagents'

export const subagentsAPI = {
  async getSubAgents(): Promise<SubAgentListResponse> {
    const response = await fetch(SUBAGENTS_API_BASE)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSubAgent(agentId: string): Promise<SubAgent> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSubAgentRaw(agentId: string): Promise<SubAgentRawResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}/raw`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async createSubAgent(data: SubAgentCreateRequest): Promise<SubAgent> {
    const response = await fetch(SUBAGENTS_API_BASE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async saveSubAgent(agentId: string, content: string): Promise<SubAgentReloadResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async deleteSubAgent(agentId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async reloadAllSubAgents(): Promise<SubAgentReloadResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/reload`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async reloadSubAgent(agentId: string): Promise<SubAgentReloadResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}/reload`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async executeSubAgent(
    agentId: string,
    data: SubAgentExecuteRequest
  ): Promise<SubAgentExecuteResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/${agentId}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async delegateTask(data: SubAgentExecuteRequest): Promise<SubAgentExecuteResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/delegate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSubAgentsBySkill(skillId: string): Promise<SubAgentListResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/by-skill/${skillId}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSubAgentsByTool(toolName: string): Promise<SubAgentListResponse> {
    const response = await fetch(`${SUBAGENTS_API_BASE}/by-tool/${toolName}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },
}
