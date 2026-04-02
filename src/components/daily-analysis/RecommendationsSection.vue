<template>
  <div class="recommendations-section">
    <div v-if="streamingPapers && streamingPapers.length > 0" class="streaming-results">
      <div class="streaming-header">
        <span class="streaming-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          Recommend Analysis Items ({{ streamingPapers.length }})
        </span>
      </div>
      <div class="streaming-cards">
        <div 
          v-for="(paper, index) in streamingPapers" 
          :key="paper.paper_id + index" 
          class="streaming-card"
        >
          <div class="card-header">
            <span class="card-index">#{{ index + 1 }}</span>
            <span class="card-title">{{ paper.title }}</span>
            <span class="card-confidence" :class="getRelevanceClass(paper.relevance_score)">
              {{ (paper.relevance_score).toFixed(0) }}%
            </span>
          </div>
          <div class="card-type">
            <span class="paper-id">{{ paper.paper_id }}</span>
            <span class="type-label">Interests:</span>
            <span class="type-value">{{ paper.matched_interests }}</span>
          </div>
          <div class="card-description">{{ paper.reason }}</div>
          <div class="actions">
            <button class="action-btn" @click="$emit('viewPaper', paper.paper_id)">View Paper</button>
          </div>
        </div>
      </div>
    </div>

    <h4 v-if="papers.length > 0" class="section-title">🎯 Final Recommended</h4>
    <div class="papers-list">
      <div v-for="paper in papers" :key="paper.paper_id" class="paper-card">
        <div class="paper-header">
          <span class="paper-title">{{ paper.title }}</span>
          <span class="match-score">Match: {{ paper.relevance_score }}%</span>
        </div>
        <div class="paper-meta">
          <span class="paper-id">{{ paper.paper_id }}</span>
          <div class="matched-interests">
            <span v-for="interest in paper.matched_interests" :key="interest" class="interest-tag">
              {{ interest }}
            </span>
          </div>
        </div>
        <p class="reason">{{ paper.reason }}</p>
        <div class="actions">
          <button class="action-btn" @click="$emit('viewPaper', paper.paper_id)">View Paper</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RecommendedPaper } from '@/types/dailyAnalysis'

interface StreamingRecommendPaper {
  paper_id: string
  title: string
  relevance_score: number
  matched_interests: string[]
  reason: string
}

defineProps<{
  papers: RecommendedPaper[]
  streamingPapers?: StreamingRecommendPaper[]
}>()

defineEmits<{
  viewPaper: [paperId: string]
}>()

function getRelevanceClass(score: number): string {
  if (score >= 90) return 'high'
  if (score >= 80) return 'medium'
  return 'low'
}
</script>

<style scoped>
.recommendations-section {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-card {
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.paper-title {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.match-score {
  font-size: 0.8rem;
  color: var(--success-color, #10b981);
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.paper-id {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.matched-interests {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.interest-tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: var(--accent-color-light, rgba(59, 130, 246, 0.1));
  color: var(--accent-color, #3b82f6);
  border-radius: 10px;
}

.reason {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  font-size: 0.8rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-tertiary, var(--bg-secondary));
}

.streaming-results {
  margin-bottom: 16px;
  background: var(--bg-primary);
  border-radius: 10px;
}

.streaming-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.streaming-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.title-icon {
  width: 18px;
  height: 18px;
  color: #10b981;
}

.streaming-cards {
  max-height: 380px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  scroll-behavior: smooth;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin: 12px;
}

.streaming-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.card-index {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
}

.card-confidence {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.card-confidence.high {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.card-confidence.medium {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.card-confidence.low {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  color: white;
}

.card-title {
  flex: 1;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-type {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.type-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.type-value {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.card-description {
  font-size: 0.8rem;
  margin-bottom: 10px;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
