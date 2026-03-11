<template>
  <div class="output-edit-dialog" @click.self="$emit('close')">
    <div class="dialog-content">
      <div class="dialog-header">
        <h3>Output Preview</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      <div class="dialog-body">
        <div class="editor-panel" :style="{ width: leftWidth + '%' }">
          <div class="panel-header">Markdown</div>
          <textarea
            v-model="content"
            placeholder="No output content"
            readonly
          ></textarea>
        </div>
        <div 
          class="resize-handle"
          :class="{ dragging: isResizing }"
          @mousedown="startResize"
        ></div>
        <div class="preview-panel" :style="{ width: (100 - leftWidth) + '%' }">
          <div class="panel-header">Preview</div>
          <div class="markdown-preview" v-html="renderedMarkdown"></div>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="btn btn-secondary" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const content = ref(props.modelValue)
const leftWidth = ref(50)
const isResizing = ref(false)

watch(() => props.modelValue, (val) => {
  content.value = val
})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
})

const renderedMarkdown = computed(() => {
  if (!content.value) {
    return '<p class="empty-hint">No content to preview</p>'
  }
  return md.render(content.value)
})

function startResize(e: MouseEvent) {
  isResizing.value = true
  const startX = e.clientX
  const startLeftWidth = leftWidth.value
  const containerWidth = (e.target as HTMLElement).parentElement?.clientWidth || 0
  
  const onMouseMove = (e: MouseEvent) => {
    const delta = e.clientX - startX
    const deltaPercent = (delta / containerWidth) * 100
    const newWidth = Math.min(80, Math.max(20, startLeftWidth + deltaPercent))
    leftWidth.value = newWidth
  }
  
  const onMouseUp = () => {
    isResizing.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}
</script>

<style scoped>
.output-edit-dialog {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.dialog-content {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 1000px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text-primary);
}

.dialog-body {
  flex: 1;
  display: flex;
  padding: 16px;
  overflow: hidden;
  gap: 0;
}

.editor-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.resize-handle {
  width: 8px;
  cursor: ew-resize;
  background: transparent;
  transition: background 0.2s;
  flex-shrink: 0;
  position: relative;
}

.resize-handle::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  background: var(--border-color);
  transition: background 0.2s;
}

.resize-handle:hover::before,
.resize-handle.dragging::before {
  background: var(--primary-color);
}

.panel-header {
  padding: 8px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-secondary);
  border-radius: 8px 8px 0 0;
  border: 1px solid var(--border-color);
  border-bottom: none;
}

.editor-panel textarea {
  flex: 1;
  width: 100%;
  resize: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0 0 0 8px;
  padding: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.editor-panel .panel-header {
  border-radius: 8px 0 0 0;
}

.preview-panel .panel-header {
  border-radius: 0 8px 0 0;
}

.markdown-preview {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0 0 8px 0;
  padding: 16px;
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text-primary);
}

.markdown-preview::-webkit-scrollbar {
  width: 6px;
}

.markdown-preview::-webkit-scrollbar-track {
  background: transparent;
}

.markdown-preview::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.markdown-preview::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4),
.markdown-preview :deep(h5),
.markdown-preview :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-preview :deep(h1:first-child),
.markdown-preview :deep(h2:first-child),
.markdown-preview :deep(h3:first-child) {
  margin-top: 0;
}

.markdown-preview :deep(p) {
  margin: 0.8em 0;
}

.markdown-preview :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.85em;
}

.markdown-preview :deep(pre) {
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-preview :deep(pre code) {
  background: transparent;
  padding: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  display: block;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin: 0.8em 0;
  padding-left: 1.5em;
}

.markdown-preview :deep(li) {
  margin: 0.3em 0;
}

.markdown-preview :deep(blockquote) {
  margin: 1em 0;
  padding-left: 1em;
  border-left: 3px solid var(--primary-color);
  color: var(--text-secondary);
}

.markdown-preview :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

.markdown-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
}

.markdown-preview :deep(th) {
  background: var(--bg-tertiary);
  font-weight: 600;
}

.empty-hint {
  color: var(--text-muted);
  text-align: center;
  font-style: italic;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 0 0 12px 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}
</style>
