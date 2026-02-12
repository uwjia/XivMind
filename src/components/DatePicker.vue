<template>
  <div class="date-picker-overlay" v-if="isOpen" @click="closeOutside">
    <div class="date-picker" @click.stop>
      <div class="date-picker-content">
        <div class="date-picker-left">
          <div class="date-picker-selector">
            <select class="year-select" :class="{ 'dark': isDark }" v-model="selectedYear" @change="updateDateFromSelect">
              <option v-for="year in yearRange" :key="year" :value="year">{{ year }}</option>
            </select>
            <button class="month-nav-btn" @click="prevMonth" title="Previous Month">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <select class="month-select" :class="{ 'dark': isDark }" v-model="selectedMonth" @change="updateDateFromSelect">
              <option v-for="(month, index) in months" :key="index" :value="index">{{ month }}</option>
            </select>
            <button class="month-nav-btn" @click="nextMonth" title="Next Month">
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
                'disabled': day.isDisabled
              }"
              :disabled="day.isDisabled"
              @click="tempSelectDate(day.date)"
            >
              {{ day.day }}
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

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

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
}

const yearRange = computed<number[]>(() => {
  const currentYear = new Date().getFullYear()
  const years: number[] = []
  for (let year = currentYear - 5; year <= currentYear + 5; year++) {
    years.push(year)
  }
  return years
})

const updateDateFromSelect = () => {
  currentDate.value = new Date(selectedYear.value, selectedMonth.value, 1)
  tempSelectedDate.value = new Date(selectedYear.value, selectedMonth.value, 1)
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
  
  for (let i = 0; i < firstDay; i++) {
    const day = daysInPrevMonth - firstDay + i + 1
    days.push({
      day,
      date: new Date(year, month - 1, day),
      isOtherMonth: true,
      isToday: false,
      isSelected: false,
      isDisabled: true,
      key: `prev-${i}`
    })
  }
  
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i)
    const isTodayDate = date.toDateString() === today.toDateString()
    const isSelectedDate = tempSelectedDate.value && typeof tempSelectedDate.value === 'object' && date.toDateString() === tempSelectedDate.value.toDateString() || false
    days.push({
      day: i,
      date,
      isOtherMonth: false,
      isToday: isTodayDate,
      isSelected: isSelectedDate,
      isDisabled: date > today,
      key: i
    })
  }
  
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      day: i,
      date: new Date(year, month + 1, i),
      isOtherMonth: true,
      isToday: false,
      isSelected: false,
      isDisabled: true,
      key: `next-${i}`
    })
  }
  
  return days
})

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

.year-select {
  padding: 8px 12px;
  border: none;
  background: white;
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
  min-width: 120px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.year-select:hover {
  background: white;
  color: #2196F3;
  box-shadow: 0 2px 5px rgba(33, 150, 243, 0.2);
}

.year-select:focus {
  outline: none;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.month-select {
  padding: 8px 12px;
  border: none;
  background: white;
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
  min-width: 120px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.month-select:hover {
  background: white;
  color: #2196F3;
  box-shadow: 0 2px 5px rgba(33, 150, 243, 0.2);
}

.month-select:focus {
  outline: none;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

/* Dark mode styles */
.year-select.dark,
.month-select.dark {
  background: #1e293b;
  color: #f1f5f9;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.year-select.dark:hover,
.month-select.dark:hover {
  background: #1e293b;
  color: #38bdf8;
  box-shadow: 0 2px 5px rgba(56, 189, 248, 0.3);
}

.year-select.dark:focus,
.month-select.dark:focus {
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.4);
}

.month-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}

.month-nav-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.month-nav-btn svg {
  width: 16px;
  height: 16px;
}

.today-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.today-btn:hover {
  background: var(--bg-secondary);
  color: var(--accent-color);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Dark mode styles for today button */
.today-btn.dark {
  background: #1e293b;
  border-color: #475569;
  color: #f1f5f9;
}

.today-btn.dark:hover {
  background: #334155;
  color: #38bdf8;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
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
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
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
  background: var(--accent-color) !important;
  color: white !important;
  border-color: var(--accent-color) !important;
}

.day-btn.disabled {
  opacity: 0.3;
  cursor: not-allowed;
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
  background: var(--accent-color);
  color: white;
}

.confirm-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
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

  .year-select,
  .month-select {
    min-width: 100px;
    padding: 6px 10px;
    font-size: 0.85rem;
  }

  .month-nav-btn {
    width: 28px;
    height: 28px;
  }

  .month-nav-btn svg {
    width: 14px;
    height: 14px;
  }

  .preset-btn {
    padding: 8px 12px;
    font-size: 0.85rem;
  }
}
</style>
