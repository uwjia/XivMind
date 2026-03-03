<template>
  <div class="archival-editor">
    <div class="editor-header">
      <h3>{{ isEditing ? 'Edit Note' : 'New Note' }}</h3>
      <button @click="$emit('close')" class="close-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="editor-body">
      <div class="form-group">
        <label>Title</label>
        <input
          v-model="form.title"
          placeholder="Enter note title..."
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group half">
          <label>Type</label>
          <select v-model="form.content_type" class="form-select">
            <option value="note">Note</option>
            <option value="insight">Insight</option>
            <option value="summary">Summary</option>
          </select>
        </div>

        <div class="form-group half">
          <label>Tags</label>
          <div class="tags-input-inline">
            <input
              v-model="newTag"
              @keydown.enter.prevent="addTag"
              placeholder="Add tag..."
              class="form-input small"
            />
          </div>
        </div>
      </div>

      <div class="tags-display" v-if="form.tags.length > 0">
        <span v-for="(tag, index) in form.tags" :key="index" class="tag">
          {{ tag }}
          <button @click="removeTag(index)" class="tag-remove">&times;</button>
        </span>
      </div>

      <div class="form-group">
        <label>Content</label>
        <textarea
          v-model="form.content"
          placeholder="Write your note content here... (Markdown supported)"
          class="form-textarea"
          rows="8"
        ></textarea>
      </div>

      <div class="form-group">
        <label>Related Papers (arXiv IDs)</label>
        <div class="papers-input">
          <input
            v-model="newPaperId"
            @keydown.enter.prevent="addPaper"
            placeholder="e.g., 2301.12345"
            class="form-input small"
          />
        </div>
        <div class="papers-display" v-if="form.source_papers.length > 0">
          <span v-for="(paperId, index) in form.source_papers" :key="index" class="paper-tag">
            {{ paperId }}
            <button @click="removePaper(index)" class="tag-remove">&times;</button>
          </span>
        </div>
      </div>
    </div>

    <div class="editor-footer">
      <button @click="$emit('close')" class="cancel-btn">Cancel</button>
      <button @click="saveNote" class="save-btn" :disabled="!isFormValid || isSaving">
        <svg v-if="isSaving" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
        </svg>
        <span>{{ isSaving ? 'Saving...' : 'Save Note' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useMemoryStore } from '../stores/memory-store'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const memoryStore = useMemoryStore()

const isEditing = ref(false)
const isSaving = ref(false)
const newTag = ref('')
const newPaperId = ref('')

const form = reactive({
  title: '',
  content_type: 'note' as 'note' | 'insight' | 'summary',
  content: '',
  tags: [] as string[],
  source_papers: [] as string[],
})

const isFormValid = computed(() => form.content.trim().length > 0)

const addTag = () => {
  if (newTag.value.trim() && !form.tags.includes(newTag.value.trim())) {
    form.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

const addPaper = () => {
  const paperId = newPaperId.value.trim()
  if (paperId && !form.source_papers.includes(paperId)) {
    form.source_papers.push(paperId)
    newPaperId.value = ''
  }
}

const removePaper = (index: number) => {
  form.source_papers.splice(index, 1)
}

const saveNote = async () => {
  if (!isFormValid.value) return
  
  isSaving.value = true
  try {
    const result = await memoryStore.createArchivalMemory({
      title: form.title,
      content_type: form.content_type,
      content: form.content,
      tags: form.tags,
      source_papers: form.source_papers,
    })
    
    if (result) {
      emit('saved')
    }
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.archival-editor {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.editor-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  padding: 6px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.editor-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group.half {
  flex: 1;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-input.small {
  padding: 8px 10px;
}

.form-select {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-textarea {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
  min-height: 150px;
  line-height: 1.5;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
}

.tags-input-inline {
  display: flex;
  gap: 8px;
}

.tags-display,
.papers-display {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.tag,
.paper-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent-color);
  color: white;
  border-radius: 16px;
  font-size: 0.8rem;
}

.paper-tag {
  background: var(--success-color);
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.cancel-btn {
  padding: 10px 20px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.cancel-btn:hover {
  background: var(--bg-tertiary);
}

.save-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.save-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-btn .spinner {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
}
</style>
