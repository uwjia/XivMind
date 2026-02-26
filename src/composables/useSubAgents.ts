import { ref, computed } from 'vue'
import { subagentsAPI } from '../services/subagents'
import { useLLMStore } from '../stores/llm-store'
import type {
  SubAgent,
  SubAgentExecuteRequest,
  SubAgentExecuteResponse,
  SubAgentCreateRequest,
  SubAgentReloadResponse,
} from '../types/subagent'

export function useSubAgents() {
  const agents = ref<SubAgent[]>([])
  const loading = ref(false)
  const executing = ref(false)
  const error = ref<string | null>(null)
  const selectedAgent = ref<SubAgent | null>(null)
  const executionResult = ref<SubAgentExecuteResponse | null>(null)
  const activeFilter = ref('all')
  const llmStore = useLLMStore()

  const loadSubAgents = async (): Promise<SubAgent[]> => {
    loading.value = true
    error.value = null
    try {
      const result = await subagentsAPI.getSubAgents()
      agents.value = result.agents || []
      return agents.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load subagents'
      console.error('Failed to load subagents:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  const executeSubAgent = async (
    agentId: string,
    params: Omit<SubAgentExecuteRequest, 'provider' | 'model'>
  ): Promise<SubAgentExecuteResponse | null> => {
    executing.value = true
    error.value = null
    executionResult.value = null
    try {
      const result = await subagentsAPI.executeSubAgent(agentId, {
        ...params,
        provider: llmStore.selectedProvider || undefined,
        model: llmStore.selectedModel || undefined,
      })
      executionResult.value = result
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to execute subagent'
      console.error('Failed to execute subagent:', err)
      return null
    } finally {
      executing.value = false
    }
  }

  const delegateTask = async (
    params: Omit<SubAgentExecuteRequest, 'provider' | 'model'>
  ): Promise<SubAgentExecuteResponse | null> => {
    executing.value = true
    error.value = null
    executionResult.value = null
    try {
      const result = await subagentsAPI.delegateTask({
        ...params,
        provider: llmStore.selectedProvider || undefined,
        model: llmStore.selectedModel || undefined,
      })
      executionResult.value = result
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delegate task'
      console.error('Failed to delegate task:', err)
      return null
    } finally {
      executing.value = false
    }
  }

  const createSubAgent = async (data: SubAgentCreateRequest): Promise<SubAgent | null> => {
    loading.value = true
    error.value = null
    try {
      const result = await subagentsAPI.createSubAgent(data)
      await loadSubAgents()
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create subagent'
      console.error('Failed to create subagent:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const saveSubAgent = async (agentId: string, content: string): Promise<SubAgentReloadResponse | null> => {
    loading.value = true
    error.value = null
    try {
      const result = await subagentsAPI.saveSubAgent(agentId, content)
      if (result.success) {
        await loadSubAgents()
      }
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to save subagent'
      console.error('Failed to save subagent:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteSubAgent = async (agentId: string): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      const result = await subagentsAPI.deleteSubAgent(agentId)
      if (result.success) {
        await loadSubAgents()
      }
      return result.success
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete subagent'
      console.error('Failed to delete subagent:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const reloadSubAgents = async (): Promise<SubAgentReloadResponse> => {
    loading.value = true
    try {
      const result = await subagentsAPI.reloadAllSubAgents()
      await loadSubAgents()
      return result
    } catch (err) {
      console.error('Failed to reload subagents:', err)
      return { success: false, unloaded: 0, loaded: 0, message: err instanceof Error ? err.message : 'Failed to reload' }
    } finally {
      loading.value = false
    }
  }

  const reloadSubAgent = async (agentId: string): Promise<SubAgentReloadResponse> => {
    try {
      const result = await subagentsAPI.reloadSubAgent(agentId)
      if (result.success) {
        await loadSubAgents()
      }
      return result
    } catch (err) {
      console.error('Failed to reload subagent:', err)
      return { success: false, unloaded: 0, loaded: 0, message: err instanceof Error ? err.message : 'Failed to reload' }
    }
  }

  const getSubAgentById = (agentId: string): SubAgent | undefined => {
    return agents.value.find(a => a.id === agentId)
  }

  const getSubAgentsBySkill = (skillId: string): SubAgent[] => {
    return agents.value.filter(a => a.skills.includes(skillId))
  }

  const getSubAgentsByTool = (toolName: string): SubAgent[] => {
    return agents.value.filter(a => a.tools.includes(toolName))
  }

  const filteredAgents = computed(() => {
    if (activeFilter.value === 'all') return agents.value
    if (activeFilter.value === 'builtin') return agents.value.filter(a => a.source === 'builtin')
    if (activeFilter.value === 'dynamic') return agents.value.filter(a => a.source === 'dynamic')
    if (activeFilter.value.startsWith('skill:')) {
      const skillId = activeFilter.value.slice(6)
      return agents.value.filter(a => a.skills.includes(skillId))
    }
    if (activeFilter.value.startsWith('tool:')) {
      const toolName = activeFilter.value.slice(5)
      return agents.value.filter(a => a.tools.includes(toolName))
    }
    return agents.value
  })

  const allSkills = computed(() => {
    const skills = new Set<string>()
    agents.value.forEach(a => a.skills.forEach(s => skills.add(s)))
    return Array.from(skills)
  })

  const allTools = computed(() => {
    const tools = new Set<string>()
    agents.value.forEach(a => a.tools.forEach(t => tools.add(t)))
    return Array.from(tools)
  })

  const selectAgent = (agent: SubAgent | null) => {
    selectedAgent.value = agent
  }

  const clearExecutionResult = () => {
    executionResult.value = null
  }

  return {
    agents,
    loading,
    executing,
    error,
    selectedAgent,
    executionResult,
    activeFilter,
    filteredAgents,
    allSkills,
    allTools,
    loadSubAgents,
    executeSubAgent,
    delegateTask,
    createSubAgent,
    saveSubAgent,
    deleteSubAgent,
    reloadSubAgents,
    reloadSubAgent,
    getSubAgentById,
    getSubAgentsBySkill,
    getSubAgentsByTool,
    selectAgent,
    clearExecutionResult,
  }
}
