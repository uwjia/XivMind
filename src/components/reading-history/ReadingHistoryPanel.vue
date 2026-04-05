<template>
  <Teleport to="body">
    <Transition name="panel">
      <div
        v-if="isVisible"
        class="history-panel"
        :class="{ minimized: isMinimized, dragging: isDragging }"
        :style="panelStyle"
      >
        <div class="history-panel-header" @mousedown="handleMouseDown">
          <div class="header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="header-icon">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span class="header-title">Recent Reading</span>
            <span class="history-count">{{ historyStore.totalCount }}</span>
          </div>
          <div class="header-actions">
            <button class="header-btn refresh" @click.stop="refreshHistory" title="Refresh" :disabled="isLoading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" :class="{ spinning: isLoading }">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>
            <button class="header-btn" @click.stop="toggleMinimize" title="Minimize">
              <svg v-if="!isMinimized" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="18 15 12 9 6 15"/>
              </svg>
            </button>
            <button class="header-btn close" @click.stop="hidePanel" title="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <template v-if="!isMinimized">
          <div class="history-panel-body">
            <div v-if="isLoading" class="loading-state">
              <svg class="loading-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              <span>Loading...</span>
            </div>

            <div v-else-if="error" class="error-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{{ error }}</span>
              <button @click="refreshHistory">Retry</button>
            </div>

            <TransitionGroup v-else-if="history.length > 0" name="history-list" tag="div" class="history-list">
              <ReadingHistoryItem
                v-for="item in history"
                :key="item.paper_id"
                :item="item"
                @click="handleItemClick(item)"
              />
            </TransitionGroup>

            <div v-else class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <p>No reading history yet</p>
              <span>Start reading papers to see your history here</span>
            </div>
          </div>

          <div class="resize-handle" @mousedown="handleResizeMouseDown" />
        </template>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useReadingHistoryStore } from '@/stores/reading-history-store'
import ReadingHistoryItem from './ReadingHistoryItem.vue'
import type { ReadingHistoryItem as ReadingHistoryItemType } from '@/services/readingHistory'

const router = useRouter()
const historyStore = useReadingHistoryStore()

const position = ref({ ...historyStore.position })
const size = ref({ ...historyStore.size })
const isDragging = ref(false)

const isVisible = computed(() => historyStore.isVisible)
const isMinimized = computed(() => historyStore.isMinimized)
const history = computed(() => historyStore.history)
const isLoading = computed(() => historyStore.isLoading)
const error = computed(() => historyStore.error)

const panelStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: `${size.value.width}px`,
  height: isMinimized.value ? 'auto' : `${size.value.height}px`
}))

const handleMouseDown = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.header-actions')) return
  
  isDragging.value = true
  const startX = e.clientX - position.value.x
  const startY = e.clientY - position.value.y

  const handleMouseMove = (moveEvent: MouseEvent) => {
    position.value = {
      x: Math.max(0, Math.min(window.innerWidth - size.value.width, moveEvent.clientX - startX)),
      y: Math.max(0, Math.min(window.innerHeight - 100, moveEvent.clientY - startY))
    }
  }

  const handleMouseUp = () => {
    isDragging.value = false
    historyStore.updatePosition(position.value.x, position.value.y)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleResizeMouseDown = (e: MouseEvent) => {
  e.preventDefault()
  const startX = e.clientX
  const startY = e.clientY
  const startWidth = size.value.width
  const startHeight = size.value.height

  const handleMouseMove = (moveEvent: MouseEvent) => {
    size.value = {
      width: Math.max(280, startWidth + moveEvent.clientX - startX),
      height: Math.max(200, startHeight + moveEvent.clientY - startY)
    }
  }

  const handleMouseUp = () => {
    historyStore.updateSize(size.value.width, size.value.height)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const toggleMinimize = () => {
  historyStore.toggleMinimize()
}

const hidePanel = () => {
  historyStore.hidePanel()
}

const refreshHistory = () => {
  historyStore.fetchHistory()
}

const handleItemClick = (item: ReadingHistoryItemType) => {
  // router.push({ name: 'PaperDetail', params: { id: item.paper_id } })
  router.push({ name: 'PdfReader', params: { paperId: item.paper_id } })
  hidePanel()
}

watch(() => historyStore.position, (newPos) => {
  position.value = { ...newPos }
}, { deep: true })

watch(() => historyStore.size, (newSize) => {
  size.value = { ...newSize }
}, { deep: true })

watch(() => historyStore.isVisible, async (visible) => {
  if (visible && !historyStore.hasUserMovedPanel) {
    await nextTick()
    historyStore.resetToDefaultPosition()
    position.value = { ...historyStore.position }
  }
})
</script>

<style scoped>
.history-panel {
  position: fixed;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-panel.dragging {
  user-select: none;
  cursor: move;
}

.history-panel.minimized {
  height: auto !important;
}

.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.history-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  cursor: move;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  width: 18px;
  height: 18px;
  color: var(--accent-color);
}

.header-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.history-count {
  background: var(--accent-color);
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.header-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.header-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-btn.refresh:hover:not(:disabled) {
  background: rgba(0, 188, 212, 0.15);
  color: var(--accent-color);
}

.header-btn.close:hover {
  background: rgba(220, 53, 69, 0.15);
  color: var(--danger-color);
}

.header-btn svg {
  width: 16px;
  height: 16px;
}

.header-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.history-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-list-enter-active,
.history-list-leave-active {
  transition: all 0.3s ease;
}

.history-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.history-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
  text-align: center;
}

.loading-state svg,
.error-state svg,
.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

.loading-state span,
.error-state span {
  font-size: 0.9rem;
}

.error-state button {
  margin-top: 12px;
  padding: 8px 16px;
  border: none;
  background: var(--accent-color);
  color: white;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-state button:hover {
  background: var(--accent-hover);
}

.empty-state p {
  margin: 0 0 4px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.empty-state span {
  font-size: 0.8rem;
}

.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  cursor: se-resize;
}

.resize-handle::before {
  content: '';
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 8px;
  height: 8px;
  border-right: 2px solid var(--text-muted);
  border-bottom: 2px solid var(--text-muted);
  opacity: 0.5;
}
</style>
