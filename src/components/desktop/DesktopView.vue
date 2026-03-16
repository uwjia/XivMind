<template>
  <div
    ref="desktopViewRef"
    class="desktop-view"
  >
    <div class="desktop-toolbar">
      <div class="breadcrumb-bar">
        <button 
          class="breadcrumb-btn root"
          @click="goToRoot"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </button>
        <template v-if="breadcrumb.length > 0">
          <template v-for="(folder, index) in breadcrumb" :key="folder.id">
            <span class="breadcrumb-separator">/</span>
            <button 
              class="breadcrumb-btn" 
              :class="{ active: index === breadcrumb.length - 1 }"
              :data-folder-id="folder.id"
              @click="openFolder(folder.id)"
            >
              {{ folder.name }}
            </button>
          </template>
        </template>
      </div>
      <div class="toolbar-spacer"></div>
      <button 
        class="toolbar-btn" 
        @click="exportLayout"
        title="Export Layout"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="17 8 12 3 7 8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="12" y1="3" x2="12" y2="15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <button 
        class="toolbar-btn" 
        @click="triggerImport"
        title="Import Layout"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="7 10 12 15 17 10" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="12" y1="15" x2="12" y2="3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <input 
        ref="importInputRef" 
        type="file" 
        accept=".json" 
        style="display: none" 
        @change="handleImport"
      />
      <button 
        class="grid-toggle-btn" 
        :class="{ active: store.showGrid }"
        @click="toggleGrid"
        :title="store.showGrid ? 'Hide Grid' : 'Show Grid'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="7" height="7" stroke-width="2"/>
          <rect x="14" y="3" width="7" height="7" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" stroke-width="2"/>
          <rect x="14" y="14" width="7" height="7" stroke-width="2"/>
        </svg>
      </button>
    </div>

    <div 
      ref="desktopRef"
      class="desktop-content" 
      :class="{ 'show-grid': store.showGrid }"
      :style="{
        '--grid-size': `${DESKTOP_CONFIG.GRID_SIZE}px`,
        '--icon-size': `${DESKTOP_CONFIG.ICON_SIZE}px`
      }"
      @mousedown="onDesktopMouseDown"
      @mousemove="onDesktopMouseMove"
      @mouseup="onDesktopMouseUp"
      @mouseleave="onDesktopMouseUp"
      @contextmenu.prevent="onContextMenu"
    >
      <div v-if="isSelecting && selectionBox" class="selection-box" :style="selectionBoxStyle"></div>

      <DesktopIcon
      v-for="item in store.rootItems"
      :key="item.id"
      :item="item"
      :is-selected="store.selectedIds.includes(item.id)"
      :is-dragging="draggedItemId === item.id"
      :is-renaming="renamingItemId === item.id"
      :task="getTaskForItem(item)"
      @mousedown="onItemMouseDown(item, $event)"
      @dblclick="onItemDoubleClick(item)"
      @mouseenter="onItemMouseEnter(item, $event)"
      @mouseleave="onItemMouseLeave"
      @contextmenu.prevent="onContextMenu($event, item)"
      @rename="finishRename"
      @rename-cancel="cancelRename"
    />

      <DesktopTooltip
        v-if="hoveredItem && !isDragging"
        :item="hoveredItem"
        :task="getTaskForItem(hoveredItem)"
        :position="tooltipPosition"
      />

      <DesktopContextMenu
        v-if="contextMenuVisible"
        :position="contextMenuPosition"
        :target="contextMenuTarget"
        :selected-count="savedSelectedIds.length"
        :selected-items="savedSelectedItems"
        :has-clipboard="store.hasClipboardItems()"
        @close="closeContextMenu"
        @create-folder="showCreateFolderDialog = true; closeContextMenu()"
        @delete="deleteSelectedItems"
        @rename="startRename"
        @arrange="autoArrange"
        @open="openSelectedItems"
        @cut="cutSelectedItems"
        @paste="pasteItems"
      />

      <CreateFolderDialog
        v-if="showCreateFolderDialog"
        @close="showCreateFolderDialog = false"
        @create="createFolder"
      />

      <div v-if="store.rootItems.length === 0" class="empty-desktop">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="3" y1="9" x2="21" y2="9"/>
          <line x1="9" y1="21" x2="9" y2="9"/>
        </svg>
        <p>No items on desktop</p>
        <span>Right-click to create a folder or download papers to add files</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted, ref } from 'vue'
import { useDesktopActions } from '@/composables/useDesktopActions'
import type { DownloadTask } from '@/services/download'
import { DESKTOP_CONFIG } from '@/config/desktop-config'
import DesktopIcon from './DesktopIcon.vue'
import DesktopTooltip from './DesktopTooltip.vue'
import DesktopContextMenu from './DesktopContextMenu.vue'
import CreateFolderDialog from './CreateFolderDialog.vue'

const props = defineProps<{
  tasks: DownloadTask[]
}>()

const getTasks = () => props.tasks

const actions = useDesktopActions(getTasks)

const {
  store,
  isDragging,
  draggedItemId,
  isSelecting,
  selectionBox,
  hoveredItem,
  tooltipPosition,
  contextMenuVisible,
  contextMenuPosition,
  contextMenuTarget,
  savedSelectedIds,
  savedSelectedItems,
  showCreateFolderDialog,
  renamingItemId,
  breadcrumb,
  getTaskForItem,
  onItemMouseDown,
  onItemDoubleClick,
  onItemMouseEnter,
  onItemMouseLeave,
  onDesktopMouseDown,
  onDesktopMouseMove,
  onDesktopMouseUp,
  onContextMenu,
  closeContextMenu,
  createFolder,
  deleteSelectedItems,
  openSelectedItems,
  cutSelectedItems,
  pasteItems,
  startRename,
  finishRename,
  cancelRename,
  openFolder,
  goToRoot,
  autoArrange,
  toggleGrid,
  exportLayout,
  importLayout,
} = actions

const desktopRef = actions.desktopRef
const desktopViewRef = ref<HTMLElement | null>(null)
const importInputRef = ref<HTMLInputElement | null>(null)

let resizeObserver: ResizeObserver | null = null

function triggerImport() {
  importInputRef.value?.click()
}

async function handleImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    importLayout(data)
  } catch (error) {
    console.error('Failed to import layout:', error)
  }
  
  input.value = ''
}

onMounted(() => {
  adjustToGrid()
  resizeObserver = new ResizeObserver(() => {
    adjustToGrid()
  })
  if (desktopViewRef.value) {
    resizeObserver.observe(desktopViewRef.value)
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})

function adjustToGrid() {
  if (!desktopViewRef.value) return
  const rect = desktopViewRef.value.getBoundingClientRect()
  const toolbarHeight = DESKTOP_CONFIG.TOOLBAR_HEIGHT
  const gridStep = DESKTOP_CONFIG.GRID_SIZE
  const borderSize = DESKTOP_CONFIG.BORDER_SIZE
  const availableHeight = rect.height - toolbarHeight - borderSize * 2
  const availableWidth = rect.width - borderSize * 2
  const adjustedHeight = Math.floor(availableHeight / gridStep) * gridStep + borderSize * 2
  const adjustedWidth = Math.floor(availableWidth / gridStep) * gridStep + borderSize * 2
  const contentEl = desktopViewRef.value.querySelector('.desktop-content') as HTMLElement
  if (contentEl) {
    contentEl.style.height = `${adjustedHeight}px`
    contentEl.style.width = `${adjustedWidth}px`
    contentEl.style.flex = 'none'
    contentEl.style.margin = 'auto'
  }
}

watch(() => props.tasks, (newTasks) => {
  store.initializeFromTasks(newTasks)
  void desktopRef
}, { deep: true })

const selectionBoxStyle = computed(() => {
  if (!selectionBox.value) return {}
  
  const minX = Math.min(selectionBox.value.startX, selectionBox.value.endX)
  const maxX = Math.max(selectionBox.value.startX, selectionBox.value.endX)
  const minY = Math.min(selectionBox.value.startY, selectionBox.value.endY)
  const maxY = Math.max(selectionBox.value.startY, selectionBox.value.endY)
  
  return {
    left: `${minX}px`,
    top: `${minY}px`,
    width: `${maxX - minX}px`,
    height: `${maxY - minY}px`,
  }
})
</script>

<style scoped>
.desktop-view {
  position: relative;
  width: 100%;
  height: calc(100vh - 200px);
  min-height: 400px;
  background: var(--bg-secondary);
  user-select: none;
  display: flex;
  flex-direction: column;
}

.desktop-content {
  position: relative;
  flex: 1;
  overflow: hidden;
  background: var(--bg-secondary);
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(0, 188, 212, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(156, 39, 176, 0.05) 0%, transparent 50%);
  border: 2px solid transparent;
  box-sizing: border-box;
  --grid-size: 80px;
}

.desktop-content.show-grid::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(128, 128, 128, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(128, 128, 128, 0.2) 1px, transparent 1px);
  background-size: var(--grid-size) var(--grid-size);
  background-position: 0 0;
  pointer-events: none;
  z-index: 0;
}

.desktop-content.show-grid {
  border-color: rgba(33, 150, 243, 0.5);
}

.breadcrumb-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.breadcrumb-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.breadcrumb-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.breadcrumb-btn.active {
  color: var(--accent-color);
  font-weight: 500;
}

.breadcrumb-btn svg {
  width: 16px;
  height: 16px;
}

.breadcrumb-separator {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.selection-box {
  position: absolute;
  background: rgba(0, 188, 212, 0.1);
  border: 1px solid rgba(0, 188, 212, 0.5);
  border-radius: 2px;
  pointer-events: none;
  z-index: 1000;
}

.empty-desktop {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-muted);
}

.empty-desktop svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-desktop p {
  font-size: 1.1rem;
  margin: 0 0 8px 0;
}

.empty-desktop span {
  font-size: 0.85rem;
}

.desktop-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding-right: 8px;
}

.toolbar-spacer {
  flex: 1;
}

.grid-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.grid-toggle-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.grid-toggle-btn.active {
  color: var(--accent-color);
}

.grid-toggle-btn svg {
  width: 18px;
  height: 18px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn svg {
  width: 18px;
  height: 18px;
}
</style>
