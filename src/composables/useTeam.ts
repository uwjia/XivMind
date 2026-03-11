import { ref } from 'vue'
import { teamService } from '@/services/team'
import type {
  TeamResult,
  TeamExecuteRequest,
  TaskAnalysisResult,
  SessionSummary,
  TeamStats,
  SubTaskStatus,
} from '@/types/team'

export function useTeam() {
  const loading = ref(false)
  const executing = ref(false)
  const analyzing = ref(false)
  const currentResult = ref<TeamResult | null>(null)
  const analysisResult = ref<TaskAnalysisResult | null>(null)
  const sessions = ref<string[]>([])
  const stats = ref<TeamStats | null>(null)
  const error = ref<string | null>(null)

  const analyzeTask = async (request: TeamExecuteRequest): Promise<TaskAnalysisResult | null> => {
    analyzing.value = true
    error.value = null
    
    try {
      const result = await teamService.analyzeTask(request)
      analysisResult.value = result
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Analysis failed'
      return null
    } finally {
      analyzing.value = false
    }
  }

  const executeTask = async (request: TeamExecuteRequest): Promise<TeamResult | null> => {
    executing.value = true
    error.value = null
    currentResult.value = null
    
    try {
      const result = await teamService.executeTask(request)
      currentResult.value = result
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Execution failed'
      return null
    } finally {
      executing.value = false
    }
  }

  const loadSessions = async (): Promise<string[]> => {
    loading.value = true
    
    try {
      const data = await teamService.getSessions()
      sessions.value = data.sessions
      return data.sessions
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load sessions'
      return []
    } finally {
      loading.value = false
    }
  }

  const getSession = async (sessionId: string): Promise<Record<string, any> | null> => {
    loading.value = true
    
    try {
      return await teamService.getSession(sessionId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to get session'
      return null
    } finally {
      loading.value = false
    }
  }

  const getSessionSummary = async (sessionId: string): Promise<SessionSummary | null> => {
    loading.value = true
    
    try {
      return await teamService.getSessionSummary(sessionId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to get session summary'
      return null
    } finally {
      loading.value = false
    }
  }

  const cancelSession = async (sessionId: string): Promise<boolean> => {
    try {
      await teamService.cancelSession(sessionId)
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to cancel session'
      return false
    }
  }

  const loadStats = async (): Promise<TeamStats | null> => {
    try {
      const data = await teamService.getStats()
      stats.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load stats'
      return null
    }
  }

  const clearResult = () => {
    currentResult.value = null
    analysisResult.value = null
    error.value = null
  }

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      pending: '#9CA3AF',
      analyzing: '#FBBF24',
      decomposing: '#FBBF24',
      dispatching: '#60A5FA',
      executing: '#3B82F6',
      synthesizing: '#8B5CF6',
      completed: '#10B981',
      failed: '#EF4444',
      cancelled: '#6B7280',
    }
    return colors[status] || '#9CA3AF'
  }

  const getComplexityColor = (complexity: string): string => {
    const colors: Record<string, string> = {
      simple: '#10B981',
      standard: '#3B82F6',
      moderate: '#FBBF24',
      high: '#EF4444',
    }
    return colors[complexity] || '#9CA3AF'
  }

  const getSubTaskStatusIcon = (status: SubTaskStatus): string => {
    const icons: Record<SubTaskStatus, string> = {
      pending: '○',
      queued: '◔',
      running: '◑',
      completed: '●',
      failed: '✕',
      cancelled: '⊘',
    }
    return icons[status] || '○'
  }

  return {
    loading,
    executing,
    analyzing,
    currentResult,
    analysisResult,
    sessions,
    stats,
    error,
    analyzeTask,
    executeTask,
    loadSessions,
    getSession,
    getSessionSummary,
    cancelSession,
    loadStats,
    clearResult,
    getStatusColor,
    getComplexityColor,
    getSubTaskStatusIcon,
  }
}
