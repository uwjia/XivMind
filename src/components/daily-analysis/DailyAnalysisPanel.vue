<template>
  <div class="daily-analysis-panel">
    <div class="panel-content">
      <div class="analysis-controls">
        <button 
          class="analyze-btn" 
          @click="startAnalysis"
          :disabled="isAnalyzing || isSearching"
        >
          {{ isAnalyzing ? 'Analyzing...' : '🔍 Analyze' }}
        </button>
        <select v-model="analysisMode" class="mode-select" @change="($event.target as HTMLSelectElement)?.blur()">
          <option value="full">Full Analysis</option>
          <option value="summary">Summary Only</option>
          <option value="trends">Trends Only</option>
          <option value="high_value">High-Value Papers</option>
          <option value="recommend">Recommendations</option>
          <option value="semantic_search">Semantic Search</option>
        </select>
        <select v-model="analysisLanguage" class="language-select" @change="($event.target as HTMLSelectElement)?.blur()">
          <option value="en">English</option>
          <option value="zh">中文</option>
        </select>
        <div class="max-papers-control">
          <label>Papers:</label>
          <input 
            type="range" 
            v-model.number="maxPapers"
            :min="sliderMin"
            :max="sliderMax"
            class="max-papers-slider"
          />
          <span class="max-papers-value">{{ maxPapers }}</span>
        </div>
      </div>

      <div v-if="analysisMode === 'semantic_search'" class="search-section">
        <label class="search-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          Search Query
        </label>
        <div class="search-input-wrapper">
          <input 
            type="text" 
            v-model="searchQuery"
            class="search-input"
            :class="{ 'input-error': searchQueryError }"
            placeholder="e.g., transformers for image classification"
            @keydown.enter.prevent="startAnalysis"
            @input="searchQueryError = ''"
          />
          <span v-if="searchQueryError" class="search-error">{{ searchQueryError }}</span>
          <span v-else class="search-hint">Enter natural language query for semantic search</span>
        </div>
      </div>

      <div v-else class="interests-section">
        <label class="interests-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          Research Interests (for recommendations)
        </label>
        <div class="interests-input-wrapper">
          <input 
            type="text" 
            v-model="interestsInput"
            class="interests-input"
            :class="{ 'input-error': interestsError }"
            placeholder="e.g., Machine Learning, NLP, Computer Vision"
            @keydown.enter.prevent="startAnalysis"
            @input="interestsError = ''"
          />
          <span v-if="interestsError" class="interests-error">{{ interestsError }}</span>
          <span v-else class="interests-hint">Comma-separated keywords</span>
        </div>
        <div v-if="parsedInterests.length > 0" class="interests-tags">
          <span v-for="interest in parsedInterests" :key="interest" class="interest-tag">
            {{ interest }}
          </span>
        </div>
      </div>

      <div v-if="isAnalyzing" class="progress-section">
        <div class="progress-text">{{ currentProgress }}</div>
        <div v-if="analysisProgress" class="progress-detail">
          <span class="progress-count">{{ analysisProgress.current }} / {{ analysisProgress.total }}</span>
          <span class="progress-title">{{ analysisProgress.title }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: analysisProgress ? `${(analysisProgress.current / analysisProgress.total) * 100}%` : '0%' }"></div>
        </div>
      </div>

      <div v-if="isSearching" class="progress-section">
        <div class="progress-text">
          <svg class="search-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          Searching for semantically similar papers...
        </div>
        <div class="progress-bar">
          <div class="progress-fill progress-fill-indeterminate"></div>
        </div>
      </div>

      <div v-if="error && !isAnalyzing" class="error-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>{{ error }}</span>
        <button @click="startAnalysis">Retry</button>
      </div>

      <template v-if="analysisMode === 'semantic_search' && searchResults.length > 0 && !isAnalyzing">
        <div class="search-results">
          <div class="results-header">
            <span>Found {{ totalResults }} papers</span>
          </div>
          <div class="results-grid">
            <PaperCard 
              v-for="(paper, index) in searchResults" 
              :key="paper.id"
              :paper="convertToPaper(paper)"
              :index="index + 1"
            />
          </div>
        </div>
      </template>

      <template v-else-if="analysisResult && hasAnyResult && !isSearching">
        <div class="results-tabs">
          <div class="tabs-header">
            <button 
              v-if="hasSummary"
              class="tab-btn"
              :class="{ active: activeTab === 'summary' }"
              @click="activeTab = 'summary'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 6h16M4 12h16M4 18h7"/>
              </svg>
              Summary
            </button>
            <button 
              v-if="hasTrends"
              class="tab-btn"
              :class="{ active: activeTab === 'trends' }"
              @click="activeTab = 'trends'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 6l-9.5 9.5-5-5L1 18"/>
                <path d="M17 6h6v6"/>
              </svg>
              Trends
            </button>
            <button 
              v-if="hasHighValue"
              class="tab-btn"
              :class="{ active: activeTab === 'high_value' }"
              @click="activeTab = 'high_value'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              High Value
              <span v-if="highValueCount > 0" class="tab-badge">{{ highValueCount }}</span>
            </button>
            <button 
              v-if="hasRecommendations"
              class="tab-btn"
              :class="{ active: activeTab === 'recommendations' }"
              @click="activeTab = 'recommendations'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              Recommendations
              <span v-if="recommendCount > 0" class="tab-badge">{{ recommendCount }}</span>
            </button>
          </div>

          <div class="tabs-content">
            <SummarySection 
              v-if="activeTab === 'summary' && analysisResult.summary" 
              :summary="analysisResult.summary"
              :themes="analysisResult.main_themes"
            />
            
            <TrendsSection 
              v-if="activeTab === 'trends' && analysisResult.trends?.length" 
              :trends="analysisResult.trends" 
            />
            
            <HighValueSection 
              v-if="activeTab === 'high_value' && (analysisResult.high_value_papers?.length || streamingHighValueResults.length > 0)" 
              :papers="analysisResult.high_value_papers || []"
              :streaming-papers="streamingHighValueResults"
              @view-paper="viewPaper"
            />
            
            <RecommendationsSection 
              v-if="activeTab === 'recommendations' && (analysisResult.recommendations?.length || streamingRecommendResults.length > 0)" 
              :papers="analysisResult.recommendations || []"
              :streaming-papers="streamingRecommendResults"
              @view-paper="viewPaper"
            />
          </div>
        </div>
      </template>

      <div v-if="analysisMode === 'semantic_search' && !isSearching && !searchError && searchResults.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <p>Enter a search query and click "Analyze" to find semantically similar papers</p>
      </div>

      <div v-else-if="analysisMode !== 'semantic_search' && !isAnalyzing && !error && !hasAnyResult" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
        <p>Click "Analyze" to start AI-powered daily paper analysis</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDailyAnalysis } from '@/composables/useDailyAnalysis'
import { useSemanticSearch } from '@/composables/useSemanticSearch'
import type { AnalysisMode, AnalysisLanguage, SemanticSearchPaper } from '@/types/dailyAnalysis'
import SummarySection from '@/components/daily-analysis/SummarySection.vue'
import TrendsSection from '@/components/daily-analysis/TrendsSection.vue'
import HighValueSection from '@/components/daily-analysis/HighValueSection.vue'
import RecommendationsSection from '@/components/daily-analysis/RecommendationsSection.vue'
import PaperCard from '@/components/PaperCard.vue'

const props = defineProps<{
  date: string
  userInterests?: string[]
}>()

const router = useRouter()

const {
  isAnalyzing,
  currentProgress,
  analysisProgress,
  analysisResult,
  error,
  startStreamAnalysis,
  streamingHighValueResults,
  streamingRecommendResults,
  totalPapers,
  fetchPaperCount,
} = useDailyAnalysis()

const {
  isSearching,
  searchError,
  searchResults,
  totalResults,
  searchPapers,
} = useSemanticSearch()

const analysisMode = ref<AnalysisMode>('full')
const analysisLanguage = ref<AnalysisLanguage>('en')
const interestsInput = ref('')
const interestsError = ref('')
const maxPapers = ref(50)
const activeTab = ref<'summary' | 'trends' | 'high_value' | 'recommendations'>('summary')

const sliderMin = 10
const sliderMax = computed(() => Math.max(sliderMin, totalPapers.value || 100))

const parsedInterests = computed(() => {
  if (!interestsInput.value.trim()) return []
  return interestsInput.value
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)
})

const hasSummary = computed(() => !!analysisResult.value?.summary)
const hasTrends = computed(() => !!analysisResult.value?.trends?.length)
const hasHighValue = computed(() => 
  !!(analysisResult.value?.high_value_papers?.length || streamingHighValueResults.value.length > 0)
)
const hasRecommendations = computed(() => 
  !!(analysisResult.value?.recommendations?.length || streamingRecommendResults.value.length > 0)
)

const highValueCount = computed(() => 
  analysisResult.value?.high_value_papers?.length || streamingHighValueResults.value.length || 0
)
const recommendCount = computed(() => 
  analysisResult.value?.recommendations?.length || streamingRecommendResults.value.length || 0
)

const hasAnyResult = computed(() => {
  if (!analysisResult.value) return false
  return hasSummary.value || hasTrends.value || hasHighValue.value || hasRecommendations.value
})

const searchQuery = ref('')
const searchQueryError = ref('')

const convertToPaper = (paper: SemanticSearchPaper) => {
  return {
    id: paper.id,
    title: paper.title,
    abstract: paper.abstract,
    authors: paper.authors || [],
    primaryCategory: paper.primary_category,
    categories: paper.categories || [],
    pdfUrl: paper.pdf_url,
    absUrl: paper.abs_url,
    published: paper.published || new Date().toISOString(),
    updated: paper.published || new Date().toISOString(),
  }
}

watch([hasSummary, hasTrends, hasHighValue, hasRecommendations], ([summary, trends, highValue, recs]) => {
  const tabOrder: Array<'summary' | 'trends' | 'high_value' | 'recommendations'> = ['summary', 'trends', 'high_value', 'recommendations']
  const tabAvailability = [summary, trends, highValue, recs]
  
  const currentTabIndex = tabOrder.indexOf(activeTab.value)
  if (currentTabIndex !== -1 && !tabAvailability[currentTabIndex]) {
    const firstAvailableIndex = tabAvailability.findIndex(Boolean)
    if (firstAvailableIndex !== -1) {
      activeTab.value = tabOrder[firstAvailableIndex]
    }
  }
}, { immediate: true })

async function startAnalysis() {
  interestsError.value = ''
  searchQueryError.value = ''

  if (analysisMode.value === 'semantic_search') {
    if (!searchQuery.value.trim()) {
      searchQueryError.value = 'Please enter a search query'
      return
    }
    await searchPapers(searchQuery.value, {
      topK: maxPapers.value,
      dateFrom: props.date,
      dateTo: props.date,
    })
    return
  }

  const interests = parsedInterests.value.length > 0 ? parsedInterests.value : props.userInterests
  
  if (analysisMode.value === 'recommend') {
    if (!interests || interests.length === 0) {
      interestsError.value = 'Please enter your research interests for recommendations'
      return
    }
  }

  await startStreamAnalysis(props.date, analysisMode.value, interests, analysisLanguage.value, maxPapers.value)
}

function viewPaper(paperId: string) {
  router.push({ name: 'PaperDetail', params: { id: paperId } })
}

watch(() => props.date, (newDate) => {
  fetchPaperCount(newDate)
})

onMounted(() => {
  if (props.userInterests?.length) {
    interestsInput.value = props.userInterests.join(', ')
  }
  fetchPaperCount(props.date)
})
</script>

<style scoped>
.daily-analysis-panel {
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.panel-content {
  padding: 24px;
}

.analysis-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.analyze-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mode-select {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  min-width: 160px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.language-select {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  min-width: 100px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.max-papers-control {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.max-papers-control label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.max-papers-slider {
  width: 80px;
  height: 4px;
  appearance: none;
  background: var(--border-color);
  border-radius: 2px;
  cursor: pointer;
}

.max-papers-slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

.max-papers-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.max-papers-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.max-papers-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-color, #8b5cf6);
  min-width: 28px;
  text-align: center;
}

.interests-section {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.interests-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.interests-label svg {
  width: 18px;
  height: 18px;
  color: var(--accent-color, #8b5cf6);
}

.interests-input-wrapper {
  position: relative;
}

.interests-input {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.2s;
}

.interests-input:focus {
  outline: none;
  border-color: var(--accent-color, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.interests-input::placeholder {
  color: var(--text-muted);
}

.interests-hint {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.interests-error {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--error-color, #ef4444);
}

.interests-input.input-error {
  border-color: var(--error-color, #ef4444);
}

.interests-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.interest-tag {
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15));
  color: var(--accent-color, #8b5cf6);
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.progress-section {
  padding: 20px 10px;
  text-align: center;
}

.progress-text {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  margin-bottom: 16px;
  font-size: 0.95rem;
}

.progress-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.progress-count {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-color, #8b5cf6);
}

.progress-title {
  font-size: 0.85rem;
  color: var(--text-secondary);
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
  max-width: 300px;
  margin: 0 auto;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
  transition: width 0.3s ease;
}

.progress-fill-indeterminate {
  width: 30%;
  animation: indeterminate 1.5s ease-in-out infinite;
}

@keyframes indeterminate {
  0% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(250%);
  }
  100% {
    transform: translateX(-100%);
  }
}

.search-spinner {
  width: 20px;
  height: 20px;
  animation: spin 1.5s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px 20px;
  color: var(--error-color, #ef4444);
}

.error-state svg {
  width: 48px;
  height: 48px;
  opacity: 0.7;
}

.error-state button {
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-primary);
  transition: all 0.2s;
}

.error-state button:hover {
  background: var(--bg-tertiary);
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1rem;
}

.search-section {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.search-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.search-label svg {
  width: 18px;
  height: 18px;
  color: var(--accent-color, #8b5cf6);
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-hint {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.search-error {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--error-color, #ef4444);
}

.search-input.input-error {
  border-color: var(--error-color, #ef4444);
}

.search-results {
  margin-top: 20px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.results-header span {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.results-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.results-tabs {
  margin-top: 20px;
}

.tabs-header {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--bg-secondary);
  border-radius: 10px;
  margin-bottom: 16px;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  max-width: 220px;
}

.tab-btn svg {
  width: 16px;
  height: 16px;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(139, 92, 246, 0.08);
}

.tab-btn.active {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.tab-badge {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
}

.tab-btn:not(.active) .tab-badge {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.tabs-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .panel-content {
    padding: 16px;
  }

  .analysis-controls {
    flex-direction: column;
  }

  .mode-select,
  .language-select {
    width: 100%;
    min-width: unset;
  }

  .results-grid {
    gap: 12px;
  }

  .tabs-header {
    flex-wrap: wrap;
  }

  .tab-btn {
    flex: 1 1 calc(50% - 2px);
    font-size: 0.8rem;
    padding: 8px 12px;
  }
}
</style>
