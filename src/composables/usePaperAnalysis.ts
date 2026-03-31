import { ref, computed } from 'vue'
import { useLLMStore } from '@/stores/llm-store'
import { useToastStore } from '@/stores/toast-store'

export interface KeyPoint {
  title: string
  description: string
  importance: 'high' | 'medium' | 'low'
}

export interface QuestionAndConclusion {
  question: string
  conclusion: string
}

export interface AnalysisResult {
  paper_id: string
  summary: string | null
  key_points: KeyPoint[] | null
  methodology: string | null
  questions_and_conclusions: QuestionAndConclusion[] | null
  analyzed_at: string
  service_used: string
  model_used: string
}

export type AnalysisType = 'full' | 'summary' | 'keypoints' | 'methodology' | 'questions'

const API_BASE = '/api/papers'

const PROGRESS_MAP: Record<string, number> = {
  summary: 25,
  keypoints: 50,
  methodology: 75,
  questions_conclusions: 90,
}

export function usePaperAnalysis() {
  const llmStore = useLLMStore()
  const toastStore = useToastStore()
  
  const isAnalyzing = ref(false)
  const currentProgress = ref<string>('')
  const analysisResult = ref<AnalysisResult | null>(null)
  const error = ref<string | null>(null)
  
  const analysisCache = ref<Map<string, AnalysisResult>>(new Map())
  
  const selectedProvider = computed(() => llmStore.selectedProvider)
  const selectedModel = computed(() => llmStore.selectedModel)
  
  const progressPercentage = computed(() => {
    if (!currentProgress.value) return 0
    for (const [key, value] of Object.entries(PROGRESS_MAP)) {
      if (currentProgress.value.includes(key)) return value
    }
    return 10
  })
  
  const getCacheKey = (paperId: string, analysisType: AnalysisType, language: string) => 
    `${paperId}:${analysisType}:${language}`
  
  const mergeResult = (
    result: Partial<AnalysisResult>,
    type: string,
    content: Record<string, unknown>
  ): Partial<AnalysisResult> => {
    const fieldMap: Record<string, keyof AnalysisResult> = {
      summary: 'summary',
      keypoints: 'key_points',
      methodology: 'methodology',
      questions_conclusions: 'questions_and_conclusions',
    }
    
    const field = fieldMap[type]
    if (field && content) {
      (result as Record<string, unknown>)[field] = content[field === 'key_points' ? 'key_points' : field] ?? 
        (field === 'summary' ? content.summary : 
         field === 'methodology' ? content.methodology :
         content.questions_and_conclusions)
    }
    return result
  }
  
  const startStreamAnalysis = async (
    paperId: string,
    analysisType: AnalysisType = 'full',
    language: string = 'en'
  ): Promise<AnalysisResult | null> => {
    clearResult()
    
    isAnalyzing.value = true
    error.value = null
    currentProgress.value = 'Starting analysis...'
    
    const result: Partial<AnalysisResult> = {
      paper_id: paperId,
      service_used: selectedProvider.value || '',
      model_used: selectedModel.value || '',
    }
    
    try {
      const response = await fetch(`${API_BASE}/${paperId}/analyze/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service: selectedProvider.value || undefined,
          model: selectedModel.value || undefined,
          analysis_type: analysisType,
          language,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }
      
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }
      
      const decoder = new TextDecoder()
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              
              if (event.type === 'status') {
                currentProgress.value = event.content
              } else if (event.type === 'error') {
                throw new Error(event.content)
              } else if (event.content) {
                mergeResult(result, event.type, event.content)
                analysisResult.value = result as AnalysisResult
              }
            } catch (parseError) {
              if (parseError instanceof Error) {
                error.value = parseError.message
                toastStore.showError(error.value)
              }
            }
          }
        }
      }
      
      result.analyzed_at = new Date().toISOString()
      analysisResult.value = result as AnalysisResult
      
      const cacheKey = getCacheKey(paperId, analysisType, language)
      analysisCache.value.set(cacheKey, result as AnalysisResult)
      
      return result as AnalysisResult
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Analysis failed'
      toastStore.showError(error.value)
      return null
    } finally {
      isAnalyzing.value = false
      currentProgress.value = ''
    }
  }
  
  const analyzePaper = async (
    paperId: string,
    analysisType: AnalysisType = 'full',
    language: string = 'en'
  ): Promise<AnalysisResult | null> => {
    const cacheKey = getCacheKey(paperId, analysisType, language)
    
    if (analysisCache.value.has(cacheKey)) {
      const cached = analysisCache.value.get(cacheKey)!
      analysisResult.value = cached
      return cached
    }
    
    isAnalyzing.value = true
    error.value = null
    currentProgress.value = 'Starting analysis...'
    
    try {
      const response = await fetch(`${API_BASE}/${paperId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service: selectedProvider.value || undefined,
          model: selectedModel.value || undefined,
          analysis_type: analysisType,
          language,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.error || 'Analysis failed')
      }
      
      analysisResult.value = data.result
      analysisCache.value.set(cacheKey, data.result)
      
      return data.result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Analysis failed'
      toastStore.showError(error.value)
      return null
    } finally {
      isAnalyzing.value = false
      currentProgress.value = ''
    }
  }
  
  const clearResult = () => {
    analysisResult.value = null
    error.value = null
  }
  
  const getCachedAnalysis = (
    paperId: string, 
    analysisType: AnalysisType = 'full', 
    language: string = 'en'
  ): AnalysisResult | null => {
    const cacheKey = getCacheKey(paperId, analysisType, language)
    const cached = analysisCache.value.get(cacheKey) || null
    if (cached) {
      analysisResult.value = cached
    }
    return cached
  }
  
  return {
    isAnalyzing,
    currentProgress,
    progressPercentage,
    analysisResult,
    error,
    selectedProvider,
    selectedModel,
    analyzePaper,
    startStreamAnalysis,
    clearResult,
    getCachedAnalysis,
  }
}
