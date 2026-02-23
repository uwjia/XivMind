<template>
  <Teleport to="body">
    <Transition name="tooltip-fade">
      <div
        v-if="visible && (dateInfo || embeddingInfo)"
        class="day-tooltip"
        :style="tooltipStyle"
        @click.stop
      >
        <div class="tooltip-header">
          <span class="tooltip-date">{{ date }}</span>
          <button v-if="closable" class="tooltip-close" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="tooltip-body">
          <div v-if="dateInfo" class="tooltip-section">
            <div class="section-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Papers Stored</span>
            </div>
            <div class="section-content">
              <div class="info-row">
                <span class="info-label">Count:</span>
                <span class="info-value">{{ dateInfo.count }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Fetched:</span>
                <span class="info-value">{{ formatDate(dateInfo.fetched_at) }}</span>
              </div>
            </div>
          </div>
          <div v-if="embeddingInfo" class="tooltip-section">
            <div class="section-header embedding">
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
              <span>Embeddings</span>
            </div>
            <div class="section-content">
              <div class="info-row">
                <span class="info-label">Count:</span>
                <span class="info-value">{{ embeddingInfo.count }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Generated:</span>
                <span class="info-value">{{ formatDate(embeddingInfo.generated_at) }}</span>
              </div>
              <div v-if="embeddingInfo.model_name" class="info-row">
                <span class="info-label">Model:</span>
                <span class="info-value">{{ embeddingInfo.model_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface DateInfo {
  count: number
  fetched_at: string
}

interface EmbeddingInfo {
  count: number
  generated_at: string
  model_name?: string
}

const props = withDefaults(defineProps<{
  visible: boolean
  date: string
  dateInfo?: DateInfo | null
  embeddingInfo?: EmbeddingInfo | null
  position?: { x: number; y: number }
  closable?: boolean
}>(), {
  closable: true,
  position: () => ({ x: 0, y: 0 })
})

defineEmits<{
  (e: 'close'): void
}>()

const tooltipStyle = computed(() => ({
  left: `${props.position.x}px`,
  top: `${props.position.y}px`
}))

function formatDate(datetime: string): string {
  if (!datetime) return ''
  try {
    const date = new Date(datetime)
    return date.toLocaleString()
  } catch {
    return datetime
  }
}
</script>

<style scoped>
.day-tooltip {
  position: fixed;
  z-index: 10000;
  min-width: 220px;
  max-width: 320px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transform: translate(10px, 10px);
  overflow: hidden;
}

.tooltip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-bottom: 1px solid var(--border-color);
}

.tooltip-date {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.tooltip-close {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.tooltip-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.tooltip-close svg {
  width: 14px;
  height: 14px;
}

.tooltip-body {
  padding: 12px 16px;
}

.tooltip-section {
  margin-bottom: 12px;
}

.tooltip-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--success-color);
}

.section-header svg {
  width: 16px;
  height: 16px;
}

.section-header.embedding {
  color: #9C27B0;
}

.section-content {
  padding-left: 24px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 0.8rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: var(--text-secondary);
  min-width: 70px;
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translate(5px, 5px);
}
</style>
