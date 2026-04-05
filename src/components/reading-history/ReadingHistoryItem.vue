<template>
  <div class="history-item" @click="$emit('click')">
    <div class="item-main">
      <div class="item-title">{{ item.title }}</div>
      <div class="item-meta">
        <span class="item-category">{{ item.primary_category }}</span>
        <span class="item-time">{{ formattedTime }}</span>
      </div>
    </div>
    <div class="item-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${item.progress_percent}%` }"></div>
      </div>
      <span class="progress-text">{{ item.current_page }}/{{ item.total_pages }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReadingHistoryItem } from '@/services/readingHistory'

const props = defineProps<{
  item: ReadingHistoryItem
}>()

defineEmits<{
  click: []
}>()

const formattedTime = computed(() => {
  const date = new Date(props.item.last_read_at)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
})
</script>

<style scoped>
.history-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  background: var(--bg-tertiary);
  transform: translateX(4px);
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-category {
  padding: 2px 6px;
  background: rgba(139, 92, 246, 0.15);
  color: var(--accent-color, #8b5cf6);
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.item-time {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.item-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.7rem;
  color: var(--text-secondary);
  min-width: 40px;
  text-align: right;
}
</style>
