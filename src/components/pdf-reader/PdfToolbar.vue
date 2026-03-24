<template>
  <div class="pdf-toolbar">
    <div class="toolbar-left">
      <button 
        class="toolbar-btn" 
        :class="{ active: showSidebar }" 
        @click="$emit('toggle-sidebar')"
        title="Toggle Sidebar"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2"/>
          <line x1="9" y1="3" x2="9" y2="21" stroke-width="2"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-center">
      <div class="nav-controls">
        <button 
          class="toolbar-btn" 
          :disabled="!canGoPrev || loading" 
          @click="$emit('prev-page')"
          title="Previous Page"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="15 18 9 12 15 6" stroke-width="2"/>
          </svg>
        </button>

        <div class="page-input">
          <input
            type="number"
            :value="currentPage"
            :min="1"
            :max="totalPages"
            :disabled="loading"
            @change="handlePageInput"
          />
          <span class="page-total">/ {{ totalPages }}</span>
        </div>

        <button 
          class="toolbar-btn" 
          :disabled="!canGoNext || loading" 
          @click="$emit('next-page')"
          title="Next Page"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="9 18 15 12 9 6" stroke-width="2"/>
          </svg>
        </button>
      </div>

      <div class="divider"></div>

      <div class="zoom-controls">
        <button 
          class="toolbar-btn" 
          :disabled="loading" 
          @click="$emit('zoom-out')"
          title="Zoom Out"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8" stroke-width="2"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-width="2"/>
            <line x1="8" y1="11" x2="14" y2="11" stroke-width="2"/>
          </svg>
        </button>

        <div class="zoom-select">
          <select :value="zoomPercentage" @change="handleZoomSelect" :disabled="loading">
            <option v-for="level in displayZoomLevels" :key="level" :value="level">{{ level }}%</option>
          </select>
        </div>

        <button 
          class="toolbar-btn" 
          :disabled="loading" 
          @click="$emit('zoom-in')"
          title="Zoom In"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8" stroke-width="2"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-width="2"/>
            <line x1="11" y1="8" x2="11" y2="14" stroke-width="2"/>
            <line x1="8" y1="11" x2="14" y2="11" stroke-width="2"/>
          </svg>
        </button>

        <button 
          class="toolbar-btn" 
          :disabled="loading" 
          @click="$emit('fit-width')"
          title="Fit Width"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 3H3v18h18V3z" stroke-width="2"/>
            <path d="M3 9h18M3 15h18" stroke-width="1"/>
          </svg>
        </button>

        <button 
          class="toolbar-btn" 
          :disabled="loading" 
          @click="$emit('fit-page')"
          title="Fit Page"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="4" y="4" width="16" height="16" stroke-width="2"/>
            <rect x="7" y="7" width="10" height="10" stroke-width="1"/>
          </svg>
        </button>
      </div>

      <div class="divider"></div>

      <div class="view-controls">
        <button 
          class="toolbar-btn" 
          :class="{ active: viewMode === 'single' }"
          :disabled="loading"
          @click="$emit('toggle-view')"
          title="Single Page"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="5" y="3" width="14" height="18" stroke-width="2"/>
          </svg>
        </button>
        <button 
          class="toolbar-btn" 
          :class="{ active: viewMode === 'continuous' }"
          :disabled="loading"
          @click="$emit('toggle-view')"
          title="Continuous Scroll"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="5" y="2" width="14" height="6" stroke-width="2"/>
            <rect x="5" y="9" width="14" height="6" stroke-width="2"/>
            <rect x="5" y="16" width="14" height="6" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="toolbar-right">
      <div class="tool-controls">
        <button 
          class="toolbar-btn" 
          :class="{ active: currentTool === 'select' }"
          :disabled="loading"
          @click="$emit('set-tool', 'select')"
          title="Select Tool"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z" stroke-width="2"/>
          </svg>
        </button>
        <button 
          class="toolbar-btn" 
          :class="{ active: currentTool === 'highlight' }"
          :disabled="loading"
          @click="$emit('set-tool', 'highlight')"
          title="Highlight"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5z" stroke-width="2"/>
            <path d="M2 17l10 5 10-5" stroke-width="2"/>
            <path d="M2 12l10 5 10-5" stroke-width="2"/>
          </svg>
        </button>
        <button 
          class="toolbar-btn" 
          :class="{ active: currentTool === 'drawing' }"
          :disabled="loading"
          @click="$emit('set-tool', 'drawing')"
          title="Draw"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 19l7-7 3 3-7 7-3-3z" stroke-width="2"/>
            <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" stroke-width="2"/>
            <path d="M2 2l7.586 7.586" stroke-width="2"/>
          </svg>
        </button>
      </div>

      <div class="color-controls" v-if="currentTool === 'highlight' || currentTool === 'drawing'">
        <button 
          v-for="(colorValue, colorName) in highlightColors" 
          :key="colorName"
          class="color-btn"
          :class="{ active: currentColor === colorName }"
          :style="{ backgroundColor: colorValue }"
          :title="colorName"
          @click="$emit('set-color', colorName)"
        />
      </div>

      <div class="stroke-controls" v-if="currentTool === 'drawing'">
        <label class="stroke-label">Stroke:</label>
        <select :value="strokeWidth" @change="handleStrokeChange" class="stroke-select">
          <option v-for="width in strokeWidths" :key="width" :value="width">{{ width }}px</option>
        </select>
      </div>

      <button class="toolbar-btn close-btn" @click="$emit('close')" title="Close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18" stroke-width="2"/>
          <line x1="6" y1="6" x2="18" y2="18" stroke-width="2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ViewMode, HighlightColor, AnnotationType } from '@/types/pdf'

const props = defineProps<{
  zoom: number
  zoomPercentage: number
  viewMode: ViewMode
  currentPage: number
  totalPages: number
  loading: boolean
  canGoPrev: boolean
  canGoNext: boolean
  currentTool: AnnotationType | 'select' | null
  currentColor: HighlightColor
  strokeWidth: number
  showSidebar: boolean
}>()

const emit = defineEmits<{
  'zoom-in': []
  'zoom-out': []
  'fit-width': []
  'fit-page': []
  'set-zoom': [value: number]
  'toggle-view': []
  'prev-page': []
  'next-page': []
  'go-to-page': [page: number]
  'set-tool': [tool: AnnotationType | 'select' | null]
  'set-color': [color: HighlightColor]
  'set-stroke-width': [width: number]
  'toggle-sidebar': []
  'close': []
}>()

const zoomLevels = [25, 50, 75, 100, 125, 150, 200, 300, 400, 500]

const displayZoomLevels = computed(() => {
  if (!zoomLevels.includes(props.zoomPercentage)) {
    return [...zoomLevels, props.zoomPercentage].sort((a, b) => a - b)
  }
  return zoomLevels
})

const highlightColors: Record<HighlightColor, string> = {
  yellow: '#FFEB3B',
  green: '#4CAF50',
  blue: '#2196F3',
  pink: '#E91E63',
  purple: '#9C27B0',
}

const strokeWidths = [1, 2, 3, 4, 5, 8, 10]

function handlePageInput(event: Event) {
  const target = event.target as HTMLInputElement
  const page = parseInt(target.value, 10)
  if (page >= 1 && page <= props.totalPages) {
    emit('go-to-page', page)
  }
}

function handleZoomSelect(event: Event) {
  const target = event.target as HTMLSelectElement
  const percentage = parseInt(target.value, 10)
  emit('set-zoom', percentage / 100)
}

function handleStrokeChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const width = parseInt(target.value, 10)
  emit('set-stroke-width', width)
}
</script>

<style scoped>
.pdf-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  gap: 16px;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn.active {
  background: var(--accent-color);
  color: white;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-btn svg {
  width: 20px;
  height: 20px;
}

.close-btn:hover:not(:disabled) {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.nav-controls,
.zoom-controls,
.view-controls,
.tool-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-input {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-input input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  text-align: center;
}

.page-input input::-webkit-outer-spin-button,
.page-input input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.page-total {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.zoom-select select {
  padding: 6px 24px 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 8px;
}

.color-controls {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.color-btn {
  width: 24px;
  height: 24px;
  border: 2px solid transparent;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.color-btn:hover {
  transform: scale(1.1);
}

.color-btn.active {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-primary);
}

.stroke-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
}

.stroke-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stroke-select {
  padding: 4px 20px 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.75rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 4px center;
}
</style>
