<template>
  <div class="data-manager">
    <div class="data-manager-container">
      <template v-if="viewMode === 'year'">
        <div class="page-header">
          <h1 class="page-title">Data Manager</h1>
          <p class="page-subtitle">Manage locally stored papers by date</p>
        </div>

        <div class="stats-panel">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total_days }}</div>
            <div class="stat-label">Days Stored</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total_embedded_days }}</div>
            <div class="stat-label">Days Embedded</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(statistics.total_papers) }}</div>
            <div class="stat-label">Total Papers</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ yearStats.days }}</div>
            <div class="stat-label">Days in {{ selectedYear }}</div>
            <div class="stat-percent">{{ yearStats.daysPercent }}% of total</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ yearStats.embeddedDays }}</div>
            <div class="stat-label">Embedded in {{ selectedYear }}</div>
            <div class="stat-percent">{{ yearStats.embeddedPercent }}% of total</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(yearStats.papers) }}</div>
            <div class="stat-label">Papers in {{ selectedYear }}</div>
            <div class="stat-percent">{{ yearStats.papersPercent }}% of total</div>
          </div>
        </div>

        <div class="calendar-toolbar">
          <div class="toolbar-group navigation">
            <button class="control-btn" @click="previousYear" title="Previous Year">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <div class="year-select-wrapper">
              <button 
                class="year-select-btn" 
                @click="showYearDropdown = !showYearDropdown"
                @blur="closeYearDropdown"
              >
                <span>{{ selectedYear }}</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>
              <div class="year-dropdown" v-show="showYearDropdown">
                <div class="year-dropdown-content">
                  <div 
                    v-for="year in yearRange" 
                    :key="year" 
                    class="year-option"
                    :class="{ 'selected': year === selectedYear }"
                    @mousedown="selectYear(year)"
                  >
                    {{ year }}
                  </div>
                </div>
              </div>
            </div>
            <button class="control-btn" @click="nextYear" title="Next Year">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
            <button class="control-btn today-btn" @click="goToToday">Today</button>
          </div>

          <div class="toolbar-group legend">
            <div class="legend-item">
              <span class="legend-icon stored">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </span>
              <span>Stored</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon embedding">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <path d="M5 6 Q9 3, 12 6 T19 6"/>
                  <path d="M5 12 Q9 9, 12 12 T19 12"/>
                  <path d="M5 18 Q9 15, 12 18 T19 18"/>
                </svg>
              </span>
              <span>Embedded</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon fetching">
                <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
              </span>
              <span>Fetching</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </span>
              <span>No Papers</span>
            </div>
          </div>
        </div>

        <div class="year-view">
          <div v-for="month in months" :key="month.index" class="month-card">
            <h3 class="month-title clickable" @click="openMonthView(month.index)">
              {{ month.name }}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </h3>
            <div class="month-calendar">
              <div class="weekday-header">
                <span v-for="day in weekdays" :key="day" class="weekday">{{ day }}</span>
              </div>
              <div class="days-grid">
                <Tooltip
                  v-for="(day, idx) in month.days"
                  :key="idx"
                  :content="getDayTooltip(day)"
                  :type="getDayTooltipType(day)"
                  position="top"
                  :delay="300"
                >
                  <span
                    class="day-cell"
                    :class="{
                      'empty': !day.date,
                      'today': day.isToday,
                      'stored': day.stored,
                      'future': day.isFuture,
                      'selected': day.date === selectedDate,
                      'fetching': day.fetching
                    }"
                    @click="handleDayClick(day)"
                    @mouseenter="handleDayMouseEnter(day, $event)"
                    @mouseleave="handleDayMouseLeave"
                  >
                  <span v-if="day.date" class="day-number">{{ day.day }}</span>
                  <div v-if="day.date" class="day-status-icons">
                    <span v-if="day.hasEmbedding" class="day-status embedding-icon" title="Embeddings generated">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <path d="M5 6 Q9 3, 12 6 T19 6"/>
                        <path d="M5 12 Q9 9, 12 12 T19 12"/>
                        <path d="M5 18 Q9 15, 12 18 T19 18"/>
                      </svg>
                    </span>
                    <span v-else-if="day.stored && day.count > 0" class="day-status stored-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    </span>
                    <span v-else-if="day.fetching" class="day-status fetching-icon">
                      <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                      </svg>
                    </span>
                    <span v-else-if="day.count === 0 && day.fetched" class="day-status empty-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                      </svg>
                    </span>
                  </div>
                </span>
                </Tooltip>
              </div>
          </div>
        </div>
      </div>

      <div v-if="selectedDate && viewMode === 'year'" class="date-detail-panel" :style="panelStyle" @mousedown="startDrag">
        <div class="detail-header">
          <h3>{{ formatDate(selectedDate) }}</h3>
          <button class="close-btn" @click="selectedDate = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="detail-content">
          <p v-if="getSelectedDayInfo()?.stored">
            <strong>{{ getSelectedDayInfo()?.count }}</strong> papers stored
          </p>
          <p v-else-if="getSelectedDayInfo()?.isFuture" class="future-warning">
            Cannot fetch papers for future dates
          </p>
          <p v-else>No papers stored for this date</p>
        </div>
        <div class="detail-actions">
          <button
            v-if="!getSelectedDayInfo()?.isFuture"
            class="action-btn fetch-btn"
            :disabled="getSelectedDayInfo()?.fetching"
            @click="selectedDate && handleFetchDate(selectedDate)"
          >
            <svg v-if="!getSelectedDayInfo()?.fetching" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            {{ getSelectedDayInfo()?.fetching ? 'Fetching...' : (getSelectedDayInfo()?.stored ? 'Re-fetch' : 'Fetch Papers') }}
          </button>
          <button
            v-if="getSelectedDayInfo()?.stored"
            class="action-btn embedding-btn"
            :class="{ 'generated': getSelectedDayInfo()?.hasEmbedding }"
            :disabled="!!(selectedDate && generatingEmbeddingDates.has(selectedDate))"
            @click="selectedDate && handleGenerateEmbedding(selectedDate)"
          >
            <svg v-if="!generatingEmbeddingDates.has(selectedDate || '')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M5 6 Q9 3, 12 6 T19 6"/>
              <path d="M5 12 Q9 9, 12 12 T19 12"/>
              <path d="M5 18 Q9 15, 12 18 T19 18"/>
            </svg>
            <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            {{ selectedDate && generatingEmbeddingDates.has(selectedDate) ? 'Generating...' : (getSelectedDayInfo()?.hasEmbedding ? 'Regenerate' : 'Embedding') }}
          </button>
          <button
            v-if="getSelectedDayInfo()?.stored"
            class="action-btn clear-btn"
            @click="clearDateCache(selectedDate)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Clear
          </button>
        </div>
      </div>
      </template>
      <template v-else>
        <MonthView
          :year="selectedYear"
          :month="selectedMonth"
          @back="viewMode = 'year'"
          @viewPapers="viewPapers"
        />
      </template>

      <DayTooltip
        :visible="isTooltipVisible"
        :date="tooltipDate || ''"
        :dateInfo="tooltipDateInfo"
        :embeddingInfo="tooltipEmbeddingInfo"
        :position="tooltipPosition"
        :closable="false"
        @close="closeTooltip"
      />

      <ConfirmDialog
        :visible="showConfirmDialog"
        :title="confirmDialogTitle"
        :message="confirmDialogMessage"
        type="danger"
        confirmText="Clear Cache"
        cancelText="Cancel"
        @confirm="confirmClearCache"
        @cancel="cancelClearCache"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToastStore } from '../stores/toast-store'
import { useRouter } from 'vue-router'
import { arxivBackendAPI } from '../services/arxivBackend'
import { useDateIndexes, useDayTooltip } from '../composables/useDateIndexes'
import MonthView from '../components/MonthView.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import Tooltip from '../components/Tooltip.vue'
import DayTooltip from '../components/DayTooltip.vue'

interface DayInfo {
  date: string | null
  day: number | null
  isToday: boolean
  isFuture: boolean
  stored: boolean
  hasEmbedding: boolean
  count: number
  fetching: boolean
  fetched: boolean
}

const toastStore = useToastStore()
const router = useRouter()

const viewMode = ref<'year' | 'month'>('year')
const selectedYear = ref<number>(new Date().getFullYear())
const showYearDropdown = ref(false)
const selectedMonth = ref(0)
const selectedDate = ref<string | null>(null)

const { 
  dateIndexes, 
  embeddingIndexes,
  dateIndexMap, 
  embeddingIndexMap,
  dateIndexInfoMap,
  embeddingIndexInfoMap,
  fetchingDates,
  generatingEmbeddingDates,
  totalDays, 
  totalPapers,
  totalEmbeddedDays,
  fetchDateIndexes, 
  fetchDate: fetchDateFromComposable,
  generateEmbedding,
  refreshDateIndexes
} = useDateIndexes()

const {
  tooltipDate,
  tooltipPosition,
  tooltipDateInfo,
  tooltipEmbeddingInfo,
  isTooltipVisible,
  showTooltip,
  hideTooltip
} = useDayTooltip(dateIndexInfoMap, embeddingIndexInfoMap)

function handleDayMouseEnter(day: DayInfo, event: MouseEvent) {
  if (!day.date || (!day.stored && !day.hasEmbedding)) return
  showTooltip(day.date, event.clientX, event.clientY)
}

function handleDayMouseLeave() {
  hideTooltip()
}

function closeTooltip() {
  hideTooltip()
}

const statistics = computed(() => ({
  total_days: totalDays.value,
  total_papers: totalPapers.value,
  total_embedded_days: totalEmbeddedDays.value
}))

const yearStats = computed(() => {
  const yearStr = selectedYear.value.toString()
  let days = 0
  let papers = 0
  let embeddedDays = 0
  
  for (const idx of dateIndexes.value) {
    if (idx.date && idx.date.startsWith(yearStr)) {
      if (idx.total_count > 0) days++
      papers += idx.total_count
    }
  }
  
  for (const idx of embeddingIndexes.value) {
    if (idx.date && idx.date.startsWith(yearStr)) {
      embeddedDays++
    }
  }
  
  const daysPercent = totalDays.value > 0 ? ((days / totalDays.value) * 100).toFixed(1) : '0.0'
  const papersPercent = totalPapers.value > 0 ? ((papers / totalPapers.value) * 100).toFixed(1) : '0.0'
  const embeddedPercent = totalEmbeddedDays.value > 0 ? ((embeddedDays / totalEmbeddedDays.value) * 100).toFixed(1) : '0.0'
  
  return { days, papers, embeddedDays, daysPercent, papersPercent, embeddedPercent }
})

const yearRange = computed(() => {
  const currentYear = new Date().getFullYear()
  const startYear = 1991
  
  const years: number[] = []
  for (let year = startYear; year <= currentYear; year++) {
    years.push(year)
  }
  
  return years.sort((a, b) => b - a)
})

const showConfirmDialog = ref(false)
const confirmDialogTitle = ref('Clear Cache')
const confirmDialogMessage = ref('')
const pendingClearDate = ref<string | null>(null)

const panelOffsetX = ref(0)
const panelOffsetY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)

const panelStyle = computed(() => ({
  transform: `translate(${panelOffsetX.value}px, ${panelOffsetY.value}px)`
}))

const startDrag = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.close-btn, .action-btn')) return
  isDragging.value = true
  dragStartX.value = e.clientX - panelOffsetX.value
  dragStartY.value = e.clientY - panelOffsetY.value
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  panelOffsetX.value = e.clientX - dragStartX.value
  panelOffsetY.value = e.clientY - dragStartY.value
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

function openMonthView(month: number) {
  selectedMonth.value = month
  viewMode.value = 'month'
  window.scrollTo({ top: 0, behavior: 'instant' })
}

function viewPapers(date: string) {
  router.push({ path: '/', query: { date } })
}

const months = computed(() => {
  const result = []
  const today = new Date()
  const todayStr = formatDateISO(today)
  
  for (let m = 0; m < 12; m++) {
    const days: DayInfo[] = []
    const firstDay = new Date(selectedYear.value, m, 1)
    const lastDay = new Date(selectedYear.value, m + 1, 0)
    const startWeekday = firstDay.getDay()
    
    for (let i = 0; i < startWeekday; i++) {
      days.push({
        date: null,
        day: null,
        isToday: false,
        isFuture: false,
        stored: false,
        hasEmbedding: false,
        count: 0,
        fetching: false,
        fetched: false
      })
    }
    
    for (let d = 1; d <= lastDay.getDate(); d++) {
      const dateStr = `${selectedYear.value}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      const dateObj = new Date(selectedYear.value, m, d)
      const count = dateIndexMap.value.get(dateStr) ?? 0
      const hasEmbedding = embeddingIndexMap.value.has(dateStr)
      
      days.push({
        date: dateStr,
        day: d,
        isToday: dateStr === todayStr,
        isFuture: dateObj > today,
        stored: count > 0,
        hasEmbedding: hasEmbedding,
        count: count,
        fetching: fetchingDates.value.has(dateStr),
        fetched: dateIndexMap.value.has(dateStr)
      })
    }
    
    result.push({
      index: m,
      name: monthNames[m],
      days
    })
  }
  
  return result
})

function formatDateISO(date: Date): string {
  return date.toISOString().split('T')[0]
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatNumber(num: number): string {
  return num.toLocaleString()
}

function previousYear() {
  selectedYear.value = selectedYear.value - 1
}

function nextYear() {
  selectedYear.value = selectedYear.value + 1
}

function goToToday() {
  const today = new Date()
  selectedYear.value = today.getFullYear()
}

function selectYear(year: number) {
  selectedYear.value = year
  showYearDropdown.value = false
}

function closeYearDropdown() {
  setTimeout(() => {
    showYearDropdown.value = false
  }, 150)
}

function handleDayClick(day: DayInfo) {
  if (!day.date) return
  panelOffsetX.value = 0
  panelOffsetY.value = 0
  selectedDate.value = day.date
}

function getSelectedDayInfo(): DayInfo | undefined {
  if (!selectedDate.value) return undefined
  for (const month of months.value) {
    for (const day of month.days) {
      if (day.date === selectedDate.value) {
        return day
      }
    }
  }
  return undefined
}

function getDayTooltip(day: DayInfo): string {
  if (!day.date) return ''
  if (day.isFuture) return 'Future date'
  if (day.fetching) return 'Fetching papers...'
  if (day.stored && day.count > 0) return ``
  if (day.fetched && day.count === 0) return 'No papers (empty)'
  return 'Click to fetch papers'
}

function getDayTooltipType(day: DayInfo): 'default' | 'info' | 'success' | 'warning' {
  if (day.stored && day.count > 0) return 'success'
  if (day.fetching) return 'warning'
  if (day.isFuture) return 'default'
  return 'info'
}

async function handleFetchDate(date: string) {
  toastStore.showLoading(`Fetching papers for ${date}...`)
  const result = await fetchDateFromComposable(date)
  
  if (result.success) {
    toastStore.showSuccess(`Fetched ${result.count} papers for ${date}`)
  } else {
    toastStore.showError(result.error || `Failed to fetch papers for ${date}`)
  }
}

async function handleGenerateEmbedding(date: string) {
  toastStore.showLoading(`Generating embeddings for ${date}...`)
  const result = await generateEmbedding(date, true)
  
  if (result.success) {
    toastStore.showSuccess(`Generated ${result.generated_count} embeddings for ${date}`)
  } else {
    toastStore.showError(result.error || `Failed to generate embeddings for ${date}`)
  }
}

async function clearDateCache(date: string) {
  pendingClearDate.value = date
  confirmDialogMessage.value = `Are you sure you want to clear the cache for ${date}? This will delete all stored papers for this date and you will need to fetch them again.`
  showConfirmDialog.value = true
}

async function confirmClearCache() {
  if (!pendingClearDate.value) return
  
  const date = pendingClearDate.value
  showConfirmDialog.value = false
  pendingClearDate.value = null
  
  try {
    toastStore.showLoading(`Clearing cache for ${date}...`)
    await arxivBackendAPI.clearDateCache(date)
    toastStore.showSuccess(`Cache cleared for ${date}`)
    await refreshDateIndexes()
  } catch (error) {
    console.error('Failed to clear cache:', error)
    toastStore.showError('Failed to clear cache')
  }
}

function cancelClearCache() {
  showConfirmDialog.value = false
  pendingClearDate.value = null
}

onMounted(() => {
  fetchDateIndexes()
  const today = new Date()
  selectedDate.value = formatDateISO(today)
})
</script>

<style scoped>
.data-manager {
  min-height: 100vh;
  padding-top: 64px;
  background: var(--bg-secondary);
}

.data-manager-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.stats-panel {
  display: flex;
  gap: 24px;
  margin-bottom: 0;
  padding: 24px;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-color) 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stat-percent {
  font-size: 0.8rem;
  color: var(--accent-color);
  margin-top: 2px;
  font-weight: 500;
  opacity: 0.8;
}

.calendar-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 24px;
  background: var(--bg-primary);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-group.navigation {
  gap: 6px;
}

.toolbar-group.legend {
  gap: 16px;
}

.year-select-wrapper {
  position: relative;
}

.year-select-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 110px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.year-select-btn span {
  line-height: 1;
}

.year-select-btn:hover {
  border-color: var(--accent-color);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.year-select-btn:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.2),
    0 2px 8px rgba(0, 0, 0, 0.08);
}

.year-select-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  stroke-width: 2.5;
  transition: transform 0.3s ease;
}

.year-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 100;
}

.year-dropdown-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.15),
    0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 240px;
  overflow-y: auto;
  padding: 8px;
}

.year-dropdown-content::-webkit-scrollbar {
  width: 6px;
}

.year-dropdown-content::-webkit-scrollbar-track {
  background: transparent;
}

.year-dropdown-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.year-dropdown-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.year-option {
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.year-option:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.year-option.selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  color: var(--accent-color);
  font-weight: 600;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.control-btn.today-btn {
  width: auto;
  padding: 0 24px;
  font-weight: 600;
  background: rgba(102, 126, 234, 0.1);
  color: var(--accent-color);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.control-btn.today-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: var(--accent-color);
}

.control-btn svg {
  width: 20px;
  height: 20px;
}

.year-view {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.month-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.month-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.month-card:nth-child(1) { border-top: 4px solid #667eea; }
.month-card:nth-child(2) { border-top: 4px solid #764ba2; }
.month-card:nth-child(3) { border-top: 4px solid #f093fb; }
.month-card:nth-child(4) { border-top: 4px solid #f5576c; }
.month-card:nth-child(5) { border-top: 4px solid #4facfe; }
.month-card:nth-child(6) { border-top: 4px solid #00f2fe; }
.month-card:nth-child(7) { border-top: 4px solid #43e97b; }
.month-card:nth-child(8) { border-top: 4px solid #38f9d7; }
.month-card:nth-child(9) { border-top: 4px solid #fa709a; }
.month-card:nth-child(10) { border-top: 4px solid #fee140; }
.month-card:nth-child(11) { border-top: 4px solid #a8edea; }
.month-card:nth-child(12) { border-top: 4px solid #fed6e3; }

.month-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  text-align: center;
}

.month-title.clickable {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  margin: -4px -8px 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.month-title.clickable:hover {
  background: var(--bg-secondary);
  color: var(--accent-color);
}

.month-title.clickable svg {
  width: 16px;
  height: 16px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.month-title.clickable:hover svg {
  opacity: 1;
}

.month-calendar {
  font-size: 0.75rem;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}

.weekday {
  text-align: center;
  color: var(--text-secondary);
  font-weight: 600;
  padding: 4px 0;
  font-size: 0.65rem;
  text-transform: uppercase;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.days-grid span {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
  background: transparent;
  outline: none;
  border: none;
  box-shadow: none;
  -webkit-appearance: none;
  appearance: none;
}

.day-cell.empty {
  pointer-events: none;
  visibility: hidden;
}

.day-cell:not(.empty) {
  cursor: pointer;
  visibility: visible;
}

.day-cell:not(.empty):hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.1);
}

.day-cell:focus {
  outline: none;
  box-shadow: none;
}

.day-cell:focus-visible {
  outline: none;
  box-shadow: none;
}

.day-cell:active {
  outline: none;
  box-shadow: none;
}

.day-cell.today {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
}

.day-cell.today:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
}

.day-cell.today .day-number {
  color: var(--accent-color);
  font-weight: 700;
}

.day-cell.selected {
  box-shadow: 0 0 0 2px var(--accent-color), 0 4px 15px rgba(102, 126, 234, 0.3);
}

.day-cell.stored {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.15) 0%, rgba(56, 249, 215, 0.15) 100%);
}

.day-cell.stored:hover {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.25) 0%, rgba(56, 249, 215, 0.25) 100%);
}

.day-cell.future {
  opacity: 0.4;
  cursor: not-allowed;
}

.day-cell.fetching {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.2) 0%, rgba(254, 225, 64, 0.2) 100%);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.day-number {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.7rem;
}

.day-status-icons {
  position: absolute;
  bottom: 2px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.day-status {
  width: 10px;
  height: 10px;
}

.day-status svg {
  width: 10px;
  height: 10px;
}

.stored-icon svg {
  stroke: var(--success-color);
}

.embedding-icon svg {
  stroke: #9C27B0;
}

.fetching-icon svg {
  stroke: var(--warning-color);
  animation: spin 1s linear infinite;
}

.empty-icon svg {
  stroke: var(--text-secondary);
  stroke-width: 2;
}

.date-detail-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  min-width: 320px;
  max-width: 380px;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-lg);
  z-index: 100;
  border: 1px solid var(--border-color);
  cursor: move;
  user-select: none;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-header h3 {
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-color) 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: linear-gradient(135deg, var(--accent-color) 0%, #764ba2 100%);
  color: white;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.detail-content {
  margin-bottom: 16px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.future-warning {
  color: var(--warning-color);
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-btn {
  flex: 1;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 10px;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.fetch-btn {
  background: linear-gradient(135deg, var(--accent-color) 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.fetch-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.fetch-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.clear-btn {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.clear-btn:hover {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  color: white;
}

.embedding-btn {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.2) 0%, rgba(254, 225, 64, 0.2) 100%);
  color: var(--warning-color);
  border: 1px solid rgba(250, 112, 154, 0.3);
}

.embedding-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.3) 0%, rgba(254, 225, 64, 0.3) 100%);
  transform: translateY(-2px);
}

.embedding-btn.generated {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.15) 0%, rgba(103, 58, 183, 0.15) 100%);
  color: #9C27B0;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.embedding-btn.generated:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.25) 0%, rgba(103, 58, 183, 0.25) 100%);
}

.embedding-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toolbar-group.legend .legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.toolbar-group.legend .legend-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.toolbar-group.legend .legend-icon {
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-group.legend .legend-icon svg {
  width: 12px;
  height: 12px;
}

.legend-icon.stored svg {
  stroke: var(--success-color);
}

.legend-icon.embedding svg {
  stroke: #9C27B0;
}

.legend-icon.fetching svg {
  stroke: var(--warning-color);
}

.legend-icon.empty svg {
  stroke: var(--text-secondary);
  stroke-width: 2;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1200px) {
  .year-view {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .year-view {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .data-manager-container {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 2rem;
  }

  .stats-panel {
    flex-direction: column;
    gap: 16px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .year-select {
    min-width: 80px;
    padding: 8px 12px;
    padding-right: 32px;
    font-size: 0.9rem;
  }

  .year-view {
    grid-template-columns: 1fr;
  }

  .date-detail-panel {
    left: 16px;
    right: 16px;
    width: auto;
    bottom: 16px;
  }

  .legend {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
