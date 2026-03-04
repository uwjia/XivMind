<template>
  <div class="store-memory-modal">
    <h3>Store New Memory</h3>
    
    <div class="form-group">
      <label>Content</label>
      <textarea 
        v-model="localText" 
        placeholder="Enter the memory content..."
        rows="4"
        class="form-textarea"
      ></textarea>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label>Category</label>
        <select v-model="localCategory" class="form-select">
          <option v-for="cat in categories" :key="cat.value" :value="cat.value">
            {{ cat.label }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Importance: {{ (localImportance * 100).toFixed(0) }}%</label>
        <input 
          type="range" 
          v-model.number="localImportance" 
          min="0" 
          max="1" 
          step="0.1"
          class="form-range"
        />
      </div>
    </div>
    
    <div class="modal-actions">
      <button @click="$emit('update:modelValue', false)" class="cancel-btn">Cancel</button>
      <button 
        @click="handleStore" 
        class="confirm-btn primary" 
        :disabled="isStoring || !localText.trim()"
      >
        {{ isStoring ? 'Storing...' : 'Store Memory' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { MemoryCategory } from '@/types/memory'

const props = defineProps<{
  modelValue: boolean
  isStoring: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'store': [text: string, category: MemoryCategory, importance: number]
}>()

const localText = ref('')
const localCategory = ref<MemoryCategory>('fact')
const localImportance = ref(0.7)

const categories: { value: MemoryCategory; label: string }[] = [
  { value: 'fact', label: 'Fact' },
  { value: 'preference', label: 'Preference' },
  { value: 'context', label: 'Context' },
  { value: 'insight', label: 'Insight' },
  { value: 'task', label: 'Task' },
]

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    localText.value = ''
    localCategory.value = 'fact'
    localImportance.value = 0.7
  }
})

const handleStore = () => {
  if (!localText.value.trim()) return
  emit('store', localText.value.trim(), localCategory.value, localImportance.value)
}
</script>

<style scoped>
.store-memory-modal {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
}

.store-memory-modal h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
  min-height: 100px;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-range {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-tertiary);
  outline: none;
  -webkit-appearance: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent-color);
  cursor: pointer;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
}

.cancel-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn.primary {
  background: var(--accent-color);
  color: white;
}

.confirm-btn.primary:hover:not(:disabled) {
  opacity: 0.9;
}

.confirm-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
