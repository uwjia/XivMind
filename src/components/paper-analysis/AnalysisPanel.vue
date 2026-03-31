<template>
  <div class="analysis-panel">
    <div class="analysis-header">
      <h3 class="analysis-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="analysis-icon">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        AI Paper Analysis
      </h3>
      <div class="analysis-controls">
        <select v-model="selectedLanguage" class="language-select">
          <option value="en">English</option>
          <option value="zh">中文</option>
        </select>
        <select v-model="selectedType" class="type-select">
          <option value="full">Full Analysis</option>
          <option value="summary">Summary Only</option>
          <option value="keypoints">Key Points Only</option>
          <option value="methodology">Methodology Only</option>
          <option value="questions">Questions & Conclusions</option>
        </select>
        <button 
          class="analyze-btn" 
          @click="startAnalysis" 
          :disabled="isAnalyzing"
          :class="{ analyzing: isAnalyzing }"
        >
          <svg v-if="isAnalyzing" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="62.83" stroke-dashoffset="15.7">
              <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </circle>
          </svg>
          <span>{{ isAnalyzing ? 'Analyzing...' : 'Analyze' }}</span>
        </button>
      </div>
    </div>
    
    <div v-if="currentProgress && isAnalyzing" class="progress-indicator">
      <div class="progress-text">{{ currentProgress }}</div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10" stroke-width="2"/>
        <path d="M12 8v4m0 4h.01" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>{{ error }}</span>
    </div>
    
    <div v-if="result" class="analysis-result">
      <div v-if="result.summary" class="result-section">
        <h4 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Summary
        </h4>
        <p class="section-content">{{ result.summary }}</p>
      </div>
      
      <div v-if="result.key_points && result.key_points.length > 0" class="result-section">
        <h4 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Key Points
        </h4>
        <ul class="key-points-list">
          <li v-for="(point, index) in result.key_points" :key="index" class="key-point-item" :class="point.importance">
            <div class="point-header">
              <span class="point-importance">{{ point.importance }}</span>
              <span class="point-title">{{ point.title }}</span>
            </div>
            <p class="point-description">{{ point.description }}</p>
          </li>
        </ul>
      </div>
      
      <div v-if="result.methodology" class="result-section">
        <h4 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Methodology
        </h4>
        <p class="section-content">{{ result.methodology }}</p>
      </div>
      
      <div v-if="result.questions_and_conclusions && result.questions_and_conclusions.length > 0" class="result-section">
        <h4 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Questions & Conclusions
        </h4>
        <div class="qa-list">
          <div v-for="(qa, index) in result.questions_and_conclusions" :key="index" class="qa-item">
            <div class="qa-question">
              <span class="qa-label">Q:</span>
              {{ qa.question }}
            </div>
            <div class="qa-conclusion">
              <span class="qa-label">A:</span>
              {{ qa.conclusion }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="result-meta">
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="meta-icon">
            <path d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ result.service_used }} / {{ result.model_used }}
        </span>
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="meta-icon">
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ formatDate(result.analyzed_at) }}
        </span>
      </div>
    </div>
    
    <div v-else-if="!isAnalyzing && !error" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
      </svg>
      <p>Click "Analyze" to start AI analysis of this paper</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { usePaperAnalysis, type AnalysisType } from '@/composables/usePaperAnalysis'
import { formatDate } from '@/utils/format'

const props = defineProps<{
  paperId: string
}>()

const {
  isAnalyzing,
  currentProgress,
  progressPercentage,
  analysisResult,
  error,
  startStreamAnalysis,
  clearResult,
  getCachedAnalysis,
} = usePaperAnalysis()

const selectedLanguage = ref<string>('en')
const selectedType = ref<AnalysisType>('full')

const progressWidth = computed(() => `${progressPercentage.value}%`)

const result = computed(() => analysisResult.value)

const startAnalysis = () => {
  startStreamAnalysis(props.paperId, selectedType.value, selectedLanguage.value)
}

watch(() => props.paperId, () => {
  clearResult()
  getCachedAnalysis(props.paperId, selectedType.value, selectedLanguage.value)
}, { immediate: true })
</script>

<style scoped>
.analysis-panel {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  margin-top: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.analysis-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-color);
}

.analysis-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.language-select,
.type-select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
}

.analyze-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: var(--accent-color);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.analyze-btn.analyzing {
  background: var(--icon-downloads);
}

.spinner {
  width: 16px;
  height: 16px;
}

.progress-indicator {
  margin-bottom: 16px;
}

.progress-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.progress-bar {
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-color);
  transition: width 0.3s ease;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: color-mix(in srgb, var(--icon-error) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--icon-error) 30%, transparent);
  border-radius: 8px;
  color: var(--icon-error);
  margin-bottom: 16px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.analysis-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-section {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.section-title svg {
  width: 20px;
  height: 20px;
  color: var(--accent-color);
}

.section-content {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.key-points-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.key-point-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
  border-left: 3px solid var(--border-color);
}

.key-point-item.high {
  border-left-color: var(--icon-success);
}

.key-point-item.medium {
  border-left-color: var(--icon-downloads);
}

.key-point-item.low {
  border-left-color: var(--icon-comments);
}

.point-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.point-importance {
  font-size: 0.7rem;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--border-color);
  color: var(--text-secondary);
}

.key-point-item.high .point-importance {
  background: color-mix(in srgb, var(--icon-success) 20%, transparent);
  color: var(--icon-success);
}

.key-point-item.medium .point-importance {
  background: color-mix(in srgb, var(--icon-downloads) 20%, transparent);
  color: var(--icon-downloads);
}

.key-point-item.low .point-importance {
  background: color-mix(in srgb, var(--icon-comments) 20%, transparent);
  color: var(--icon-comments);
}

.point-title {
  font-weight: 500;
  color: var(--text-primary);
}

.point-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.qa-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
}

.qa-question,
.qa-conclusion {
  margin-bottom: 8px;
}

.qa-conclusion {
  margin-bottom: 0;
}

.qa-label {
  font-weight: 600;
  margin-right: 8px;
}

.qa-question .qa-label {
  color: var(--icon-downloads);
}

.qa-conclusion .qa-label {
  color: var(--icon-success);
}

.result-meta {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-icon {
  width: 14px;
  height: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  text-align: center;
}
</style>
