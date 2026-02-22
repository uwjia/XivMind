import type { 
  Skill, 
  SkillsResponse, 
  SkillExecuteResponse, 
  SkillRawResponse, 
  SkillReloadResponse,
  RelatedPaper 
} from '../types/skill'

export type { 
  Skill, 
  SkillsResponse, 
  SkillExecuteResponse, 
  SkillRawResponse, 
  SkillReloadResponse,
  RelatedPaper 
}

const SKILLS_API_BASE = '/api/skills'

export const skillsAPI = {
  async getSkills(): Promise<SkillsResponse> {
    const response = await fetch(SKILLS_API_BASE)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSkill(skillId: string): Promise<Skill> {
    const response = await fetch(`${SKILLS_API_BASE}/${skillId}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async getSkillRaw(skillId: string): Promise<SkillRawResponse> {
    const response = await fetch(`${SKILLS_API_BASE}/${skillId}/raw`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async executeSkill(
    skillId: string,
    paperIds?: string[],
    params?: Record<string, unknown>,
    provider?: string,
    model?: string
  ): Promise<SkillExecuteResponse> {
    const response = await fetch(`${SKILLS_API_BASE}/${skillId}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        paper_ids: paperIds,
        params: params,
        provider: provider,
        model: model,
      }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async reloadSkills(): Promise<SkillReloadResponse> {
    const response = await fetch(`${SKILLS_API_BASE}/reload`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async reloadSkill(skillId: string): Promise<SkillReloadResponse> {
    const response = await fetch(`${SKILLS_API_BASE}/${skillId}/reload`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },

  async saveSkill(skillId: string, content: string): Promise<SkillReloadResponse> {
    const response = await fetch(`${SKILLS_API_BASE}/${skillId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
}
