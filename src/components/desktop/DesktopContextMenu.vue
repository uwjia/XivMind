<template>
  <div 
    class="context-menu" 
    :style="menuStyle"
    @click.stop
  >
    <template v-if="target.type === 'desktop'">
      <button 
        v-if="!hasSelectedItems" 
        class="menu-item" 
        @click="$emit('create-folder')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M12 5v14M5 12h14" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>New Folder</span>
      </button>
      <template v-if="hasSelectedItems">
        <button class="menu-item" @click="handleOpen">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" stroke-width="2"/>
            <polyline points="15 3 21 3 21 9" stroke-width="2"/>
            <line x1="10" y1="14" x2="21" y2="3" stroke-width="2"/>
          </svg>
          <span>Open</span>
        </button>
        <button 
          v-if="isSingleFileSelected" 
          class="menu-item" 
          @click="openContainingFolder"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke-width="2"/>
          </svg>
          <span>Open Containing Folder</span>
        </button>
        <div class="menu-divider"></div>
        <button class="menu-item" @click="handleCut">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke-width="2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke-width="2"/>
          </svg>
          <span>Cut</span>
        </button>
        <button 
          class="menu-item" 
          @click="handleRename"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke-width="2"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke-width="2"/>
          </svg>
          <span>Rename Selected</span>
        </button>
        <button class="menu-item danger" @click="handleDelete">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6" stroke-width="2"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke-width="2"/>
          </svg>
          <span>Delete Selected</span>
        </button>
      </template>
      <template v-if="!hasSelectedItems && hasClipboard">
        <div class="menu-divider"></div>
        <button class="menu-item" @click="handlePaste">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>
          </svg>
          <span>Paste</span>
        </button>
      </template>
      <div class="menu-divider"></div>
      <button class="menu-item" @click="$emit('arrange')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="7" height="7" stroke-width="2"/>
          <rect x="14" y="3" width="7" height="7" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" stroke-width="2"/>
          <rect x="14" y="14" width="7" height="7" stroke-width="2"/>
        </svg>
        <span>Arrange Icons</span>
      </button>
    </template>
    
    <template v-else-if="target.type === 'file'">
      <button class="menu-item" @click="openFile">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" stroke-width="2"/>
          <polyline points="15 3 21 3 21 9" stroke-width="2"/>
          <line x1="10" y1="14" x2="21" y2="3" stroke-width="2"/>
        </svg>
        <span>Open File</span>
      </button>
      <button class="menu-item" @click="openContainingFolder">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke-width="2"/>
        </svg>
        <span>Open Containing Folder</span>
      </button>
      <div class="menu-divider"></div>
      <button class="menu-item" @click="handleCut">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke-width="2"/>
          <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke-width="2"/>
        </svg>
        <span>Cut</span>
      </button>
      <button class="menu-item" @click="handleRename">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke-width="2"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke-width="2"/>
        </svg>
        <span>Rename</span>
      </button>
      <button class="menu-item danger" @click="$emit('delete')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="3 6 5 6 21 6" stroke-width="2"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke-width="2"/>
        </svg>
        <span>Delete</span>
      </button>
    </template>
    
    <template v-else-if="target.type === 'folder'">
      <button class="menu-item" @click="openFolder">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke-width="2"/>
        </svg>
        <span>Open</span>
      </button>
      <div class="menu-divider"></div>
      <button class="menu-item" @click="handleCut">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke-width="2"/>
          <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke-width="2"/>
        </svg>
        <span>Cut</span>
      </button>
      <button class="menu-item" @click="handleRename">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke-width="2"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke-width="2"/>
        </svg>
        <span>Rename</span>
      </button>
      <button class="menu-item danger" @click="$emit('delete')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="3 6 5 6 21 6" stroke-width="2"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke-width="2"/>
        </svg>
        <span>Delete</span>
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { apiService } from '@/services/api'
import type { ContextMenuTarget, DesktopItem } from '@/types/desktop'

const props = defineProps<{
  position: { x: number; y: number }
  target: ContextMenuTarget
  selectedCount?: number
  selectedItems?: DesktopItem[]
  hasClipboard?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create-folder'): void
  (e: 'delete'): void
  (e: 'rename'): void
  (e: 'arrange'): void
  (e: 'open'): void
  (e: 'cut'): void
  (e: 'paste'): void
}>()

const hasSelectedItems = computed(() => (props.selectedCount || 0) > 0)

const isSingleFileSelected = computed(() => {
  return props.selectedCount === 1 && 
         props.selectedItems?.length === 1 && 
         props.selectedItems[0]?.type === 'file' &&
         !!props.selectedItems[0]?.taskId
})

const menuStyle = computed(() => ({
  left: `${props.position.x}px`,
  top: `${props.position.y}px`,
}))

function openFile() {
  if (props.target.item?.type === 'file' && props.target.item.taskId) {
    apiService.openDownloadFile(props.target.item.taskId)
  }
  emit('close')
}

function openContainingFolder() {
  if (props.target.item?.type === 'file' && props.target.item.taskId) {
    apiService.openContainingFolder(props.target.item.taskId)
  } else if (isSingleFileSelected.value && props.selectedItems?.[0]?.taskId) {
    apiService.openContainingFolder(props.selectedItems[0].taskId)
  }
  emit('close')
}

function openFolder() {
  emit('open')
  emit('close')
}

function handleRename() {
  emit('rename')
  emit('close')
}

function handleDelete() {
  emit('delete')
  emit('close')
}

function handleOpen() {
  emit('open')
  emit('close')
}

function handleCut() {
  emit('cut')
  emit('close')
}

function handlePaste() {
  emit('paste')
  emit('close')
}
</script>

<style scoped>
.context-menu {
  position: absolute;
  z-index: 3000;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 180px;
  padding: 4px 0;
  animation: fadeIn 0.1s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.menu-item:hover {
  background: var(--bg-secondary);
}

.menu-item.danger {
  color: #F44336;
}

.menu-item.danger:hover {
  background: rgba(244, 67, 54, 0.1);
}

.menu-item svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.menu-divider {
  height: 1px;
  background: var(--border-color);
  margin: 4px 8px;
}
</style>
