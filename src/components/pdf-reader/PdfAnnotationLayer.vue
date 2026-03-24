<template>
  <div 
    class="annotation-layer"
    :class="{ 
      'selecting': currentTool === 'select',
      'drawing-mode': currentTool === 'drawing'
    }"
    ref="layerRef"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
  >
    <div
      v-for="annotation in annotations"
      :key="annotation.id"
      class="annotation"
      :class="[annotation.type, { selected: selectedId === annotation.id }]"
      :style="getAnnotationStyle(annotation)"
      @click.stop="selectAnnotation(annotation)"
      @contextmenu.prevent="showContextMenu($event, annotation)"
      @mouseenter="showTooltip($event, annotation)"
      @mouseleave="scheduleHideTooltip"
    >
      <div v-if="annotation.type === 'comment'" class="comment-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2z"/>
        </svg>
      </div>
      <svg v-if="annotation.type === 'drawing'" class="drawing-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <path :d="getDrawingPath(annotation)" :stroke="annotation.color" :stroke-width="getAnnotationStrokeWidth(annotation)" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <div
      v-if="tooltipVisible && tooltipAnnotation"
      class="comment-tooltip"
      :style="tooltipStyle"
      @mouseenter="cancelHideTooltip"
      @mouseleave="hideTooltip"
    >
      <div class="tooltip-header">
        <span class="tooltip-type">Comment</span>
        <span class="tooltip-date">{{ formatDate(tooltipAnnotation.created_at) }}</span>
      </div>
      <div class="tooltip-content">{{ tooltipAnnotation.content || 'No content' }}</div>
      <div class="tooltip-actions">
        <button class="tooltip-btn edit" @click="startEditComment">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Edit
        </button>
        <button class="tooltip-btn delete" @click="deleteFromTooltip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          Delete
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="showEditDialog"
        class="edit-dialog-overlay"
        @click.self="cancelEdit"
      >
        <div class="edit-dialog">
          <h3 class="edit-dialog-title">Edit Comment</h3>
          <textarea
            v-model="editContent"
            class="edit-textarea"
            placeholder="Enter your comment..."
            rows="4"
          ></textarea>
          <div class="edit-dialog-actions">
            <button class="edit-btn cancel" @click="cancelEdit">Cancel</button>
            <button class="edit-btn save" @click="saveEdit">Save</button>
          </div>
        </div>
      </div>
    </Teleport>

    <div
      v-if="isDrawing && drawingPath.length > 0"
      class="drawing-preview"
    >
      <svg width="100%" height="100%">
        <path :d="getPathD(drawingPath)" fill="none" :stroke="drawingColor" :stroke-width="strokeWidth" stroke-linecap="round"/>
      </svg>
    </div>

    <ConfirmDialog
      :visible="showDeleteConfirm"
      title="Delete Annotation"
      message="Are you sure you want to delete this annotation?"
      type="danger"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { usePdfAnnotationLayer } from '@/composables/pdf/usePdfAnnotationLayer'
import type { PdfAnnotation, AnnotationPosition, AnnotationType, HighlightColor } from '@/types/pdf'

const props = defineProps<{
  pageNumber: number
  annotations: PdfAnnotation[]
  zoom: number
  currentTool: AnnotationType | 'select' | null
  currentColor: HighlightColor
  strokeWidth: number
}>()

const emit = defineEmits<{
  'annotation-create': [data: { type: AnnotationType; position: AnnotationPosition; path?: { x: number; y: number }[]; color?: string; stroke_width?: number }]
  'text-select': [data: { text: string; position: AnnotationPosition; clientX: number; clientY: number }]
  'annotation-select': [annotation: PdfAnnotation | null]
  'annotation-delete': [id: string]
  'annotation-update': [data: { id: string; content: string }]
}>()

const layerRef = ref<HTMLDivElement | null>(null)

const {
  selectedId,
  isDrawing,
  drawingPath,
  drawingColor,
  showDeleteConfirm,
  tooltipVisible,
  tooltipAnnotation,
  tooltipStyle,
  showEditDialog,
  editContent,
  getAnnotationStyle,
  getDrawingPath,
  getAnnotationStrokeWidth,
  selectAnnotation,
  handleMouseDown,
  handleMouseMove,
  handleMouseUp,
  getPathD,
  showContextMenu,
  confirmDelete,
  cancelDelete,
  showTooltip,
  scheduleHideTooltip,
  cancelHideTooltip,
  hideTooltip,
  formatDate,
  startEditComment,
  cancelEdit,
  saveEdit,
  deleteFromTooltip,
} = usePdfAnnotationLayer(layerRef, props, emit)
</script>

<style scoped>
.annotation-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transform-origin: 0 0;
  overflow: visible;
}

.annotation-layer.selecting {
  pointer-events: none;
}

.annotation-layer.drawing-mode {
  pointer-events: auto;
  cursor: crosshair;
}

.text-layer.selecting ~ .annotation-layer section,
.annotation-layer.selecting section {
  pointer-events: none;
}

.annotation-layer.selecting .annotation {
  pointer-events: auto;
}

.annotation {
  position: absolute;
  pointer-events: auto;
  cursor: pointer;
  transition: opacity 0.2s;
}

.annotation.highlight {
  border-radius: 2px;
}

.annotation.underline {
  background: transparent !important;
  border-bottom: 2px solid;
}

.annotation.strikeout {
  text-decoration: line-through;
  text-decoration-color: currentColor;
}

.annotation.drawing {
  pointer-events: auto;
  overflow: visible;
}

.drawing-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.drawing-svg path {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.annotation.comment {
  background: #FFC107;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.comment-icon {
  width: 60%;
  height: 60%;
  color: white;
}

.comment-icon svg {
  width: 100%;
  height: 100%;
}

.annotation.selected {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

.drawing-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.drawing-preview svg {
  width: 100%;
  height: 100%;
}

.comment-tooltip {
  position: fixed;
  z-index: 1000;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px 16px;
  max-width: 400px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  pointer-events: auto;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.tooltip-type {
  font-weight: 600;
  color: var(--accent-color);
  font-size: 0.85rem;
}

.tooltip-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.tooltip-content {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
  margin-bottom: 12px;
}

.tooltip-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.tooltip-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tooltip-btn svg {
  width: 14px;
  height: 14px;
}

.tooltip-btn.edit {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tooltip-btn.edit:hover {
  background: var(--accent-color);
  color: white;
}

.tooltip-btn.delete {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.tooltip-btn.delete:hover {
  background: #F44336;
  color: white;
}
</style>

<style>
.edit-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.edit-dialog {
  background: var(--bg-primary, #ffffff);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.edit-dialog-title {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary, #333333);
}

.edit-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-primary, #333333);
  box-sizing: border-box;
}

.edit-textarea:focus {
  outline: none;
  border-color: var(--accent-color, #1976d2);
}

.edit-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.edit-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn.cancel {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary, #666666);
}

.edit-btn.cancel:hover {
  background: var(--bg-primary, #ffffff);
  color: var(--text-primary, #333333);
}

.edit-btn.save {
  background: var(--accent-color, #1976d2);
  color: white;
}

.edit-btn.save:hover {
  opacity: 0.9;
}
</style>
