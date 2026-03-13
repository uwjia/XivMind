<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Export Notes</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="format-options">
            <label class="format-option">
              <input type="radio" v-model="format" value="text" />
              <span class="format-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                Plain Text
              </span>
            </label>
            <label class="format-option">
              <input type="radio" v-model="format" value="markdown" />
              <span class="format-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <path d="M7 15V9l2.5 3L12 9v6"/>
                  <path d="M17 9v6"/>
                  <path d="M15 12h4"/>
                </svg>
                Markdown
              </span>
            </label>
            <label class="format-option">
              <input type="radio" v-model="format" value="json" />
              <span class="format-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="16 18 22 12 16 6"/>
                  <polyline points="8 6 2 12 8 18"/>
                </svg>
                JSON
              </span>
            </label>
          </div>
          <div class="export-options">
            <label class="option-item">
              <input type="checkbox" v-model="includeTimestamps" />
              Include timestamps
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="includeTags" />
              Include tags
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="includeSource" />
              Include source
            </label>
          </div>
          <div class="preview-section">
            <div class="preview-header">
              <span>Preview</span>
              <button class="copy-preview-btn" @click="copyPreview">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                Copy
              </button>
            </div>
            <pre class="preview-content">{{ previewContent }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn secondary" @click="$emit('close')">Cancel</button>
          <button class="btn primary" @click="handleExport">Download</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { toRef } from 'vue'
import type { Note } from '@/types/note'
import { useNoteExport } from '@/composables/note/useNoteExport'

const props = defineProps<{
  visible: boolean
  notes: Note[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const {
  format,
  includeTimestamps,
  includeTags,
  includeSource,
  createPreviewComputed,
  copyToClipboard,
  downloadFile
} = useNoteExport()

const notesRef = toRef(props, 'notes')
const previewContent = createPreviewComputed(notesRef)

const copyPreview = async () => {
  await copyToClipboard(props.notes)
}

const handleExport = () => {
  downloadFile(props.notes)
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.close-btn {
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
}

.close-btn:hover {
  background: var(--bg-secondary);
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.format-options {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.format-option {
  flex: 1;
  cursor: pointer;
}

.format-option input {
  display: none;
}

.format-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.format-option input:checked + .format-label {
  border-color: var(--accent-color);
  background: rgba(0, 188, 212, 0.1);
  color: var(--accent-color);
}

.format-label svg {
  width: 24px;
  height: 24px;
}

.export-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.option-item input {
  accent-color: var(--accent-color);
}

.preview-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-secondary);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.copy-preview-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.75rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.copy-preview-btn:hover {
  background: var(--bg-tertiary);
}

.copy-preview-btn svg {
  width: 12px;
  height: 12px;
}

.preview-content {
  margin: 0;
  padding: 12px;
  background: var(--bg-primary);
  font-size: 0.75rem;
  color: var(--text-primary);
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Consolas', 'Monaco', monospace;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn.secondary:hover {
  background: var(--bg-tertiary);
}

.btn.primary {
  background: var(--accent-color);
  color: white;
}

.btn.primary:hover {
  background: var(--accent-hover);
}
</style>
