<template>
  <div class="home">

    <div class="content">
      <div class="content-header">
        <div>
          <p v-if="filterDescription" class="section-description">{{ filterDescription }}</p>
        </div>
        <div class="header-actions">
          <button v-if="!isGraphView" class="icon-btn date-btn" @click="toggleDatePicker" title="Select date">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </button>
          <button v-if="!isGraphView" class="icon-btn category-btn" @click="toggleCategoryPicker" title="Select category">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          </button>
          <button v-if="!isGraphView" class="icon-btn filter-btn" @click="toggleFilterDrawer" :title="isFilterDrawerOpen ? 'Hide categories' : 'Show categories'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" fill="currentColor" fill-opacity="0.2"/>
            </svg>
          </button>
          <button v-if="!isGraphView" class="icon-btn toggle-btn" @click="configStore.setUseSimpleCard(!configStore.useSimpleCard)" :title="configStore.useSimpleCard ? 'Switch to detailed view' : 'Switch to simple view'">
            <svg v-if="configStore.useSimpleCard" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="3" y1="15" x2="21" y2="15"/>
              <line x1="9" y1="9" x2="9" y2="15"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="5" rx="1"/>
              <rect x="3" y="10" width="18" height="5" rx="1"/>
              <rect x="3" y="17" width="18" height="4" rx="1"/>
            </svg>
          </button>
          <button class="icon-btn view-toggle-btn" @click="toggleGraphView" :title="isGraphView ? 'Switch to list view' : 'Switch to graph view'">
            <svg v-if="isGraphView" viewBox="0 0 24 24" fill="none" stroke-width="2">
              <rect x="3" y="3" width="7" height="7" fill="var(--icon-graph-node-1)" stroke="var(--icon-graph-node-1)"/>
              <rect x="14" y="3" width="7" height="7" fill="var(--icon-graph-node-2)" stroke="var(--icon-graph-node-2)"/>
              <rect x="3" y="14" width="7" height="7" fill="var(--icon-graph-node-3)" stroke="var(--icon-graph-node-3)"/>
              <rect x="14" y="14" width="7" height="7" fill="var(--icon-graph-node-4)" stroke="var(--icon-graph-node-4)"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="4" fill="var(--icon-graph-node-1)"/>
              <circle cx="5" cy="5" r="3" fill="var(--icon-graph-node-2)"/>
              <circle cx="19" cy="5" r="3" fill="var(--icon-graph-node-3)"/>
              <circle cx="5" cy="19" r="3" fill="var(--icon-graph-node-4)"/>
              <circle cx="19" cy="19" r="3" fill="var(--icon-graph-node-5)"/>
              <line x1="7.5" y1="7.5" x2="9" y2="9" stroke="var(--icon-graph-line)" stroke-width="1.5"/>
              <line x1="15" y1="9" x2="16.5" y2="7.5" stroke="var(--icon-graph-line)" stroke-width="1.5"/>
              <line x1="7.5" y1="16.5" x2="9" y2="15" stroke="var(--icon-graph-line)" stroke-width="1.5"/>
              <line x1="15" y1="15" x2="16.5" y2="16.5" stroke="var(--icon-graph-line)" stroke-width="1.5"/>
            </svg>
          </button>
          <button v-if="!isGraphView" class="icon-btn analysis-btn" @click="goToDailyAnalysis" title="AI Daily Analysis">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </button>
          <button v-if="!isGraphView" class="icon-btn refresh-btn" @click="refreshPapers" :disabled="loading" title="Refresh papers">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="error" class="error-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="refreshPapers">Retry</button>
      </div>

      <div v-else-if="isGraphView" class="graph-view-container">
        <KnowledgeGraph
          :date="graphDate"
          @node-click="handleNodeClick"
          @graph-ready="handleGraphReady"
        />
        <GraphControls
          :config="graphConfig"
          :categories="graphCategories"
          @config-change="handleGraphConfigChange"
          @layout-change="handleLayoutChange"
          @reset="handleGraphReset"
        />
        <GraphStatistics :statistics="graphStatistics" />
      </div>

      <div v-else class="papers-grid">
        <PaperCard
          v-if="!configStore.useSimpleCard"
          v-for="(paper, index) in filteredPapers"
          :key="'detailed-' + paper.id"
          :paper="paper"
          :index="currentPage * configStore.maxResults + index + 1"
        />
        <PaperCardSimple
          v-else
          v-for="(paper, index) in filteredPapers"
          :key="'simple-' + paper.id"
          :paper="paper"
          :index="currentPage * configStore.maxResults + index + 1"
        />
      </div>

      <div v-if="!isGraphView && !loading && (filteredPapers.length > 0 || currentPage > 0)" class="pagination">
        <button class="pagination-btn" @click="goToFirstPage" :disabled="currentPage === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
          </svg>
          First
        </button>
        <button class="pagination-btn" @click="goToPreviousPage" :disabled="currentPage === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Previous
        </button>
        <div class="pagination-jump">
          <span class="pagination-info">Page {{ currentPage + 1 }}/{{ totalPages }}</span>
          <input 
            type="number" 
            v-model.number="jumpPageInput" 
            class="pagination-input" 
            placeholder="num"
            min="1"
            :max="totalPages"
            @input="handleJumpPageInput"
            @keyup.enter="handleGoToPage"
          />
          <button class="pagination-btn" @click="handleGoToPage">Go</button>
        </div>
        <button class="pagination-btn" @click="goToNextPage" :disabled="currentPage >= totalPages - 1">
          Next
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

      <div v-if="!error && !loading && filteredPapers.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9.172 16.172a4 4 0 0 1-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
        </svg>
        <p>No papers found matching your criteria</p>
      </div>
    </div>

    <DatePicker
      :is-open="isDatePickerOpen"
      :model-value="selectedDate as string | Date | null"
      @update:model-value="handleDateSelect"
      @update:is-open="closeDatePicker"
    />

    <CategoryPicker
      :is-open="isCategoryPickerOpen"
      :model-value="selectedCategory"
      @update:model-value="handleCategorySelect"
      @update:is-open="closeCategoryPicker"
    />

    <CategoryDrawer
      :is-open="isFilterDrawerOpen"
      :selected-category="localFilterCategory"
      :category-counts="categoryCounts"
      @close="closeFilterDrawer"
      @select="handleFilterCategorySelect"
    />

    <ScrollTopButton />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onActivated, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config-store'
import { useBookmarkStore } from '@/stores/bookmark-store'
import { useDownloadStore } from '@/stores/download-store'
import PaperCard from '@/components/PaperCard.vue'
import PaperCardSimple from '@/components/PaperCardSimple.vue'
import DatePicker from '@/components/DatePicker.vue'
import CategoryPicker from '@/components/CategoryPicker.vue'
import { KnowledgeGraph, GraphControls, GraphStatistics } from '@/components/graph'
import CategoryDrawer from '@/components/CategoryDrawer.vue'
import ScrollTopButton from '@/components/ScrollTopButton.vue'
import { usePaperFilter } from '@/composables/usePaperFilter'
import { useKnowledgeGraph } from '@/composables/useKnowledgeGraph'

const configStore = useConfigStore()
const bookmarkStore = useBookmarkStore()
const downloadStore = useDownloadStore()
const jumpPageInput = ref<number | null>(null)
const route = useRoute()
const router = useRouter()

const {
  currentPage,
  selectedCategory,
  selectedDate,
  loading,
  error,
  totalPapers,
  isDatePickerOpen,
  isCategoryPickerOpen,
  toggleDatePicker,
  toggleCategoryPicker,
  closeDatePicker,
  closeCategoryPicker,
  handleDateSelect,
  handleCategorySelect,
  loadPapers,
  goToFirstPage,
  goToPreviousPage,
  goToNextPage,
  goToPage,
  handleFilterCategorySelect,
  localFilterCategory,
  filteredPapers,
  filterDescription,
  categoryCounts,
  checkAndLoadPapers,
  toggleFilterDrawer,
  closeFilterDrawer,
  isFilterDrawerOpen,
} = usePaperFilter()

const {
  isGraphView,
  graphDate,
  graphConfig,
  graphStatistics,
  graphCategories,
  toggleGraphView,
  handleNodeClick,
  handleGraphReady,
  handleGraphConfigChange,
  handleLayoutChange,
  handleGraphReset
} = useKnowledgeGraph(selectedDate, selectedCategory)

const totalPages = computed(() => {
  if (totalPapers.value <= 0) return 1
  return Math.ceil(totalPapers.value / configStore.maxResults)
})

const handleJumpPageInput = () => {
  const value = jumpPageInput.value
  if (typeof value === 'number' && value > totalPages.value) {
    jumpPageInput.value = totalPages.value
  }
}

const handleGoToPage = () => {
  const targetPage = jumpPageInput.value
  if (targetPage && targetPage > 0 && targetPage <= totalPages.value) {
    goToPage(targetPage - 1)
    jumpPageInput.value = null
  }
}

const refreshPapers = async () => {
  console.log('Refreshing papers...')
  await loadPapers()
}

const handleRouteQuery = async () => {
  const dateQuery = route.query.date as string | undefined
  if (dateQuery) {
    console.log('Loading papers for date from query:', dateQuery)
    const date = new Date(dateQuery)
    if (!isNaN(date.getTime())) {
      handleDateSelect(date)
      router.replace({ query: {} })
      return true
    }
  }
  return false
}

function formatDateLocal(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function goToDailyAnalysis() {
  let dateStr: string
  
  if (!selectedDate.value) {
    dateStr = formatDateLocal(new Date())
  } else if (selectedDate.value instanceof Date) {
    dateStr = formatDateLocal(selectedDate.value)
  } else if (typeof selectedDate.value === 'string') {
    dateStr = selectedDate.value === 'all' ? formatDateLocal(new Date()) : selectedDate.value
  } else if (typeof selectedDate.value === 'object' && 'startDate' in selectedDate.value) {
    dateStr = selectedDate.value.startDate
  } else {
    dateStr = formatDateLocal(new Date())
  }
  
  router.push({ name: 'DailyAnalysis', params: { date: dateStr } })
}

watch(() => route.query.date, async (newDate) => {
  if (newDate) {
    console.log('Route query date changed:', newDate)
    const date = new Date(newDate as string)
    if (!isNaN(date.getTime())) {
      handleDateSelect(date)
      router.replace({ query: {} })
    }
  }
})

watch(selectedDate, () => {
  localFilterCategory.value = null
})

watch(filteredPapers, async (papers) => {
  if (papers.length > 0) {
    const paperIds = papers.map(p => p.id).filter(Boolean)
    if (paperIds.length > 0) {
      await bookmarkStore.checkBookmarksBatch(paperIds)
      await downloadStore.checkDownloadsBatch(paperIds)
    }
  }
}, { immediate: true })

onMounted(async () => {
  console.log('Home mounted')
  const handled = await handleRouteQuery()
  if (!handled) {
    checkAndLoadPapers()
  }
})

onActivated(() => {
  console.log('Home activated (returned from another page)')
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding-top: 64px;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 10px 20px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.icon-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.icon-btn:hover svg {
  transform: scale(1.1);
}

.date-btn {
  color: var(--icon-date);
  border-color: color-mix(in srgb, var(--icon-date) 20%, transparent);
}

.date-btn:hover {
  background: color-mix(in srgb, var(--icon-date) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-date) 40%, transparent);
}

.analysis-btn {
  color: var(--icon-analysis);
  border-color: color-mix(in srgb, var(--icon-analysis) 20%, transparent);
}

.analysis-btn:hover {
  background: color-mix(in srgb, var(--icon-analysis) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-analysis) 40%, transparent);
}

.category-btn {
  color: var(--icon-category);
  border-color: color-mix(in srgb, var(--icon-category) 20%, transparent);
}

.category-btn:hover {
  background: color-mix(in srgb, var(--icon-category) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-category) 40%, transparent);
}

.view-toggle-btn {
  color: var(--icon-viewToggle);
  border-color: color-mix(in srgb, var(--icon-viewToggle) 20%, transparent);
}

.view-toggle-btn:hover {
  background: color-mix(in srgb, var(--icon-viewToggle) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-viewToggle) 40%, transparent);
}

.toggle-btn {
  color: var(--icon-toggle);
  border-color: color-mix(in srgb, var(--icon-toggle) 20%, transparent);
}

.toggle-btn:hover {
  background: color-mix(in srgb, var(--icon-toggle) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-toggle) 40%, transparent);
}

.filter-btn {
  color: var(--icon-filter);
  border-color: color-mix(in srgb, var(--icon-filter) 20%, transparent);
}

.filter-btn:hover {
  background: color-mix(in srgb, var(--icon-filter) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-filter) 40%, transparent);
}

.refresh-btn {
  color: var(--icon-refresh);
  border-color: color-mix(in srgb, var(--icon-refresh) 20%, transparent);
}

.refresh-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--icon-refresh) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-refresh) 40%, transparent);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.section-description {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0;
}

.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.error-state svg {
  width: 60px;
  height: 60px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--icon-error);
}

.error-state p {
  font-size: 1.1rem;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 10px 24px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
}

.retry-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.papers-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .papers-grid {
    grid-template-columns: 1fr;
  }
}

.graph-view-container {
  display: grid;
  grid-template-columns: 1fr 280px;
  grid-template-rows: 1fr auto;
  gap: 16px;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.graph-view-container > :first-child {
  grid-row: 1 / 3;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 32px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid #667eea;
  cursor: pointer;
  background: #667eea;
  color: white;
}

.pagination-btn svg {
  width: 20px;
  height: 20px;
}

.pagination-btn:hover:not(:disabled) {
  background: #764ba2;
  color: white;
  border-color: #764ba2;
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  min-width: 80px;
  text-align: center;
  padding: 6px 14px;
}

.pagination-input {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  border: 1px solid #667eea;
  background: var(--bg-secondary);
  color: var(--text-primary);
  width: 80px;
  text-align: center;
  transition: all 0.3s ease;
  overflow: hidden;
}

.pagination-input:focus {
  outline: none;
  border-color: #764ba2;
  box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.1);
}

.pagination-input::placeholder {
  color: var(--text-muted);
}
</style>
