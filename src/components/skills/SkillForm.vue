<template>
  <div class="skill-form">
    <div class="form-header">
      <h3>{{ skill.name }}</h3>
      <p>{{ skill.description }}</p>
    </div>
    
    <div v-if="skill.requires_paper" class="form-field">
      <label for="paper-ids">Paper ID(s) <span class="required">*</span></label>
      <input
        id="paper-ids"
        v-model="paperIdsInput"
        type="text"
        placeholder="Enter paper ID (e.g., 2301.12345)"
        class="form-input"
        :disabled="isExecuting"
      />
      <span class="field-hint">Comma-separated for multiple papers</span>
    </div>
    
    <div v-for="field in formFields" :key="field.key" class="form-field">
      <label :for="field.key">
        {{ field.label }}
        <span v-if="field.required" class="required">*</span>
      </label>
      
      <input
        v-if="field.type === 'string' && !field.enum"
        :id="field.key"
        v-model.string="values[field.key]"
        type="text"
        class="form-input"
        :placeholder="field.description"
        :disabled="isExecuting"
      />
      
      <select
        v-else-if="field.type === 'select'"
        :id="field.key"
        v-model="values[field.key]"
        class="form-select"
        :disabled="isExecuting"
      >
        <option v-for="opt in field.enum" :key="opt" :value="opt">{{ opt }}</option>
      </select>
      
      <input
        v-else-if="field.type === 'integer'"
        :id="field.key"
        v-model.number="values[field.key]"
        type="number"
        class="form-input"
        :min="field.minimum"
        :max="field.maximum"
        :disabled="isExecuting"
      />
      
      <div v-else-if="field.type === 'boolean'" class="form-checkbox">
        <input
          :id="field.key"
          v-model="values[field.key]"
          type="checkbox"
          :disabled="isExecuting"
        />
        <label :for="field.key">{{ field.description || 'Enable' }}</label>
      </div>
      
      <textarea
        v-else-if="field.type === 'text'"
        :id="field.key"
        :value="values[field.key] as string"
        @input="values[field.key] = ($event.target as HTMLTextAreaElement).value"
        class="form-textarea"
        rows="4"
        :placeholder="field.description"
        :disabled="isExecuting"
      ></textarea>
      
      <span v-if="field.description && field.type !== 'boolean'" class="field-hint">
        {{ field.description }}
      </span>
    </div>
    
    <div class="form-actions">
      <button @click="handleCancel" class="cancel-btn" :disabled="isExecuting">
        Cancel
      </button>
      <button
        @click="handleSubmit"
        :disabled="isSubmitting || isExecuting || !isValid"
        class="submit-btn"
      >
        <svg v-if="isSubmitting || isExecuting" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
        </svg>
        <span v-else>Execute Skill</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Skill, FormField, SchemaProperty } from '../../types/skill'

const props = defineProps<{
  skill: Skill
  isExecuting?: boolean
}>()

const emit = defineEmits<{
  (e: 'submit', paperIds: string[], params: Record<string, unknown>): void
  (e: 'cancel'): void
}>()

const paperIdsInput = ref('')
const values = ref<Record<string, unknown>>({})
const isSubmitting = ref(false)

const formFields = computed<FormField[]>(() => {
  if (!props.skill.input_schema?.properties) return []
  
  const properties = props.skill.input_schema.properties
  const required = props.skill.input_schema.required || []
  
  return Object.entries(properties).map(([key, prop]) => {
    const schemaProp = prop as SchemaProperty
    const field: FormField = {
      key,
      label: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      type: schemaProp.enum ? 'select' : schemaProp.type === 'string' ? 'string' : schemaProp.type,
      description: schemaProp.description,
      enum: schemaProp.enum,
      default: schemaProp.default,
      minimum: schemaProp.minimum,
      maximum: schemaProp.maximum,
      required: required.includes(key)
    }
    
    if (schemaProp.default !== undefined) {
      values.value[key] = schemaProp.default
    }
    
    return field
  })
})

const isValid = computed(() => {
  if (props.skill.requires_paper && !paperIdsInput.value.trim()) {
    return false
  }
  
  for (const field of formFields.value) {
    if (field.required && (values.value[field.key] === undefined || values.value[field.key] === '')) {
      return false
    }
  }
  
  return true
})

const handleCancel = () => {
  emit('cancel')
}

const handleSubmit = async () => {
  if (!isValid.value || isSubmitting.value) return
  
  isSubmitting.value = true
  
  try {
    const paperIds = paperIdsInput.value
      .split(',')
      .map(id => id.trim())
      .filter(id => id.length > 0)
    
    emit('submit', paperIds, { ...values.value })
  } finally {
    isSubmitting.value = false
  }
}

watch(() => props.skill, () => {
  paperIdsInput.value = ''
  values.value = {}
  
  if (props.skill.input_schema?.properties) {
    for (const [key, prop] of Object.entries(props.skill.input_schema.properties)) {
      const schemaProp = prop as SchemaProperty
      if (schemaProp.default !== undefined) {
        values.value[key] = schemaProp.default
      }
    }
  }
}, { immediate: true })
</script>

<style scoped>
.skill-form {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
}

.form-header {
  margin-bottom: 20px;
}

.form-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.form-header p {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

.form-field {
  margin-bottom: 16px;
}

.form-field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.required {
  color: #EF4444;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #10B981;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-checkbox input {
  width: 18px;
  height: 18px;
  accent-color: #10B981;
}

.form-checkbox label {
  margin: 0;
  font-weight: 400;
}

.field-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  padding: 12px 24px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  background: #10B981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #059669;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn .spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
