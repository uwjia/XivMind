<template>
  <div class="relate-panel">
    <div class="related-header">
      <h3 class="related-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="related-icon">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Related Papers
      </h3>
      <button 
        v-if="!loading && !error" 
        @click="refresh" 
        class="refresh-btn"
        title="Find similar papers"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" :class="{ 'spinning': loading }">
          <path d="M23 4v6h-6"/>
          <path d="M1 20v-6h6"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
    </div>
    
    <div v-if="loading" class="related-loading">
      <div class="spinner"></div>
      <p>Finding similar papers...</p>
    </div>
    
    <div v-else-if="error" class="related-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="refresh" class="retry-btn">Retry</button>
    </div>
    
    <div v-else-if="papers.length > 0" class="related-papers">
      <div 
        v-for="paper in papers" 
        :key="paper.id" 
        class="paper-item" 
        @click="goToPaper(paper.id)"
      >
        <span class="paper-id">{{ paper.id }}</span>
        <span class="paper-title">{{ paper.title }}</span>
        <span class="paper-score">{{ (paper.similarity_score * 100).toFixed(1) }}%</span>
      </div>
    </div>
    
    <div v-else class="no-papers">
      <p>No similar papers found</p>
      <button @click="refresh" class="retry-btn">Search Again</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRelatedPapers } from '@/composables/useRelatedPapers'

const props = defineProps<{
  paperId: string
  paperTitle?: string
  paperAbstract?: string
}>()

const router = useRouter()

const {
  papers,
  loading,
  error,
  fetchRelatedPapers,
} = useRelatedPapers()

const refresh = () => {
  if (props.paperId && props.paperTitle && props.paperAbstract) {
    fetchRelatedPapers(props.paperId, props.paperTitle, props.paperAbstract)
  }
}

const goToPaper = (id: string) => {
  router.push({ name: 'PaperDetail', params: { id } })
}

onMounted(() => {
  refresh()
})

watch(() => props.paperId, () => {
  refresh()
})
</script>

<style scoped>
.relate-panel {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  margin-top: 20px;
}

.related-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.related-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.related-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-color);
}

.refresh-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.related-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  color: var(--text-secondary);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.related-loading p {
  margin: 12px 0 0 0;
  font-size: 0.9rem;
}

.related-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  color: var(--text-secondary);
  text-align: center;
}

.related-error svg {
  width: 32px;
  height: 32px;
  color: #ef4444;
  margin-bottom: 8px;
}

.related-error p {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
}

.retry-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: var(--transition);
}

.retry-btn:hover {
  opacity: 0.9;
}

.related-papers {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.paper-item:hover {
  background: var(--bg-tertiary);
  transform: translateX(4px);
}

.paper-id {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 80px;
}

.paper-title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  flex: 1;
}

.paper-score {
  font-size: 0.75rem;
  color: var(--accent-color);
  font-weight: 600;
  background: color-mix(in srgb, var(--accent-color) 10%, transparent);
  padding: 2px 8px;
  border-radius: 4px;
}

.no-papers {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  color: var(--text-secondary);
  text-align: center;
}

.no-papers p {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
}
</style>
