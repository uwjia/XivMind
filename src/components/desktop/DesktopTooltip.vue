<template>
  <div class="desktop-tooltip" :style="positionStyle">
    <div v-if="item.type === 'file' && task" class="tooltip-content">
      <div class="tooltip-header">
        <span class="tooltip-title">{{ truncateTitle(task.title) }}</span>
        <span class="tooltip-status" :class="task.status">{{ getStatusLabel(task.status) }}</span>
      </div>
      <div class="tooltip-body">
        <div class="tooltip-row">
          <span class="label">Paper ID:</span>
          <span class="value">{{ task.paper_id }}</span>
        </div>
        <div class="tooltip-row">
          <span class="label">Created:</span>
          <span class="value">{{ formatDate(task.created_at) }}</span>
        </div>
        <div v-if="task.file_size" class="tooltip-row">
          <span class="label">Size:</span>
          <span class="value">{{ formatFileSize(task.file_size) }}</span>
        </div>
        <div v-if="task.file_path" class="tooltip-row file-path">
          <span class="label">Path:</span>
          <span class="value" :title="task.file_path">{{ truncatePath(task.file_path) }}</span>
        </div>
      </div>
    </div>
    <div v-else-if="item.type === 'folder'" class="tooltip-content">
      <div class="tooltip-header">
        <span class="tooltip-title">{{ item.name }}</span>
        <span class="tooltip-status folder">Folder</span>
      </div>
      <div class="tooltip-body">
        <div class="tooltip-row">
          <span class="label">Items:</span>
          <span class="value">{{ childrenCount }}</span>
        </div>
        <div class="tooltip-row">
          <span class="label">Created:</span>
          <span class="value">{{ formatDate(item.createdAt) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDesktopStore } from '@/stores/desktop-store'
import type { DesktopItem } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'

const props = defineProps<{
  item: DesktopItem
  task?: DownloadTask
  position: { x: number; y: number }
}>()

const store = useDesktopStore()

const positionStyle = computed(() => ({
  left: `${props.position.x}px`,
  top: `${props.position.y}px`,
}))

const childrenCount = computed(() => {
  return store.items.filter(i => i.folderId === props.item.id).length
})

function truncateTitle(title: string, maxLength: number = 50): string {
  if (title.length <= maxLength) return title
  return title.substring(0, maxLength) + '...'
}

function truncatePath(path: string, maxLength: number = 40): string {
  if (path.length <= maxLength) return path
  return '...' + path.substring(path.length - maxLength)
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pending',
    downloading: 'Downloading',
    completed: 'Completed',
    failed: 'Failed',
  }
  return labels[status] || status
}
</script>

<style scoped>
.desktop-tooltip {
  position: absolute;
  z-index: 2000;
  pointer-events: none;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  max-width: 320px;
  overflow: hidden;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.tooltip-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  flex: 1;
}

.tooltip-status {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  flex-shrink: 0;
}

.tooltip-status.pending {
  background: rgba(158, 158, 158, 0.2);
  color: #9E9E9E;
}

.tooltip-status.downloading {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
}

.tooltip-status.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.tooltip-status.failed {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.tooltip-status.folder {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
}

.tooltip-body {
  padding: 8px 12px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 0.8rem;
}

.tooltip-row .label {
  color: var(--text-muted);
  flex-shrink: 0;
}

.tooltip-row .value {
  color: var(--text-secondary);
  text-align: right;
  margin-left: 12px;
  word-break: break-all;
}

.tooltip-row.file-path .value {
  font-family: monospace;
  font-size: 0.75rem;
}
</style>
