<template>
  <div class="note-item" :class="{ selected }" :style="noteStyle">
    <div class="note-header">
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('toggle-select', note.id)"
        class="note-checkbox"
      />
      <span class="note-time">{{ formattedTime }}</span>
      <div class="note-actions">
        <button class="action-btn copy" @click="$emit('copy', note.id)" title="Copy">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
        </button>
        <button class="action-btn edit" @click="$emit('edit', note.id)" title="Edit">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="action-btn delete" @click="$emit('delete', note.id)" title="Delete">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="note-content">{{ note.content }}</div>
    <div v-if="note.tags.length > 0" class="note-tags">
      <span
        v-for="tag in note.tags"
        :key="tag"
        class="tag"
        @click="$emit('filter-tag', tag)"
      >{{ tag }}</span>
    </div>
    <div v-if="note.source" class="note-source">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
      {{ note.source }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Note } from '@/types/note'

const props = defineProps<{
  note: Note
  selected: boolean
}>()

defineEmits<{
  (e: 'toggle-select', id: string): void
  (e: 'edit', id: string): void
  (e: 'delete', id: string): void
  (e: 'copy', id: string): void
  (e: 'filter-tag', tag: string): void
}>()

const formattedTime = computed(() => {
  const date = new Date(props.note.createdAt)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
})

const noteStyle = computed(() => {
  if (props.note.color) {
    return {
      borderLeftColor: props.note.color,
      borderLeftWidth: '3px'
    }
  }
  return {}
})
</script>

<style scoped>
.note-item {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.note-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.note-item.selected {
  border-color: var(--accent-color);
  background: rgba(0, 188, 212, 0.1);
}

.note-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.note-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--accent-color);
}

.note-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  flex: 1;
}

.note-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.note-item:hover .note-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--bg-tertiary);
}

.action-btn.copy:hover {
  color: var(--accent-color);
}

.action-btn.edit:hover {
  color: #8B5CF6;
}

.action-btn.delete:hover {
  color: var(--danger-color);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.note-content {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: rgba(0, 188, 212, 0.15);
  color: var(--accent-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag:hover {
  background: rgba(0, 188, 212, 0.25);
}

.note-source {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 0.75rem;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-source svg {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}
</style>
