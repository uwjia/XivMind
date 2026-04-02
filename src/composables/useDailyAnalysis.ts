import { ref } from 'vue'
import { dailyAnalysisAPI, type StreamEvent } from '@/services/dailyAnalysis'
import { useLLMStore } from '@/stores/llm-store'
import type { DailyAnalysisResult, AnalysisMode, AnalysisLanguage } from '@/types/dailyAnalysis'

interface StreamingHighValuePaper {
  paper_id: string
  title: string
  innovation_type: string
  innovation_description: string
  confidence: number
}

interface StreamingRecommendPaper {
  paper_id: string
  title: string
  relevance_score: number
  matched_interests: string[]
  reason: string
}

export function useDailyAnalysis() {
  const llmStore = useLLMStore()
  
  const isAnalyzing = ref(false)
  const currentProgress = ref<string>('')
  const analysisProgress = ref<{ current: number; total: number; title: string } | null>(null)
  const analysisResult = ref<DailyAnalysisResult | null>(null)
  const streamingHighValueResults = ref<StreamingHighValuePaper[]>([])
  const streamingRecommendResults = ref<StreamingRecommendPaper[]>([])
  const error = ref<string | null>(null)
  const totalPapers = ref<number>(0)
  
  const startStreamAnalysis = async (
    date: string,
    mode: AnalysisMode = 'full',
    userInterests?: string[],
    language: AnalysisLanguage = 'en',
    maxPapers: number = 50
  ): Promise<DailyAnalysisResult | null> => {
    isAnalyzing.value = true
    error.value = null
    currentProgress.value = 'Starting analysis...'
    analysisProgress.value = null
    streamingHighValueResults.value = []
    streamingRecommendResults.value = []
    
    const result: DailyAnalysisResult = {
      date,
      total_papers: 0,
      summary: null,
      main_themes: null,
      trends: null,
      high_value_papers: [],
      recommendations: [],
    }
    
    analysisResult.value = result
    
    try {
      const eventGenerator = dailyAnalysisAPI.streamAnalysis({
        date,
        mode,
        userInterests,
        provider: llmStore.selectedProvider || undefined,
        model: llmStore.selectedModel || undefined,
        language,
        maxPapers,
      })
      
      for await (const event of eventGenerator) {
        processEvent(event, result)
      }
      
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Analysis failed'
      return null
    } finally {
      isAnalyzing.value = false
      analysisProgress.value = null
    }
  }
  
  const processEvent = (event: StreamEvent, result: DailyAnalysisResult) => {
    const { type, content } = event
    
    if (type === 'status') {
      currentProgress.value = content as unknown as string
      analysisProgress.value = null
    } else if (type === 'progress') {
      analysisProgress.value = content as { current: number; total: number; title: string }
    } else if (type === 'error') {
      error.value = content as unknown as string
    } else if (type === 'done') {
      currentProgress.value = content as unknown as string
      analysisProgress.value = null
    } else {
      updateResult(result, type, content)
      analysisResult.value = { ...result }
    }
  }
  
  const updateResult = (
    result: DailyAnalysisResult, 
    type: string, 
    content: Record<string, unknown>
  ) => {
    const updateMap: Record<string, () => void> = {
      summary: () => {
        result.summary = content.summary as string
        result.main_themes = content.main_themes as string[]
      },
      trends: () => {
        result.trends = content.trends as DailyAnalysisResult['trends']
      },
      high_value: () => {
        result.high_value_papers = content.high_value_papers as DailyAnalysisResult['high_value_papers']
      },
      high_value_item: () => {
        if (!result.high_value_papers) result.high_value_papers = []
        const paper = content as unknown as StreamingHighValuePaper
        streamingHighValueResults.value = [...streamingHighValueResults.value, paper]
      },
      high_value_final: () => {
        result.high_value_papers = content.high_value_papers as DailyAnalysisResult['high_value_papers']
      },
      recommendations: () => {
        result.recommendations = content.recommendations as DailyAnalysisResult['recommendations']
      },
      recommend_item: () => {
        if (!result.recommendations) result.recommendations = []
        const paper = content as unknown as StreamingRecommendPaper
        streamingRecommendResults.value = [...streamingRecommendResults.value, paper]
      },
      recommend_final: () => {
        result.recommendations = content.recommendations as DailyAnalysisResult['recommendations']
      },
    }
    
    if (updateMap[type]) {
      updateMap[type]()
    }
  }
  
  const clearResult = () => {
    analysisResult.value = null
    error.value = null
    currentProgress.value = ''
    analysisProgress.value = null
    streamingHighValueResults.value = []
    streamingRecommendResults.value = []
  }
  
  const fetchPaperCount = async (date: string): Promise<number> => {
    try {
      const data = await dailyAnalysisAPI.fetchPaperCount(date)
      totalPapers.value = data.total_papers
      return data.total_papers
    } catch (e) {
      console.error('Failed to fetch paper count:', e)
      return 0
    }
  }
  
  return {
    isAnalyzing,
    currentProgress,
    analysisProgress,
    analysisResult,
    streamingHighValueResults,
    streamingRecommendResults,
    error,
    totalPapers,
    startStreamAnalysis,
    clearResult,
    fetchPaperCount,
  }
}
