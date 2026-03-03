import { ref } from 'vue'
import { skillsAPI } from '../services/skills'
import { useLLMStore } from '../stores/llm-store'
import type { Skill, SkillExecuteResponse, RelatedPaper } from '../types/skill'

interface ExecuteSkillParams {
  skillId: string
  paperIds: string[]
  params: Record<string, unknown>
}

export function formatSkillResult(result: Record<string, unknown>): string {
  if (result.summary) {
    return `**Summary**\n\n${result.summary}`
  }
  
  if (result.translation) {
    return `**Translation (${result.target_language})**\n\n${result.translation}`
  }
  
  if (result.citations) {
    let content = '**Citations**\n\n'
    for (const [format, citation] of Object.entries(result.citations as Record<string, string>)) {
      content += `**${format}:**\n\`\`\`\n${citation}\n\`\`\`\n\n`
    }
    return content
  }
  
  if (result.related_papers && Array.isArray(result.related_papers)) {
    let content = `**Related Papers** (${result.total || result.related_papers.length} found)\n\n`
    result.related_papers.forEach((paper: RelatedPaper, index: number) => {
      content += `${index + 1}. **${paper.title}**\n   ${paper.authors?.slice(0, 2).join(', ')}\n   Similarity: ${(paper.similarity_score * 100).toFixed(1)}%\n\n`
    })
    return content
  }
  
  if (result.result) {
    return `**${result.skill_name || 'Result'}**\n\n${result.result}`
  }
  
  return JSON.stringify(result, null, 2)
}

export function useSkills() {
  const skills = ref<Skill[]>([])
  const loading = ref(false)
  const executing = ref(false)
  const error = ref<string | null>(null)
  const saving = ref(false)
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
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute skill'
      error.value = errorMessage
      console.error('Failed to execute skill:', err)
      return { success: false, error: errorMessage }
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

  const getSkillRaw = async (skillId: string): Promise<{ content: string } | null> => {
    try {
      const result = await skillsAPI.getSkillRaw(skillId)
      return result
    } catch (err) {
      console.error('Failed to get skill raw content:', err)
      return null
    }
  }

  const saveSkillContent = async (skillId: string, content: string): Promise<{ success: boolean; message?: string }> => {
    saving.value = true
    try {
      const result = await skillsAPI.saveSkill(skillId, content)
      if (result.success) {
        await loadSkills()
      }
      return result
    } catch (err) {
      console.error('Failed to save skill:', err)
      return { success: false, message: err instanceof Error ? err.message : 'Failed to save' }
    } finally {
      saving.value = false
    }
  }

  return {
    skills,
    loading,
    executing,
    saving,
    error,
    loadSkills,
    executeSkill,
    reloadSkill,
    reloadAllSkills,
    getSkillById,
    getSkillsByCategory,
    getSkillRaw,
    saveSkillContent
  }
}
