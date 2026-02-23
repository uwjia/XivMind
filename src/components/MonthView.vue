<template>
  <div class="month-view">
    <div class="month-view-header">
      <button class="back-btn" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        <span>Back to Year View</span>
      </button>
      <h2 class="month-title">{{ monthName }} {{ year }}</h2>
    </div>

    <div class="month-stats">
      <div class="stat-card">
        <div class="stat-icon stored">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ storedDays }}</div>
          <div class="stat-label">Days Stored</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon embedding-stat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="6" cy="6" r="2"/>
            <circle cx="18" cy="6" r="2"/>
            <circle cx="6" cy="18" r="2"/>
            <circle cx="18" cy="18" r="2"/>
            <circle cx="12" cy="12" r="2.5"/>
            <line x1="7.5" y1="7.5" x2="10" y2="10"/>
            <line x1="13.5" y1="7.5" x2="14" y2="10"/>
            <line x1="7.5" y1="16.5" x2="10" y2="14"/>
            <line x1="13.5" y1="16.5" x2="14" y2="14"/>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ embeddedDays }}</div>
          <div class="stat-label">Days Embedded</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon papers">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPapers }}</div>
          <div class="stat-label">Total Papers</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon avg">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="12" y1="20" x2="12" y2="10"/>
            <line x1="18" y1="20" x2="18" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="16"/>
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ avgPapers }}</div>
          <div class="stat-label">Avg/Day</div>
        </div>
      </div>
    </div>

    <div class="calendar-grid">
      <div class="weekday-row">
        <div v-for="day in weekdays" :key="day" class="weekday-cell">{{ day }}</div>
      </div>
      <div class="days-grid">
        <div
          v-for="(day, idx) in calendarDays"
          :key="idx"
          class="day-card"
          :class="{
            'empty': !day.date,
            'today': day.isToday,
            'stored': day.stored,
            'future': day.isFuture,
            'selected': day.date === selectedDate,
            'fetching': day.date ? fetchingDates.has(day.date) : false
          }"
          @click="handleDayClick(day, $event)"
        >
          <template v-if="day.date">
            <div class="day-header">
              <span class="day-number">{{ day.day }}</span>
              <div class="day-badges">
                <span v-if="day.hasEmbedding" class="day-badge embedding" title="Embeddings generated">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="6" cy="6" r="2"/>
                    <circle cx="18" cy="6" r="2"/>
                    <circle cx="6" cy="18" r="2"/>
                    <circle cx="18" cy="18" r="2"/>
                    <circle cx="12" cy="12" r="2.5"/>
                    <line x1="7.5" y1="7.5" x2="10" y2="10"/>
                    <line x1="13.5" y1="7.5" x2="14" y2="10"/>
                    <line x1="7.5" y1="16.5" x2="10" y2="14"/>
                    <line x1="13.5" y1="16.5" x2="14" y2="14"/>
                  </svg>
                </span>
                <span v-if="day.stored" class="day-badge stored" title="Papers stored">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="day-content">
              <div v-if="day.stored" class="paper-count">
                <span class="count-value">{{ day.count }}</span>
                <span class="count-label">papers</span>
              </div>
              <div v-else-if="day.isFuture" class="future-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <span>Future</span>
              </div>
              <div v-else-if="fetchingDates.has(day.date)" class="fetching-label">
                <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                <span>Fetching...</span>
              </div>
              <div v-else class="empty-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>No data</span>
              </div>
            </div>
            <div class="day-actions">
              <button
                v-if="!day.isFuture && !day.stored"
                class="action-btn fetch"
                :disabled="fetchingDates.has(day.date || '')"
                :title="fetchingDates.has(day.date || '') ? 'Fetching...' : 'Fetch papers for this date'"
                @click.stop="day.date && handleFetchDate(day.date)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
              </button>
              <button
                v-if="day.stored"
                class="action-btn embedding"
                :class="{ 'loading': generatingEmbeddingDates.has(day.date || ''), 'generated': day.hasEmbedding }"
                :disabled="generatingEmbeddingDates.has(day.date || '')"
                :title="generatingEmbeddingDates.has(day.date || '') ? 'Generating...' : (day.hasEmbedding ? 'Regenerate embeddings for this date' : 'Generate embeddings for this date')"
                @click.stop="day.date && handleGenerateEmbedding(day.date)"
              >
                <svg v-if="!generatingEmbeddingDates.has(day.date || '')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="6" cy="6" r="2"/>
                  <circle cx="18" cy="6" r="2"/>
                  <circle cx="6" cy="18" r="2"/>
                  <circle cx="18" cy="18" r="2"/>
                  <circle cx="12" cy="12" r="2.5"/>
                  <line x1="7.5" y1="7.5" x2="10" y2="10"/>
                  <line x1="13.5" y1="7.5" x2="14" y2="10"/>
                  <line x1="7.5" y1="16.5" x2="10" y2="14"/>
                  <line x1="13.5" y1="16.5" x2="14" y2="14"/>
                </svg>
                <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
              </button>
              <button
                v-if="day.stored"
                class="action-btn view"
                title="View papers for this date"
                @click.stop="day.date && $emit('viewPapers', day.date)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button
                v-if="day.stored"
                class="action-btn refetch"
                :class="{ 'loading': fetchingDates.has(day.date || '') }"
                :disabled="fetchingDates.has(day.date || '')"
                :title="fetchingDates.has(day.date || '') ? 'Fetching...' : 'Re-fetch papers for this date'"
                @click.stop="day.date && handleFetchDate(day.date)"
              >
                <svg v-if="!fetchingDates.has(day.date || '')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 4v6h-6"/>
                  <path d="M1 20v-6h6"/>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                </svg>
                <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <DayTooltip
      :visible="isTooltipVisible"
      :date="tooltipDate || ''"
      :dateInfo="tooltipDateInfo"
      :embeddingInfo="tooltipEmbeddingInfo"
      :position="tooltipPosition"
      :closable="true"
      @close="closeTooltip"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useDateIndexes, useDayTooltip } from '../composables/useDateIndexes'
import DayTooltip from './DayTooltip.vue'

interface DayInfo {
  date: string | null
  day: number | null
  isToday: boolean
  isFuture: boolean
  stored: boolean
  hasEmbedding: boolean
  embeddingCount: number
  count: number
  fetching: boolean
  fetched: boolean
}

const props = defineProps<{
  year: number
  month: number
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'viewPapers', date: string): void
}>()

const selectedDate = ref<string | null>(null)

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const monthName = computed(() => monthNames[props.month])

const {
  dateIndexMap,
  embeddingIndexMap,
  dateIndexInfoMap,
  embeddingIndexInfoMap,
  fetchingDates,
  generatingEmbeddingDates,
  fetchDate,
  generateEmbedding
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

const calendarDays = computed(() => {
  const days: DayInfo[] = []
  const today = new Date()
  const todayStr = formatDateISO(today)
  const firstDay = new Date(props.year, props.month, 1)
  const lastDay = new Date(props.year, props.month + 1, 0)
  const startWeekday = firstDay.getDay()

  for (let i = 0; i < startWeekday; i++) {
    days.push({
      date: null,
      day: null,
      isToday: false,
      isFuture: false,
      stored: false,
      hasEmbedding: false,
      embeddingCount: 0,
      count: 0,
      fetching: false,
      fetched: false
    })
  }

  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${props.year}-${String(props.month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dateObj = new Date(props.year, props.month, d)
    const count = dateIndexMap.value.get(dateStr) ?? 0
    const embeddingInfo = embeddingIndexMap.value.get(dateStr)

    days.push({
      date: dateStr,
      day: d,
      isToday: dateStr === todayStr,
      isFuture: dateObj > today,
      stored: count > 0,
      hasEmbedding: !!embeddingInfo,
      embeddingCount: embeddingInfo?.count ?? 0,
      count: count,
      fetching: fetchingDates.value.has(dateStr),
      fetched: dateIndexMap.value.has(dateStr)
    })
  }

  return days
})

const storedDays = computed(() => {
  return calendarDays.value.filter(d => d.stored).length
})

const embeddedDays = computed(() => {
  return calendarDays.value.filter(d => d.hasEmbedding).length
})

const totalPapers = computed(() => {
  return calendarDays.value.reduce((sum, d) => sum + d.count, 0)
})

const avgPapers = computed(() => {
  const days = storedDays.value
  return days > 0 ? Math.round(totalPapers.value / days) : 0
})

function formatDateISO(date: Date): string {
  return date.toISOString().split('T')[0]
}

function handleDayClick(day: DayInfo, event: MouseEvent) {
  if (!day.date) return
  selectedDate.value = day.date
  
  if (day.stored || day.hasEmbedding) {
    showTooltip(day.date, event.clientX, event.clientY)
  } else {
    hideTooltip()
  }
}

function closeTooltip() {
  hideTooltip()
}

async function handleFetchDate(date: string) {
  await fetchDate(date)
}

async function handleGenerateEmbedding(date: string) {
  await generateEmbedding(date)
}
</script>

<style scoped>
.month-view {
  padding: 24px;
}

.month-view-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.month-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.month-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-icon.stored {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%);
  color: var(--success-color);
}

.stat-icon.embedding-stat {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.2) 0%, rgba(103, 58, 183, 0.2) 100%);
  color: #9C27B0;
}

.stat-icon.papers {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: var(--accent-color);
}

.stat-icon.avg {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.2) 0%, rgba(254, 225, 64, 0.2) 100%);
  color: var(--warning-color);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.calendar-grid {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.weekday-cell {
  text-align: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 8px 0;
  text-transform: uppercase;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.day-card {
  min-height: 120px;
  padding: 12px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.day-card.empty {
  background: transparent;
  cursor: default;
  pointer-events: none;
}

.day-card:not(.empty):hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.day-card.today {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-color: var(--accent-color);
}

.day-card.stored {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%);
}

.day-card.future {
  opacity: 0.5;
  cursor: not-allowed;
}

.day-card.fetching {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.15) 0%, rgba(254, 225, 64, 0.15) 100%);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.day-number {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.day-badges {
  display: flex;
  align-items: center;
  gap: 2px;
}

.day-badge {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-badge svg {
  width: 16px;
  height: 16px;
  stroke: var(--success-color);
}

.day-badge.embedding svg {
  stroke: #9C27B0;
}

.day-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.paper-count {
  text-align: center;
}

.count-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-color);
}

.count-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.future-label,
.fetching-label,
.empty-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.future-label svg,
.fetching-label svg,
.empty-label svg {
  width: 24px;
  height: 24px;
}

.fetching-label svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.day-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn.fetch {
  background: rgba(102, 126, 234, 0.1);
  color: var(--accent-color);
}

.action-btn.fetch:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.action-btn.fetch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.view {
  background: rgba(32, 178, 170, 0.1);
  color: #20B2AA;
}

.action-btn.view:hover {
  background: rgba(32, 178, 170, 0.2);
  transform: scale(1.1);
}

.action-btn.refetch {
  background: rgba(102, 126, 234, 0.1);
  color: var(--accent-color);
}

.action-btn.refetch:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.action-btn.refetch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.refetch.loading svg {
  animation: spin 1s linear infinite;
}

.action-btn.embedding {
  background: rgba(250, 112, 154, 0.1);
  color: var(--warning-color);
}

.action-btn.embedding:hover:not(:disabled) {
  background: rgba(250, 112, 154, 0.2);
  transform: scale(1.1);
}

.action-btn.embedding.generated {
  background: rgba(156, 39, 176, 0.15);
  color: #9C27B0;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.action-btn.embedding.generated:hover:not(:disabled) {
  background: rgba(156, 39, 176, 0.25);
  transform: scale(1.1);
}

.action-btn.embedding:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.embedding.loading svg {
  animation: spin 1s linear infinite;
}

@media (max-width: 900px) {
  .month-stats {
    flex-direction: column;
  }

  .day-card {
    min-height: 100px;
    padding: 8px;
  }

  .count-value {
    font-size: 1.25rem;
  }
}

@media (max-width: 600px) {
  .month-view {
    padding: 16px;
  }

  .month-view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .day-card {
    min-height: 80px;
    padding: 6px;
  }

  .day-number {
    font-size: 0.85rem;
  }

  .count-value {
    font-size: 1rem;
  }
}

@media (max-width: 600px) {
  .month-view {
    padding: 16px;
  }

  .month-view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
