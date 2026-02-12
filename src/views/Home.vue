<template>
  <div class="home">

    <div class="content">
      <div class="content-header">
        <div>
          <p v-if="filterDescription" class="section-description">{{ filterDescription }}</p>
        </div>
        <div class="header-actions">
          <button class="toggle-btn" @click="configStore.setUseSimpleCard(!configStore.useSimpleCard)" :title="configStore.useSimpleCard ? 'Switch to detailed view' : 'Switch to simple view'">
            <svg viewBox="0 0 24 24" fill="none" stroke="url(#toggleGradient)" stroke-width="2">
              <defs>
                <linearGradient id="toggleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea"/>
                  <stop offset="100%" style="stop-color:#764ba2"/>
                </linearGradient>
              </defs>
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
            <span>{{ configStore.useSimpleCard ? 'Detailed' : 'Simple' }}</span>
          </button>
          <button class="refresh-btn" @click="refreshPapers" :disabled="loading">
            <svg viewBox="0 0 24 24" fill="none" stroke="url(#refreshGradient)" stroke-width="2">
              <defs>
                <linearGradient id="refreshGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#00BCD4"/>
                  <stop offset="100%" style="stop-color:#2196F3"/>
                </linearGradient>
              </defs>
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            <span v-if="loading">Loading...</span>
            <span v-else>Refresh</span>
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

      <div v-if="!loading && (filteredPapers.length > 0 || currentPage > 0)" class="pagination">
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
          <span class="pagination-info">Page {{ currentPage + 1 }}</span>
          <input 
            type="number" 
            v-model.number="jumpPageInput" 
            class="pagination-input" 
            placeholder="num"
            min="1"
            @keyup.enter="goToPage"
          />
          <button class="pagination-btn" @click="goToPage">Go</button>
        </div>
        <button class="pagination-btn" @click="goToNextPage">
          Next
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

      <div v-if="!loading && filteredPapers.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9.172 16.172a4 4 0 0 1-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
        </svg>
        <p>No papers found matching your criteria</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onActivated, toRefs, ref } from 'vue'
import { usePaperStore } from '../stores/paper-store'
import { useToastStore } from '../stores/toast-store'
import { useConfigStore } from '../stores/config-store'
import { categories } from '../utils/categoryColors'
import PaperCard from '../components/PaperCard.vue'
import PaperCardSimple from '../components/PaperCardSimple.vue'
import type { Paper } from '../types'

const paperStore = usePaperStore()
const toastStore = useToastStore()
const configStore = useConfigStore()

const { currentPage } = toRefs(paperStore)
const jumpPageInput = ref<string>('')

const loading = computed(() => paperStore.loading)
const error = computed(() => paperStore.error)
const selectedCategory = computed(() => paperStore.selectedCategory)
const selectedDate = computed(() => paperStore.selectedDate)

const filteredPapers = computed<Paper[]>(() => {
  return paperStore.getFilteredPapers()
})

const goToFirstPage = () => {
  paperStore.setCurrentPage(0)
  loadPapers()
  window.scrollTo({ top: 0, behavior: 'instant' })
}

const goToPreviousPage = () => {
  if (currentPage.value > 0) {
    paperStore.setCurrentPage(currentPage.value - 1)
    loadPapers()
    window.scrollTo({ top: 0, behavior: 'instant' })
  }
}

const goToNextPage = () => {
  paperStore.setCurrentPage(currentPage.value + 1)
  loadPapers()
  window.scrollTo({ top: 0, behavior: 'instant' })
}

const goToPage = () => {
  const targetPage = parseInt(jumpPageInput.value)
  if (targetPage && targetPage > 0) {
    paperStore.setCurrentPage(targetPage - 1)
    loadPapers()
    window.scrollTo({ top: 0, behavior: 'instant' })
    jumpPageInput.value = ''
  }
}

const filterDescription = computed(() => {
  const parts = []
  
  if (selectedCategory.value !== 'all') {
    const category = categories.find(cat => cat.id === selectedCategory.value)
    if (category) {
      parts.push(`${selectedCategory.value} (${category.name})`)
    } else {
      parts.push(selectedCategory.value)
    }
  }
  
  if (selectedDate.value !== 'all') {
    if (selectedDate.value instanceof Date) {
      const year = selectedDate.value.getFullYear()
      const month = String(selectedDate.value.getMonth() + 1).padStart(2, '0')
      const day = String(selectedDate.value.getDate()).padStart(2, '0')
        
      const dateStr = `${year}-${month}-${day}`
      
      parts.push(dateStr)
    } else {
      console.log('filterDescription selectedDate...', selectedDate.value)
      parts.push(selectedDate.value)
    }
  }
  
  parts.push(`Page ${ currentPage.value + 1 } of ${filteredPapers.value.length} papers`)
  
  return parts.join(' · ')
})

const loadPapers = async () => {
  try {
    console.log('currentPage:', currentPage, 'currentPage.value:', currentPage.value, 'pageSize:', configStore.maxResults)
    const startIndex = currentPage.value * configStore.maxResults
    console.log('Loading papers...', selectedCategory.value, selectedDate.value, startIndex)
    toastStore.showLoading('Loading papers...')
    const category = selectedCategory.value === 'all' ? 'cs*' : selectedCategory.value
    const dateValue = selectedDate.value
    
    if (dateValue === 'all') {
      const result = await paperStore.fetchPapers({ category, maxResults: configStore.maxResults, start: startIndex })
      console.log('Loaded papers:', result)
    } else if (dateValue && (typeof dateValue === 'string' || dateValue instanceof Date || (typeof dateValue === 'object' && 'startDate' in dateValue && 'endDate' in dateValue))) {
      let startDate: Date | null = null
      let endDate: Date | null = null
      
      if (dateValue instanceof Date) {
        const year = dateValue.getFullYear()
        startDate = new Date(Date.UTC(year, dateValue.getMonth(), dateValue.getDate(), 0, 0, 0))
        endDate = new Date(Date.UTC(year, dateValue.getMonth(), dateValue.getDate(), 23, 59, 59))
      } else if (typeof dateValue === 'object' && 'startDate' in dateValue && 'endDate' in dateValue) {
        startDate = new Date(dateValue.startDate)
        endDate = new Date(dateValue.endDate)
      }
      
      if (startDate && endDate) {
        const year = startDate.getFullYear()
        const month = String(startDate.getMonth() + 1).padStart(2, '0')
        const day = String(startDate.getDate()).padStart(2, '0')
        
        const startTimestamp = `${year}${month}${day}000000`
        const endTimestamp = `${year}${month}${day}235959`
        const result = await paperStore.fetchPapersByDateRange(startTimestamp, endTimestamp, category, configStore.maxResults, startIndex)
        console.log('Loaded papers by date range:', result)
      } else {
        const result = await paperStore.fetchPapers({ category, maxResults: configStore.maxResults, start: startIndex })
        console.log('Loaded papers:', result)
      }
    } else {
      const result = await paperStore.fetchPapers({ category, maxResults: configStore.maxResults, start: startIndex })
      console.log('Loaded papers:', result)
    }
    console.log('Total papers in store:', paperStore.papers.length)
    toastStore.showSuccess('Papers loaded successfully!')
    // Scroll to top after loading papers
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch (err) {
    console.error('Failed to load papers:', err)
    toastStore.showError('Failed to load papers. Please try again.')
  }
}

const refreshPapers = async () => {
  console.log('Refreshing papers...')
  await loadPapers()
}

const checkAndLoadPapers = () => {
  console.log('Checking if papers need to be loaded...')
  console.log('Current papers count:', paperStore.papers.length)
  if (paperStore.papers.length === 0) {
    console.log('No papers in store, loading papers...')
    loadPapers()
  } else {
    console.log('Papers already loaded, skipping fetch')
  }
}

onMounted(() => {
  console.log('Home mounted')
  checkAndLoadPapers()
})

onActivated(() => {
  console.log('Home activated (returned from another page)')
  checkAndLoadPapers()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding-top: 64px;
}

.content {
  max-width: 1400px;
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
  gap: 12px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 2px solid transparent;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 12px;
  color: #667eea;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  backdrop-filter: blur(10px);
}

.toggle-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: #764ba2;
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
}

.toggle-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.toggle-btn svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.toggle-btn:hover svg {
  transform: rotate(5deg) scale(1.1);
}

.section-description {
  font-size: 1.0rem;
  font-weight: 600;
  color: #00BCD4;
  background-color: rgba(0, 188, 212, 0.1);
  border: 1px solid rgba(0, 188, 212, 0.3);
  border-radius: 20px;
  padding: 6px 16px;
  display: inline-block;
  backdrop-filter: blur(10px);
  margin: 8px 0 0 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 2px solid transparent;
  background: linear-gradient(135deg, rgba(0, 188, 212, 0.1) 0%, rgba(33, 150, 243, 0.1) 100%);
  border-radius: 12px;
  color: #00BCD4;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.15);
  backdrop-filter: blur(10px);
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0, 188, 212, 0.2) 0%, rgba(33, 150, 243, 0.2) 100%);
  color: #2196F3;
  border-color: rgba(0, 188, 212, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 188, 212, 0.25);
}

.refresh-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 188, 212, 0.2);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.refresh-btn svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.refresh-btn:hover:not(:disabled) svg {
  animation: rotate 0.6s ease-in-out;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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
  color: #ef4444;
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
