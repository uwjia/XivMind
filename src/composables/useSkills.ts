import { ref } from 'vue'
import { skillsAPI } from '../services/skills'
import { useLLMStore } from '../stores/llm-store'
import type { Skill, SkillExecuteResponse } from '../types/skill'

interface ExecuteSkillParams {
  skillId: string
  paperIds: string[]
  params: Record<string, unknown>
}

export function useSkills() {
  const skills = ref<Skill[]>([])
  const loading = ref(false)
  const executing = ref(false)
  const error = ref<string | null>(null)
  const llmStore = useLLMStore()

  const loadSkills = async (): Promise<Skill[]> => {
    loading.value = true
    error.value = null
    try {
      const result = await skillsAPI.getSkills()
      skills.value = result.skills || []
      return skills.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load skills'
      console.error('Failed to load skills:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  const executeSkill = async (
    params: ExecuteSkillParams
  ): Promise<SkillExecuteResponse | null> => {
    executing.value = true
    error.value = null
    try {
      const result = await skillsAPI.executeSkill(
        params.skillId,
        params.paperIds,
        params.params,
        llmStore.selectedProvider || undefined,
        llmStore.selectedModel || undefined
      )
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to execute skill'
      console.error('Failed to execute skill:', err)
      return null
    } finally {
      executing.value = false
    }
  }

  const reloadSkill = async (skillId: string): Promise<{ success: boolean; message?: string }> => {
    try {
      const result = await skillsAPI.reloadSkill(skillId)
      if (result.success) {
        await loadSkills()
      }
      return result
    } catch (err) {
      console.error('Failed to reload skill:', err)
      return { success: false, message: err instanceof Error ? err.message : 'Failed to reload' }
    }
  }

  const reloadAllSkills = async () => {
    loading.value = true
    try {
      const result = await skillsAPI.reloadSkills()
      await loadSkills()
      return { loaded: result.loaded ?? 0, message: result.message }
    } catch (err) {
      console.error('Failed to reload all skills:', err)
      return { loaded: 0, message: err instanceof Error ? err.message : 'Failed to reload' }
    } finally {
      loading.value = false
    }
  }

  const getSkillById = (skillId: string): Skill | undefined => {
    return skills.value.find(s => s.id === skillId)
  }

  const getSkillsByCategory = (category: string): Skill[] => {
    if (category === 'all') return skills.value
    if (category === 'dynamic') return skills.value.filter(s => s.source === 'dynamic')
    if (category === 'builtin') return skills.value.filter(s => s.source !== 'dynamic')
    return skills.value.filter(s => s.category === category)
  }

  return {
    skills,
    loading,
    executing,
    error,
    loadSkills,
    executeSkill,
    reloadSkill,
    reloadAllSkills,
    getSkillById,
    getSkillsByCategory
  }
}
