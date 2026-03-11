<template>
  <div class="execution-input-dialog">
    <div class="dialog-content">
      <div class="dialog-header">
        <h3>Execute Workflow</h3>
        <button class="close-btn" @click="$emit('cancel')">×</button>
      </div>
      
      <div class="dialog-body">
        <div class="form-group">
          <label for="instruction">
            Instruction <span class="required">*</span>
          </label>
          <textarea
            id="instruction"
            v-model="instruction"
            placeholder="Enter your task instruction... e.g., 'Summarize paper 2401.12345'"
            rows="4"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="paperIds">
            Paper IDs <span class="optional">(optional)</span>
          </label>
          <input
            id="paperIds"
            v-model="paperIdsStr"
            type="text"
            placeholder="e.g., 2401.12345, 2401.67890"
          />
          <span class="hint">Comma-separated list of arXiv paper IDs</span>
        </div>
      </div>
      
      <div class="dialog-footer">
        <button class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
        <button
          class="btn btn-primary"
          :disabled="!instruction.trim()"
          @click="handleConfirm"
        >
          Execute
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  defaultInstruction?: string
  defaultPaperIds?: string[]
}>()

const emit = defineEmits<{
  (e: 'confirm', input: { instruction: string; paperIds?: string[] }): void
  (e: 'cancel'): void
}>()

const instruction = ref(props.defaultInstruction || '')
const paperIdsStr = ref((props.defaultPaperIds || []).join(', '))

watch(() => props.defaultInstruction, (val) => {
  instruction.value = val || ''
})

watch(() => props.defaultPaperIds, (val) => {
  paperIdsStr.value = (val || []).join(', ')
})

function handleConfirm() {
  const paperIds = paperIdsStr.value
    .split(',')
    .map(id => id.trim())
    .filter(Boolean)
  
  emit('confirm', {
    instruction: instruction.value.trim(),
    paperIds: paperIds.length > 0 ? paperIds : undefined,
  })
}
</script>

<style scoped>
.execution-input-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.dialog-content {
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
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
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.required {
  color: #EF4444;
}

.optional {
  color: var(--text-muted);
  font-weight: 400;
}

.form-group textarea,
.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
}

.form-group textarea:focus,
.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-group textarea::placeholder,
.form-group input::placeholder {
  color: var(--text-muted);
}

.hint {
  display: block;
  margin-top: 6px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
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

.btn-primary {
  background: var(--primary-color);
  border: none;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #7C3AED;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
