<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="conversation-history-panel"
      :class="{ dragging: isDragging }"
      :style="panelStyle"
    >
      <div class="panel-header" @mousedown="startDrag">
        <div class="header-left">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="header-icon">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="header-title">Conversations</span>
          <span class="conversation-count">{{ conversationStore.conversations.length }}</span>
        </div>
        <button class="header-btn close" @click.stop="$emit('close')" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="panel-search">
        <div class="search-input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" class="search-icon">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search conversations..."
            class="search-input"
            @input="handleSearch"
          />
        </div>
      </div>

      <div class="panel-content">
        <div class="conversation-list">
          <div
            v-for="(conversation, index) in sortedConversations"
            :key="conversation.session_id"
            class="conversation-item"
            :class="{ active: conversation.session_id === conversationStore.currentSessionId, pinned: conversation.pinned }"
            @click="selectConversation(conversation.session_id)"
          >
            <div class="conversation-index">
              <svg v-if="conversation.pinned" class="pin-icon" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                <path d="M16 3V5H8V3H16ZM16 7V13L18 15V17H13V22L12 23L11 22V17H6V15L8 13V7H16Z"/>
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="conversation-info">
              <div class="conversation-title-row">
                <span
                  class="conversation-title"
                  :contenteditable="editingId === conversation.session_id"
                  @blur="updateTitle(conversation.session_id, $event)"
                  @dblclick.stop="startEdit(conversation.session_id)"
                >{{ conversation.title }}</span>
              </div>
              <div class="conversation-meta">
                <span>{{ formatDate(conversation.created_at) }}</span>
                <span>{{ conversation.message_count }} messages</span>
              </div>
            </div>
            <div class="action-icons">
              <svg
                class="star-icon"
                :class="{ starred: conversation.starred }"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                width="16"
                height="16"
                @click.stop="toggleStar(conversation.session_id)"
                title="Star"
              >
                <polygon v-if="conversation.starred" points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" fill="currentColor"/>
                <polygon v-else points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              <svg
                class="pin-action-icon"
                :class="{ active: conversation.pinned }"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                width="16"
                height="16"
                @click.stop="togglePin(conversation.session_id)"
                title="Pin to top"
              >
                <path d="M16 3V5H8V3H16ZM16 7V13L18 15V17H13V22L12 23L11 22V17H6V15L8 13V7H16Z"/>
              </svg>
              <button
                class="delete-btn"
                @click.stop="confirmDelete(conversation.session_id)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showDeleteConfirm" class="delete-confirm-overlay">
        <div class="delete-confirm-dialog">
          <p>Are you sure you want to delete this conversation? This action cannot be undone.</p>
          <div class="dialog-buttons">
            <button class="btn-cancel" @click="cancelDelete">Cancel</button>
            <button class="btn-delete" @click="executeDelete">Delete</button>
          </div>
        </div>
      </div>

      <div class="resize-handle" @mousedown="startResize" />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useConversationStore } from '@/stores/conversation-store'
import { useConversation } from '@/composables/useConversation'

const props = defineProps<{
  visible: boolean
  triggerElement: HTMLElement | null
}>()

const emit = defineEmits<{
  close: []
  select: [sessionId: string]
}>()

const conversationStore = useConversationStore()

const {
  searchQuery,
  editingId,
  showDeleteConfirm,
  formatDate,
  handleSearch,
  startEdit,
  updateTitle,
  toggleStar,
  togglePin,
  confirmDelete,
  executeDelete,
  cancelDelete,
} = useConversation()

const sortedConversations = computed(() => {
  return [...conversationStore.conversations].sort((a, b) => {
    if (a.pinned && !b.pinned) return -1
    if (!a.pinned && b.pinned) return 1
    return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  })
})

const position = ref({ x: 100, y: 100 })
const size = ref({ width: 500, height: 400 })
const isDragging = ref(false)
const isResizing = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })

const minSize = { width: 300, height: 200 }
const maxSize = { width: 800, height: 600 }

const panelStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: `${size.value.width}px`,
  height: `${size.value.height}px`,
}))

function updatePosition() {
  if (props.triggerElement) {
    const rect = props.triggerElement.getBoundingClientRect()
    position.value = {
      x: rect.left,
      y: rect.bottom + 8,
    }
  }
}

watch(() => props.visible, (visible) => {
  if (visible) {
    nextTick(() => {
      updatePosition()
    })
  }
})

function startDrag(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.header-btn, .conversation-item, input, button, .delete-confirm-overlay, .resize-handle')) {
    return
  }
  isDragging.value = true
  dragOffset.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y,
  }
  e.preventDefault()
}

function onDrag(e: MouseEvent) {
  if (!isDragging.value) return
  position.value = {
    x: Math.max(0, Math.min(e.clientX - dragOffset.value.x, window.innerWidth - size.value.width)),
    y: Math.max(0, Math.min(e.clientY - dragOffset.value.y, window.innerHeight - size.value.height)),
  }
}

function stopDrag() {
  isDragging.value = false
}

function startResize(e: MouseEvent) {
  e.preventDefault()
  e.stopPropagation()
  isResizing.value = true
  resizeStart.value = {
    x: e.clientX,
    y: e.clientY,
    width: size.value.width,
    height: size.value.height,
  }
}

function onResize(e: MouseEvent) {
  if (!isResizing.value) return

  const deltaX = e.clientX - resizeStart.value.x
  const deltaY = e.clientY - resizeStart.value.y

  const newWidth = Math.max(
    minSize.width,
    Math.min(maxSize.width, resizeStart.value.width + deltaX)
  )
  const newHeight = Math.max(
    minSize.height,
    Math.min(maxSize.height, resizeStart.value.height + deltaY)
  )

  size.value = { width: newWidth, height: newHeight }
}

function stopResize() {
  isResizing.value = false
}

function selectConversation(sessionId: string) {
  emit('select', sessionId)
}

onMounted(() => {
  window.addEventListener('mousemove', (e) => {
    onDrag(e)
    onResize(e)
  })
  window.addEventListener('mouseup', () => {
    stopDrag()
    stopResize()
  })
})

onUnmounted(() => {
  window.removeEventListener('mousemove', (e) => {
    onDrag(e)
    onResize(e)
  })
  window.removeEventListener('mouseup', () => {
    stopDrag()
    stopResize()
  })
})
</script>

<style scoped>
.conversation-history-panel {
  position: fixed;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2d2d44);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.conversation-history-panel.dragging {
  user-select: none;
  cursor: move;
}

.panel-header {
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

.conversation-count {
  background: var(--accent-color);
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
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

.header-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.header-btn.close:hover {
  background: rgba(220, 53, 69, 0.15);
  color: var(--danger-color);
}

.header-btn svg {
  width: 16px;
  height: 16px;
}

.panel-search {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #2d2d44);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-secondary, #888);
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 32px;
  background: var(--bg-tertiary, #0f3460);
  border: 1px solid var(--border-color, #2d2d44);
  border-radius: 6px;
  color: var(--text-primary, #e0e0e0);
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-secondary, #888);
}

.search-input:focus {
  border-color: var(--accent-color, #00BCD4);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

.conversation-list {
  padding: 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: var(--hover-bg, rgba(255, 255, 255, 0.05));
}

.conversation-item.active {
  background: var(--active-bg, rgba(0, 188, 212, 0.1));
}

.conversation-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary, #0f3460);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary, #888);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.conversation-title {
  font-size: 14px;
  color: var(--text-primary, #e0e0e0);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-title[contenteditable="true"] {
  background: var(--bg-tertiary, #0f3460);
  padding: 2px 6px;
  border-radius: 4px;
  outline: none;
}

.star-icon {
  color: var(--text-secondary, #888);
  cursor: pointer;
  transition: color 0.2s;
}

.star-icon:hover,
.star-icon.starred {
  color: #ffc107;
}

.action-icons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pin-action-icon {
  color: var(--text-secondary, #888);
  cursor: pointer;
  transition: color 0.2s;
}

.pin-action-icon:hover,
.pin-action-icon.active {
  color: #00BCD4;
}

.pin-icon {
  color: #00BCD4;
}

.conversation-item.pinned {
  background: rgba(0, 188, 212, 0.05);
  border-left: 3px solid #00BCD4;
}

.conversation-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-tertiary, #666);
}

.delete-btn {
  background: none;
  border: none;
  color: var(--text-secondary, #888);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.delete-confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-confirm-dialog {
  background: var(--bg-secondary, #16213e);
  padding: 20px;
  border-radius: 8px;
  max-width: 300px;
}

.delete-confirm-dialog p {
  margin: 0 0 16px;
  color: var(--text-primary, #e0e0e0);
}

.dialog-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-delete {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: none;
}

.btn-cancel {
  background: var(--bg-tertiary, #0f3460);
  color: var(--text-primary, #e0e0e0);
}

.btn-delete {
  background: #f44336;
  color: white;
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
  border-right: 2px solid var(--text-muted, #666);
  border-bottom: 2px solid var(--text-muted, #666);
  opacity: 0.5;
}
</style>
