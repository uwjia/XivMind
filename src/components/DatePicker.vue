<template>
  <div class="date-picker-overlay" v-if="isOpen" @click="closeOutside">
    <div class="date-picker" @click.stop>
      <div class="date-picker-content">
        <div class="date-picker-left">
          <div class="date-picker-selector">
            <div class="year-select-wrapper">
              <button 
                class="year-select-btn" 
                :class="{ 'dark': isDark }"
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
                    :class="{ 'selected': year === selectedYear, 'dark': isDark }"
                    @mousedown="selectYear(year)"
                  >
                    {{ year }}
                  </div>
                </div>
              </div>
            </div>
            <button class="month-nav-btn" :class="{ dark: isDark }" @click="prevMonth" title="Previous Month">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <div class="month-select-wrapper">
              <button 
                class="month-select-btn" 
                :class="{ 'dark': isDark }"
                @click="showMonthDropdown = !showMonthDropdown"
                @blur="closeMonthDropdown"
              >
                <span>{{ months[selectedMonth] }}</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>
              <div class="month-dropdown" v-show="showMonthDropdown">
                <div class="month-dropdown-content">
                  <div 
                    v-for="(month, index) in months" 
                    :key="index" 
                    class="month-option"
                    :class="{ 'selected': index === selectedMonth, 'dark': isDark }"
                    @mousedown="selectMonth(index)"
                  >
                    {{ month }}
                  </div>
                </div>
              </div>
            </div>
            <button class="month-nav-btn" :class="{ dark: isDark }" @click="nextMonth" title="Next Month">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
            <button class="today-btn" :class="{ 'dark': isDark }" @click="selectToday" title="Today">
              Today
            </button>
          </div>

          <div class="date-picker-weekdays">
            <span v-for="day in weekdays" :key="day" class="weekday">{{ day }}</span>
          </div>

          <div class="date-picker-days">
            <button
              v-for="day in calendarDays"
              :key="day.key"
              class="day-btn"
              :class="{
                'other-month': day.isOtherMonth,
                'today': day.isToday,
                'selected': day.isSelected,
                'disabled': day.isDisabled,
                'stored': day.isStored,
                'has-embedding': day.hasEmbedding
              }"
              :disabled="day.isDisabled"
              :title="getDayTooltip(day)"
              @click="tempSelectDate(day.date)"
              @dblclick="handleDayDblClick(day.date)"
            >
              <span class="day-number">{{ day.day }}</span>
              <span v-if="day.hasEmbedding" class="embedding-indicator" title="Embedding generated">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <path d="M5 6 Q9 3, 12 6 T19 6"/>
                  <path d="M5 12 Q9 9, 12 12 T19 12"/>
                  <path d="M5 18 Q9 15, 12 18 T19 18"/>
                </svg>
              </span>
              <span v-else-if="day.isStored" class="stored-indicator" title="Papers stored">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </span>
            </button>
          </div>
        </div>

        <div class="date-picker-right">
          <div class="date-picker-presets">
            <h4 class="presets-title">Quick Select</h4>
            <button class="preset-btn" :style="getPresetStyle('all')" @click="tempSelectPreset('all')">All Time</button>
            <button class="preset-btn" :style="getPresetStyle('1')" @click="tempSelectPreset('Last 24h')">Last 24h</button>
            <button class="preset-btn" :style="getPresetStyle('7')" @click="tempSelectPreset('Last 7 Days')">Last 7 Days</button>
          </div>

          <div class="date-picker-selected">
            <h4 class="selected-title">Selected Date</h4>
            <div class="selected-date">{{ formattedSelectedDate }}</div>
          </div>

          <div class="date-picker-actions">
            <button class="action-btn cancel-btn" @click="cancelSelection">Cancel</button>
            <button class="action-btn confirm-btn" @click="confirmSelection">Confirm</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useThemeStore } from '../stores/theme-store'
import { useDateIndexes } from '../composables/useDateIndexes'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
const { storedDatesMap, embeddingIndexMap } = useDateIndexes()

const props = defineProps<{
  isOpen: boolean
  modelValue: string | Date | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | Date]
  'update:isOpen': [value: boolean]
}>()

const currentDate = ref<Date>(new Date())
const selectedYear = ref<number>(currentDate.value.getFullYear())
const selectedMonth = ref<number>(currentDate.value.getMonth())
const showYearDropdown = ref(false)
const showMonthDropdown = ref(false)
const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
const tempSelectedDate = ref<string | Date | null>(null)

interface CalendarDay {
  day: number
  date: Date
  isOtherMonth: boolean
  isToday: boolean
  isSelected: boolean
  isDisabled: boolean
  key: string | number
  isStored: boolean
  hasEmbedding: boolean
  paperCount: number
}

const yearRange = computed<number[]>(() => {
  const currentYear = new Date().getFullYear()
  const startYear = 1991
  const years: number[] = []
  for (let year = startYear; year <= currentYear; year++) {
    years.push(year)
  }
  return years.sort((a, b) => b - a)
})

const updateDateFromSelect = () => {
  currentDate.value = new Date(selectedYear.value, selectedMonth.value, 1)
  tempSelectedDate.value = new Date(selectedYear.value, selectedMonth.value, 1)
}

const selectYear = (year: number) => {
  selectedYear.value = year
  showYearDropdown.value = false
  updateDateFromSelect()
}

const closeYearDropdown = () => {
  setTimeout(() => {
    showYearDropdown.value = false
  }, 150)
}

const selectMonth = (month: number) => {
  selectedMonth.value = month
  showMonthDropdown.value = false
  updateDateFromSelect()
}

const closeMonthDropdown = () => {
  setTimeout(() => {
    showMonthDropdown.value = false
  }, 150)
}

const presetColors: Record<string, string> = {
  'all': '#9E9E9E',
  '1': '#4CAF50',
  '7': '#2196F3'
}

const getPresetColor = (preset: string): string => {
  return presetColors[preset] || '#9E9E9E'
}

const getPresetStyle = (preset: string): Record<string, string> => {
  const color = getPresetColor(preset)
  return {
    color: color,
    borderColor: color,
    backgroundColor: `${color}15`,
    border: `1px solid ${color}30`
  }
}

const formattedSelectedDate = computed<string>(() => {
  if (!tempSelectedDate.value) return 'No date selected'
  
  const date = tempSelectedDate.value
  if (typeof date === 'string') {
    if (date === 'all') return 'All Time'
    if (date === '1') return 'Last 24h'
    if (date === '7') return 'Last 7 Days'
    return date
  }
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()
  
  const days: CalendarDay[] = []
  const today = new Date()
  
  const getDateStr = (y: number, m: number, d: number) => 
    `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
  
  for (let i = 0; i < firstDay; i++) {
    const day = daysInPrevMonth - firstDay + i + 1
    const dateStr = getDateStr(year, month - 1, day)
    const paperCount = storedDatesMap.value.get(dateStr) ?? 0
    const hasEmbedding = embeddingIndexMap.value.has(dateStr)
    days.push({
      day,
      date: new Date(year, month - 1, day),
      isOtherMonth: true,
      isToday: false,
      isSelected: false,
      isDisabled: true,
      key: `prev-${i}`,
      isStored: paperCount > 0,
      hasEmbedding,
      paperCount
    })
  }
  
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i)
    const isTodayDate = date.toDateString() === today.toDateString()
    const isSelectedDate = tempSelectedDate.value && typeof tempSelectedDate.value === 'object' && date.toDateString() === tempSelectedDate.value.toDateString() || false
    const dateStr = getDateStr(year, month, i)
    const paperCount = storedDatesMap.value.get(dateStr) ?? 0
    const hasEmbedding = embeddingIndexMap.value.has(dateStr)
    days.push({
      day: i,
      date,
      isOtherMonth: false,
      isToday: isTodayDate,
      isSelected: isSelectedDate,
      isDisabled: date > today,
      key: i,
      isStored: paperCount > 0,
      hasEmbedding,
      paperCount
    })
  }
  
  const totalCells = Math.ceil(days.length / 7) * 7
  const remainingDays = totalCells - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const dateStr = getDateStr(year, month + 1, i)
    const paperCount = storedDatesMap.value.get(dateStr) ?? 0
    const hasEmbedding = embeddingIndexMap.value.has(dateStr)
    days.push({
      day: i,
      date: new Date(year, month + 1, i),
      isOtherMonth: true,
      isToday: false,
      isSelected: false,
      isDisabled: true,
      key: `next-${i}`,
      isStored: paperCount > 0,
      hasEmbedding,
      paperCount
    })
  }
  
  return days
})

const getDayTooltip = (day: CalendarDay): string => {
  if (day.hasEmbedding) {
    return `${day.paperCount} papers stored, embedding generated`
  }
  if (day.isStored) {
    return `${day.paperCount} papers stored`
  }
  return ''
}

const prevMonth = () => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const newDate = new Date(year, month - 1, 1)
  currentDate.value = newDate
  selectedYear.value = newDate.getFullYear()
  selectedMonth.value = newDate.getMonth()
  tempSelectedDate.value = newDate
}

const nextMonth = () => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const newDate = new Date(year, month + 1, 1)
  currentDate.value = newDate
  selectedYear.value = newDate.getFullYear()
  selectedMonth.value = newDate.getMonth()
  tempSelectedDate.value = newDate
}

const selectToday = () => {
  const today = new Date()
  tempSelectedDate.value = today
  currentDate.value = today
  selectedYear.value = today.getFullYear()
  selectedMonth.value = today.getMonth()
}

const tempSelectDate = (date: Date) => {
  tempSelectedDate.value = date
}

const tempSelectPreset = (preset: string) => {
  tempSelectedDate.value = preset
}

const cancelSelection = () => {
  tempSelectedDate.value = null
  emit('update:isOpen', false)
}

const confirmSelection = () => {
  if (tempSelectedDate.value !== null) {
    if (typeof tempSelectedDate.value === 'string') {
      emit('update:modelValue', tempSelectedDate.value)
    } else {
      emit('update:modelValue', tempSelectedDate.value)
    }
    emit('update:isOpen', false)
  }
}

const handleDayDblClick = (date: Date) => {
  tempSelectedDate.value = date
  confirmSelection()
}

const closeOutside = () => {
  emit('update:isOpen', false)
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    if (typeof props.modelValue === 'object' && props.modelValue) {
      currentDate.value = new Date(props.modelValue)
      selectedYear.value = currentDate.value.getFullYear()
      selectedMonth.value = currentDate.value.getMonth()
      tempSelectedDate.value = new Date(props.modelValue)
    } else if (typeof props.modelValue === 'string' && props.modelValue !== 'all') {
      tempSelectedDate.value = props.modelValue
    } else {
      const today = new Date()
      currentDate.value = today
      selectedYear.value = today.getFullYear()
      selectedMonth.value = today.getMonth()
      tempSelectedDate.value = today
    }
  }
})
</script>

<style scoped>
.date-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.date-picker {
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  padding: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.date-picker-content {
  display: flex;
  gap: 20px;
}

.date-picker-left {
  flex: 1;
  min-width: 400px;
}

.date-picker-right {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-picker-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.year-select-wrapper {
  position: relative;
}

.year-select-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: white;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 90px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.year-select-btn span {
  line-height: 1;
}

.year-select-btn:hover {
  color: #2196F3;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
}

.year-select-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3);
}

.year-select-btn.dark {
  background: #1e293b;
  color: #f1f5f9;
}

.year-select-btn.dark:hover {
  color: #38bdf8;
  box-shadow: 0 2px 6px rgba(56, 189, 248, 0.2);
}

.year-select-btn svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  stroke-width: 2.5;
}

.year-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 100;
}

.year-dropdown-content {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  padding: 6px;
}

.year-dropdown-content::-webkit-scrollbar {
  width: 5px;
}

.year-dropdown-content::-webkit-scrollbar-track {
  background: transparent;
}

.year-dropdown-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.year-option {
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748b;
  transition: all 0.15s ease;
}

.year-option:hover {
  background: #f1f5f9;
  color: #2196F3;
}

.year-option.selected {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(33, 150, 243, 0.1));
  color: #2196F3;
  font-weight: 600;
}

.year-option.dark {
  color: #94a3b8;
}

.year-option.dark:hover {
  background: #334155;
  color: #38bdf8;
}

.year-option.dark.selected {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(56, 189, 248, 0.1));
  color: #38bdf8;
}

.year-dropdown-content:has(.year-option.dark) {
  background: #1e293b;
  border-color: #475569;
}

.month-select-wrapper {
  position: relative;
}

.month-select-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: white;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 60px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.month-select-btn span {
  line-height: 1;
}

.month-select-btn:hover {
  color: #2196F3;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
}

.month-select-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3);
}

.month-select-btn.dark {
  background: #1e293b;
  color: #f1f5f9;
}

.month-select-btn.dark:hover {
  color: #38bdf8;
  box-shadow: 0 2px 6px rgba(56, 189, 248, 0.2);
}

.month-select-btn svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  stroke-width: 2.5;
}

.month-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 100;
}

.month-dropdown-content {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  padding: 6px;
}

.month-dropdown-content::-webkit-scrollbar {
  width: 5px;
}

.month-dropdown-content::-webkit-scrollbar-track {
  background: transparent;
}

.month-dropdown-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.month-option {
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748b;
  transition: all 0.15s ease;
  text-align: center;
}

.month-option:hover {
  background: #f1f5f9;
  color: #2196F3;
}

.month-option.selected {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(33, 150, 243, 0.1));
  color: #2196F3;
  font-weight: 600;
}

.month-option.dark {
  color: #94a3b8;
}

.month-option.dark:hover {
  background: #334155;
  color: #38bdf8;
}

.month-option.dark.selected {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(56, 189, 248, 0.1));
  color: #38bdf8;
}

.month-dropdown-content:has(.month-option.dark) {
  background: #1e293b;
  border-color: #475569;
}

.month-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  width: 36px;
  padding: 0;
  border: none;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.month-nav-btn:hover {
  color: #2196F3;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
}

.month-nav-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3);
}

.month-nav-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  stroke-width: 2;
}

.today-btn {
  height: 36px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: white;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.today-btn:hover {
  color: #2196F3;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
}

.today-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3);
}

.today-btn.dark {
  background: #1e293b;
  color: #f1f5f9;
}

.today-btn.dark:hover {
  color: #38bdf8;
  box-shadow: 0 2px 6px rgba(56, 189, 248, 0.2);
}

.month-nav-btn.dark {
  background: #1e293b;
  color: #94a3b8;
}

.month-nav-btn.dark:hover {
  color: #38bdf8;
  box-shadow: 0 2px 6px rgba(56, 189, 248, 0.2);
}

.date-picker-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 8px 0;
}

.date-picker-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-btn {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  gap: 2px;
}

.day-number {
  line-height: 1;
}

.stored-indicator {
  width: 10px;
  height: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stored-indicator svg {
  width: 10px;
  height: 10px;
  stroke: var(--success-color);
  stroke-width: 3;
}

.embedding-indicator {
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.embedding-indicator svg {
  width: 14px;
  height: 14px;
  stroke: #A855F7;
  stroke-width: 2;
  fill: none;
}

.day-btn:hover:not(.disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.day-btn.other-month {
  opacity: 0.4;
}

.day-btn.today {
  border-color: var(--accent-color);
  font-weight: 600;
}

.day-btn.selected {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%) !important;
  border-color: var(--accent-color) !important;
}

.day-btn.selected .day-number {
  color: var(--accent-color);
  font-weight: 600;
}

.day-btn.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.day-btn.stored,
.day-btn.has-embedding {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%);
}

.presets-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.date-picker-presets {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preset-btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  font-weight: 500;
  width: 100%;
}

.preset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.selected-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.selected-date {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--accent-color);
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--accent-color);
  text-align: center;
}

.date-picker-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
}

.action-btn {
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  width: 100%;
}

.cancel-btn {
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.cancel-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.confirm-btn {
  border: 1px solid var(--accent-color);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
  color: var(--accent-color);
  font-weight: 500;
}

.confirm-btn:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
  color: var(--accent-color);
  border-color: var(--accent-color);
}

@media (max-width: 768px) {
  .date-picker {
    padding: 16px;
    max-width: 95%;
  }

  .date-picker-content {
    flex-direction: column;
    gap: 16px;
  }

  .date-picker-right {
    width: 100%;
  }

  .date-picker-selector {
    flex-wrap: wrap;
    justify-content: center;
    padding: 8px;
  }

  .year-select-btn,
  .month-select-btn {
    height: 32px;
    min-width: 60px;
    padding: 0 10px;
    font-size: 0.85rem;
  }

  .month-nav-btn {
    height: 32px;
    width: 32px;
  }

  .month-nav-btn svg {
    width: 14px;
    height: 14px;
  }

  .today-btn {
    height: 32px;
    padding: 0 10px;
    font-size: 0.85rem;
  }

  .preset-btn {
    padding: 8px 12px;
    font-size: 0.85rem;
  }
}
</style>
