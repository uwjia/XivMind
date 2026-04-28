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
      <div class="header-controls">
        <select v-model="top_k" class="limit-select" title="Number of papers to display" @change="($event.target as HTMLSelectElement)?.blur()">
          <option :value="5">5</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
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
    
    <div v-else-if="papers.length > 0" class="related-papers" :class="{ scrollable: top_k > 5 }">
      <div 
        v-for="paper in papers" 
        :key="paper.id" 
        class="paper-item"
      >
        <span 
          class="paper-id" 
          @click="goToPaper(paper.id)"
          @mouseenter="showTooltip(paper, $event)"
          @mouseleave="hideTooltip"
        >{{ paper.id }}</span>
        <span 
          class="paper-title"
          @click="goToPaper(paper.id)"
          @mouseenter="showTooltip(paper, $event)"
          @mouseleave="hideTooltip"
        >{{ paper.title }}</span>
        <span 
          class="paper-score"
          :class="{ pinned: pinnedPaper?.id === paper.id }"
          @click.stop="togglePinnedTooltip(paper, $event)"
        >{{ (paper.similarity_score * 100).toFixed(1) }}%</span>
      </div>
    </div>
    
    <div v-else class="no-papers">
      <p>No similar papers found</p>
      <button @click="refresh" class="retry-btn">Search Again</button>
    </div>
    
    <Teleport to="body">
      <Transition name="tooltip">
        <div 
          v-if="tooltipVisible && tooltipPaper" 
          ref="_tooltipRef"
          class="paper-tooltip"
          :class="{ pinned: isTooltipPinned }"
          :style="tooltipStyle"
        >
          <button v-if="isTooltipPinned" class="tooltip-close" @click="closePinnedTooltip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="tooltip-header">
            <span class="tooltip-title">{{ tooltipPaper.title }}</span>
            <span class="tooltip-score">{{ (tooltipPaper.similarity_score * 100).toFixed(1) }}%</span>
          </div>
          <div class="tooltip-abstract">
            <p class="abstract-text">{{ isAbstractExpanded && isTooltipPinned ? tooltipPaper.abstract : truncateAbstract(tooltipPaper.abstract) }}</p>
            <button 
              v-if="isTooltipPinned && isAbstractLong(tooltipPaper.abstract)" 
              class="abstract-toggle"
              @click.stop="toggleAbstractExpand"
            >
              {{ isAbstractExpanded ? 'Show less' : 'Show more' }}
            </button>
          </div>
          <div class="tooltip-section">
            <span class="tooltip-label">Authors:</span>
            <span class="tooltip-value">{{ tooltipPaper.authors.slice(0, 5).join(', ') }}{{ tooltipPaper.authors.length > 5 ? ' et al.' : '' }}</span>
          </div>
          <div class="tooltip-section">
            <span class="tooltip-label">Categories:</span>
            <span class="tooltip-value">{{ tooltipPaper.categories.join(', ') }}</span>
          </div>
          <div class="tooltip-section">
            <span class="tooltip-label">Published:</span>
            <span class="tooltip-value">{{ formatDate(tooltipPaper.published) }}</span>
          </div>
          <div v-if="tooltipPaper.updated && tooltipPaper.updated !== tooltipPaper.published" class="tooltip-section">
            <span class="tooltip-label">Updated:</span>
            <span class="tooltip-value">{{ formatDate(tooltipPaper.updated) }}</span>
          </div>
          <div v-if="tooltipPaper.doi" class="tooltip-section">
            <span class="tooltip-label">DOI:</span>
            <span class="tooltip-value tooltip-doi">{{ tooltipPaper.doi }}</span>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRelatedPapers } from '@/composables/useRelatedPapers'
import { useRelateTooltip } from '@/composables/useRelateTooltip'

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
  top_k,
  fetchRelatedPapers,
} = useRelatedPapers()

const {
  tooltipVisible,
  tooltipPaper,
  tooltipStyle,
  isTooltipPinned,
  pinnedPaper,
  isAbstractExpanded,
  tooltipRef: _tooltipRef,
  showTooltip,
  hideTooltip,
  togglePinnedTooltip,
  closePinnedTooltip,
  truncateAbstract,
  isAbstractLong,
  toggleAbstractExpand,
  formatDate,
} = useRelateTooltip()

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

watch(top_k, () => {
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

.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.limit-select {
  padding: 6px 28px 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: var(--transition);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.limit-select:hover {
  border-color: var(--accent-color);
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
  min-height: 288px;
}

.related-papers.scrollable {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.related-papers.scrollable::-webkit-scrollbar {
  width: 6px;
}

.related-papers.scrollable::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 3px;
}

.related-papers.scrollable::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.related-papers.scrollable::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
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
  cursor: pointer;
  transition: var(--transition);
}

.paper-id:hover {
  color: var(--accent-color);
}

.paper-title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  flex: 1;
  cursor: pointer;
  transition: var(--transition);
}

.paper-title:hover {
  color: var(--accent-color);
}

.paper-score {
  font-size: 0.75rem;
  color: var(--accent-color);
  font-weight: 600;
  background: color-mix(in srgb, var(--accent-color) 10%, transparent);
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition);
}

.paper-score:hover {
  background: color-mix(in srgb, var(--accent-color) 20%, transparent);
}

.paper-score.pinned {
  background: var(--accent-color);
  color: white;
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

.paper-tooltip {
  position: fixed;
  z-index: 9999;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  pointer-events: none;
  overflow-y: auto;
}

.paper-tooltip::-webkit-scrollbar {
  width: 6px;
}

.paper-tooltip::-webkit-scrollbar-track {
  background: transparent;
}

.paper-tooltip::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.paper-tooltip::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

.paper-tooltip.pinned {
  pointer-events: auto;
}

.tooltip-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: var(--bg-tertiary);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.tooltip-close:hover {
  background: var(--danger-color);
  color: white;
}

.tooltip-close svg {
  width: 14px;
  height: 14px;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.tooltip-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  flex: 1;
}

.tooltip-score {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent-color);
  background: color-mix(in srgb, var(--accent-color) 15%, transparent);
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.tooltip-section {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.85rem;
}

.tooltip-label {
  color: var(--text-muted);
  min-width: 80px;
  flex-shrink: 0;
}

.tooltip-value {
  color: var(--text-primary);
  word-break: break-word;
}

.tooltip-doi {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.tooltip-abstract {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.abstract-text {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.6;
  margin: 0;
}

.abstract-toggle {
  margin-top: 8px;
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: var(--accent-color);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.abstract-toggle:hover {
  text-decoration: underline;
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
