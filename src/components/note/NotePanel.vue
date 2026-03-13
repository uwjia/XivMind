<template>
  <Teleport to="body">
    <Transition name="panel">
      <div
        v-if="isVisible"
        class="note-panel"
        :class="{ minimized: isMinimized, dragging: isDragging }"
        :style="panelStyle"
      >
        <div class="note-panel-header" @mousedown="handleMouseDown">
          <div class="header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="header-icon">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            <span class="header-title">Notes</span>
            <span class="note-count">{{ noteStore.notes.length }}</span>
          </div>
          <div class="header-actions">
            <button class="header-btn add" @click.stop="startAddNote" title="Add note">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
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
          <NoteToolbar
            :search-query="noteStore.searchQuery"
            :filter-tag="noteStore.filterTag"
            :all-tags="noteStore.allTags"
            :selected-count="noteStore.selectedIds.length"
            @add="startAddNote"
            @search="setSearchQuery"
            @filter="setFilter"
            @copy-selected="handleCopySelected"
            @delete-selected="handleDeleteSelected"
            @export="showExportModal = true"
          />

          <div class="note-panel-body">
            <NoteEditor
              v-if="isEditing"
              :initial-content="editingContent"
              :initial-tags="editingTags"
              :is-editing="!!editingNoteId"
              @save="handleSaveNote"
              @cancel="cancelEdit"
            />

            <TransitionGroup name="note-list" tag="div">
              <NoteItem
                v-for="note in noteStore.filteredNotes"
                :key="note.id"
                :note="note"
                :selected="noteStore.selectedIds.includes(note.id)"
                @toggle-select="toggleSelection"
                @edit="startEditNote"
                @delete="handleDeleteNote"
                @copy="handleCopyNote"
                @filter-tag="setFilter"
              />
            </TransitionGroup>

            <div v-if="noteStore.filteredNotes.length === 0 && !isEditing" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <p>No notes yet</p>
              <button class="empty-add-btn" @click="startAddNote">Add your first note</button>
            </div>
          </div>

          <div v-if="noteStore.selectedIds.length > 0" class="note-panel-footer">
            <span class="selection-info">{{ noteStore.selectedIds.length }} selected</span>
            <div class="footer-actions">
              <button class="footer-btn" @click="toggleSelectAll">{{ noteStore.isAllSelected ? 'Deselect all' : 'Select all' }}</button>
              <button class="footer-btn" @click="clearSelection">Cancel</button>
              <button class="footer-btn primary" @click="handleCopySelected">Copy</button>
              <button class="footer-btn danger" @click="handleDeleteSelected">Delete</button>
            </div>
          </div>

          <div
            class="resize-handle"
            @mousedown="handleResizeMouseDown"
          />
        </template>
      </div>
    </Transition>

    <NoteExportModal
      :visible="showExportModal"
      :notes="noteStore.notes"
      @close="showExportModal = false"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useNoteStore } from '@/stores/note-store'
import { useDraggable, useResizable, useNotePanelKeyboard, useNotePanelResize } from '@/composables/note/useNotePanel'
import { useNoteEditor } from '@/composables/note/useNoteEditor'
import { useNoteActions } from '@/composables/note/useNoteActions'
import { useNoteSelection } from '@/composables/note/useNoteSelection'
import NoteItem from '@/components/note/NoteItem.vue'
import NoteEditor from '@/components/note/NoteEditor.vue'
import NoteToolbar from '@/components/note/NoteToolbar.vue'
import NoteExportModal from '@/components/note/NoteExportModal.vue'

const noteStore = useNoteStore()
const showExportModal = ref(false)

const {
  position,
  isDragging,
  handleMouseDown
} = useDraggable({
  initialPosition: noteStore.position,
  onPositionChange: (pos) => noteStore.updatePosition(pos.x, pos.y)
})

const {
  size,
  handleResizeMouseDown
} = useResizable({
  initialSize: noteStore.size,
  onSizeChange: (s) => noteStore.updateSize(s.width, s.height)
})

const {
  isEditing,
  editingNoteId,
  editingContent,
  editingTags,
  startAdd: startAddNote,
  startEdit: startEditNote,
  cancel: cancelEdit,
  save: handleSaveNote
} = useNoteEditor()

const {
  deleteNote: handleDeleteNote,
  deleteSelected: handleDeleteSelected,
  copyNote: handleCopyNote,
  copySelected: handleCopySelected,
  setSearchQuery,
  setFilter
} = useNoteActions()

const {
  toggleSelection,
  toggleSelectAll,
  clearSelection
} = useNoteSelection()

useNotePanelKeyboard({
  isVisible: computed(() => noteStore.isVisible),
  isEditing,
  onCancelEdit: cancelEdit,
  onClearSelection: clearSelection,
  hasSelection: () => noteStore.selectedIds.length > 0,
  onTogglePanel: () => noteStore.togglePanel()
})

useNotePanelResize({
  position,
  size,
  onPositionChange: (x, y) => noteStore.updatePosition(x, y),
  onResetPosition: () => noteStore.resetToDefaultPosition(),
  hasUserMovedPanel: () => noteStore.hasUserMovedPanel,
  isVisible: computed(() => noteStore.isVisible)
})

watch(() => noteStore.position, (newPos) => {
  position.value = { ...newPos }
}, { deep: true })

watch(() => noteStore.size, (newSize) => {
  size.value = { ...newSize }
}, { deep: true })

watch(() => noteStore.isVisible, async (visible) => {
  if (visible && !noteStore.hasUserMovedPanel) {
    await nextTick()
    noteStore.resetToDefaultPosition()
    position.value = { ...noteStore.position }
  }
})

const isVisible = computed(() => noteStore.isVisible)
const isMinimized = computed(() => noteStore.isMinimized)

const panelStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: `${size.value.width}px`,
  height: isMinimized.value ? 'auto' : `${size.value.height}px`
}))

const toggleMinimize = () => {
  noteStore.toggleMinimize()
}

const hidePanel = () => {
  noteStore.hidePanel()
}

</script>

<style scoped>
.note-panel {
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

.note-panel.dragging {
  user-select: none;
  cursor: move;
}

.note-panel.minimized {
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

.note-panel-header {
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

.note-count {
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

.header-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.header-btn.add {
  background: rgba(0, 188, 212, 0.15);
  color: var(--accent-color);
}

.header-btn.add:hover {
  background: rgba(0, 188, 212, 0.25);
}

.header-btn.close:hover {
  background: rgba(220, 53, 69, 0.15);
  color: var(--danger-color);
}

.header-btn svg {
  width: 16px;
  height: 16px;
}

.note-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.note-list-enter-active,
.note-list-leave-active {
  transition: all 0.3s ease;
}

.note-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.note-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 16px;
  font-size: 0.9rem;
}

.empty-add-btn {
  padding: 8px 16px;
  border: none;
  background: var(--accent-color);
  color: white;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.empty-add-btn:hover {
  background: var(--accent-hover);
}

.note-panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.selection-info {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.footer-actions {
  display: flex;
  gap: 6px;
}

.footer-btn {
  padding: 4px 10px;
  border: none;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.footer-btn:hover {
  background: var(--border-color);
}

.footer-btn.primary {
  background: var(--accent-color);
  color: white;
}

.footer-btn.primary:hover {
  background: var(--accent-hover);
}

.footer-btn.danger {
  color: var(--danger-color);
}

.footer-btn.danger:hover {
  background: rgba(220, 53, 69, 0.15);
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
