import { ref, type Ref } from 'vue'
import { useSkills } from './useSkills'
import type { Skill, RelatedPaper } from '../services/skills'
import type { Message } from './useChatMessages'

interface SkillExecutionResult {
  success: boolean
  content: string
  error?: string
}

export function useSkillExecution(
  skillsMessages: Ref<Message[]>,
  addUserMessage: (content: string, options?: Partial<Message>) => void,
  scrollToBottom: () => void
) {
  const { skills, loading: skillsLoading, loadSkills, executeSkill: executeSkillApi } = useSkills()
  
  const selectedSkill = ref<Skill | null>(null)
  const skillExecuted = ref(false)
  const isLoading = ref(false)

  const selectSkill = (skill: Skill) => {
    if (!skill.available) return
    selectedSkill.value = skill
    skillExecuted.value = false
    skillsMessages.value = []
  }

  const formatSkillResult = (result: Record<string, unknown>): string => {
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

  const handleSkillExecute = async (paperIds: string[], params: Record<string, unknown>): Promise<SkillExecutionResult> => {
    if (!selectedSkill.value) {
      return { success: false, content: '', error: 'No skill selected' }
    }
    
    skillExecuted.value = true
    
    const paperIdText = paperIds.length > 0 ? paperIds.join(', ') : 'No paper ID'
    addUserMessage(`**${selectedSkill.value.name}** on: ${paperIdText}`, {
      skillId: selectedSkill.value.id,
      skillName: selectedSkill.value.name,
      paperIds: paperIds,
      skillParams: params
    })
    
    isLoading.value = true
    scrollToBottom()
    
    try {
      const result = await executeSkillApi({
        skillId: selectedSkill.value.id,
        paperIds,
        params
      })
      
      if (result && result.success) {
        const responseContent = formatSkillResult(result as unknown as Record<string, unknown>)
        
        skillsMessages.value.push({
          role: 'assistant',
          content: responseContent
        })
        
        return { success: true, content: responseContent }
      } else {
        const errorContent = `Error: ${result?.error || 'Failed to execute skill'}`
        skillsMessages.value.push({
          role: 'assistant',
          content: errorContent
        })
        return { success: false, content: errorContent, error: result?.error }
      }
    } catch (error) {
      const errorContent = `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`
      skillsMessages.value.push({
        role: 'assistant',
        content: errorContent
      })
      return { success: false, content: errorContent, error: errorContent }
    } finally {
      isLoading.value = false
      scrollToBottom()
    }
  }

  const runSkillAgain = () => {
    skillExecuted.value = false
    skillsMessages.value = []
  }

  const backToSkills = () => {
    selectedSkill.value = null
    skillExecuted.value = false
    skillsMessages.value = []
  }

  const ensureSkillsLoaded = async () => {
    if (skills.value.length === 0) {
      await loadSkills()
    }
  }

  return {
    skills,
    skillsLoading,
    selectedSkill,
    skillExecuted,
    isLoading,
    selectSkill,
    handleSkillExecute,
    runSkillAgain,
    backToSkills,
    ensureSkillsLoaded,
    loadSkills
  }
}
