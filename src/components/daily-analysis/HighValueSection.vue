<template>
  <div class="high-value-section">
    <div v-if="streamingPapers && streamingPapers.length > 0" class="streaming-results">
      <div class="streaming-header">
        <span class="streaming-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          High Value Analysis Items ({{ streamingPapers.length }})
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
            <span class="card-confidence" :class="getConfidenceClass(paper.confidence)">
              {{ (paper.confidence * 100).toFixed(0) }}%
            </span>
          </div>
          <div class="card-type">
            <span class="type-value">{{ paper.paper_id }}</span>
            <span class="type-label">Type:</span>
            <span class="type-value">{{ formatInnovationType(paper.innovation_type) }}</span>
          </div>
          <div class="card-description">{{ paper.innovation_description }}</div>
          <div class="actions">
            <button class="action-btn" @click="$emit('viewPaper', paper.paper_id)">View Paper</button>
          </div>
        </div>
      </div>
    </div>

    <h4 v-if="papers.length > 0" class="section-title">⭐ High-Value Papers</h4>
    <div class="papers-list">
      <div v-for="paper in papers" :key="paper.paper_id" class="paper-item">
        <div class="paper-header">
          <span class="paper-title">{{ paper.title }}</span>
          <span class="confidence" :style="{ opacity: paper.confidence }">
            {{ Math.round(paper.confidence * 100) }}%
          </span>
        </div>
        <div class="paper-meta">
          <span class="paper-id">{{ paper.paper_id }}</span>
          <span class="innovation-type">{{ formatInnovationType(paper.innovation_type) }}</span>
        </div>
        <p class="innovation-description">{{ paper.innovation_description }}</p>
        <div class="actions">
          <button class="action-btn" @click="$emit('viewPaper', paper.paper_id)">View Paper</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HighValuePaper } from '@/types/dailyAnalysis'

interface StreamingHighValuePaper {
  paper_id: string
  title: string
  innovation_type: string
  innovation_description: string
  confidence: number
}

defineProps<{
  papers: HighValuePaper[]
  streamingPapers?: StreamingHighValuePaper[]
}>()

defineEmits<{
  viewPaper: [paperId: string]
}>()

function formatInnovationType(type: string): string {
  const types: Record<string, string> = {
    novel_method: 'Novel Method',
    significant_improvement: 'Significant Improvement',
    new_problem: 'New Problem',
    cross_domain: 'Cross-Domain',
  }
  return types[type] || type
}

function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.9) return 'high'
  if (confidence >= 0.8) return 'medium'
  return 'low'
}
</script>

<style scoped>
.high-value-section {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
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

.paper-item {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}

.paper-title {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.confidence {
  font-size: 0.75rem;
  color: var(--success-color, #10b981);
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.paper-id {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.innovation-type {
  font-size: 0.75rem;
  color: var(--accent-color, #3b82f6);
  margin-bottom: 6px;
}

.innovation-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
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
  color: #f59e0b;
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
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
