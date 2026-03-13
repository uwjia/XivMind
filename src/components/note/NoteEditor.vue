<template>
  <div class="note-editor">
    <textarea
      ref="textareaRef"
      v-model="content"
      placeholder="Enter note content..."
      class="editor-textarea"
      @keydown.ctrl.enter="handleSave"
    />
    <div class="editor-footer">
      <div class="tags-input">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tag-icon">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
          <line x1="7" y1="7" x2="7.01" y2="7"/>
        </svg>
        <input
          v-model="tagsInput"
          placeholder="Tags (comma separated)"
          class="tags-field"
          @keydown.enter.prevent="handleTagsInput"
        />
      </div>
      <div class="editor-actions">
        <button class="btn cancel" @click="$emit('cancel')">Cancel</button>
        <button class="btn save" @click="handleSave" :disabled="!content.trim()">
          {{ isEditing ? 'Update' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps<{
  initialContent?: string
  initialTags?: string[]
  isEditing?: boolean
}>()

const emit = defineEmits<{
  (e: 'save', content: string, tags: string[]): void
  (e: 'cancel'): void
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const content = ref(props.initialContent || '')
const tagsInput = ref(props.initialTags?.join(', ') || '')

const parseTags = (input: string): string[] => {
  return input
    .split(/[,，]/)
    .map(t => t.trim())
    .filter(t => t.length > 0)
}

const handleTagsInput = () => {
  // Just allow adding tags, actual parsing happens on save
}

const handleSave = () => {
  if (!content.value.trim()) return
  emit('save', content.value.trim(), parseTags(tagsInput.value))
}

watch(() => props.initialContent, (newVal) => {
  content.value = newVal || ''
})

watch(() => props.initialTags, (newVal) => {
  tagsInput.value = newVal?.join(', ') || ''
})

onMounted(() => {
  nextTick(() => {
    textareaRef.value?.focus()
  })
})
</script>

<style scoped>
.note-editor {
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--accent-color);
}

.editor-textarea {
  width: 100%;
  min-height: 80px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  font-family: inherit;
}

.editor-textarea::placeholder {
  color: var(--text-muted);
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.tags-input {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  margin-right: 12px;
}

.tag-icon {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

.tags-field {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.8rem;
  outline: none;
  font-family: inherit;
}

.tags-field::placeholder {
  color: var(--text-muted);
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.btn.cancel {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.btn.cancel:hover {
  background: var(--border-color);
}

.btn.save {
  background: var(--accent-color);
  color: white;
}

.btn.save:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn.save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
