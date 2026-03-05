<template>
  <div 
    class="skill-form-window" 
    :style="windowStyle"
    ref="windowRef"
  >
    <div class="window-header" @mousedown="startDrag">
      <div class="skill-info">
        <div class="skill-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a6 6 0 0 1-7.94-7.94l3.76-3.76a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
        </div>
        <div class="skill-details">
          <h3>{{ skill.name }}</h3>
          <p>{{ skill.description }}</p>
        </div>
      </div>
      <button @click.stop="handleCancel" class="close-btn" :disabled="isExecuting">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
    
    <div class="window-body">
      <div class="form-panel">
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
      </div>
      
      <div class="result-panel">
        <div class="result-header">
          <span>Execution Result</span>
          <button v-if="result" @click="clearResult" class="clear-btn" title="Clear result">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
        <div class="result-content" ref="resultContentRef">
          <div v-if="isExecuting" class="result-loading">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span>Executing skill...</span>
          </div>
          <div v-else-if="result" class="result-message">
            <div v-if="result.error" class="result-error">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              <span>{{ result.error }}</span>
            </div>
            <div v-else class="text-result">
              <div class="result-text" v-html="formatContent(formatSkillResult(result))"></div>
            </div>
          </div>
          <div v-else class="result-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
            </svg>
            <span>No execution result yet</span>
            <p>Fill in the form and click "Execute Skill" to see results</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="window-footer">
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
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import type { Skill, FormField, SchemaProperty } from '@/types/skill'
import { formatSkillResult } from '@/composables/useSkills'

interface SkillResult {
  papers?: Array<{
    id: string
    title: string
    authors?: string[]
    abstract?: string
    primary_category?: string
    published?: string
    similarity_score?: number
  }>
  answer?: string
  content?: string
  references?: Array<{
    id: string
    title: string
    authors?: string[]
  }>
  error?: string
  [key: string]: unknown
}

const props = defineProps<{
  skill: Skill
  isExecuting?: boolean
  result?: SkillResult | null
}>()

const emit = defineEmits<{
  (e: 'submit', paperIds: string[], params: Record<string, unknown>): void
  (e: 'cancel'): void
  (e: 'clearResult'): void
}>()

const paperIdsInput = ref('')
const values = ref<Record<string, unknown>>({})
const isSubmitting = ref(false)
const resultContentRef = ref<HTMLElement | null>(null)

const windowRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const position = ref({ x: 0, y: 0 })
const hasMoved = ref(false)

const windowStyle = computed(() => {
  if (!hasMoved.value) {
    return {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
    }
  }
  return {
    top: `${position.value.y}px`,
    left: `${position.value.x}px`,
    transform: 'none'
  }
})

const startDrag = (event: MouseEvent) => {
  if ((event.target as HTMLElement).closest('.close-btn')) return
  
  isDragging.value = true
  
  if (!hasMoved.value) {
    const rect = windowRef.value?.getBoundingClientRect()
    if (rect) {
      position.value = {
        x: rect.left,
        y: rect.top
      }
      hasMoved.value = true
    }
  }
  
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  event.preventDefault()
}

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return
  
  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y
  
  const windowWidth = windowRef.value?.offsetWidth || 900
  const windowHeight = windowRef.value?.offsetHeight || 400
  
  position.value = {
    x: Math.max(0, Math.min(newX, window.innerWidth - windowWidth)),
    y: Math.max(0, Math.min(newY, window.innerHeight - windowHeight))
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})

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

const formatContent = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const clearResult = () => {
  emit('clearResult')
}

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

watch(() => props.result, () => {
  nextTick(() => {
    if (resultContentRef.value) {
      resultContentRef.value.scrollTop = 0
    }
  })
})

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
.skill-form-window {
  position: fixed;
  top: 3vh;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  width: 94%;
  max-width: 1200px;
  height: 92vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.window-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
  flex-shrink: 0;
  cursor: move;
  user-select: none;
}

.skill-info {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.skill-icon {
  width: 42px;
  height: 42px;
  background: rgba(0, 188, 212, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.skill-icon svg {
  width: 22px;
  height: 22px;
  color: #00BCD4;
}

.skill-details h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 3px 0;
}

.skill-details p {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-btn:hover:not(:disabled) {
  background: #EF4444;
  color: white;
}

.close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.window-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.form-panel {
  width: 340px;
  min-width: 280px;
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.result-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.clear-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.clear-btn svg {
  width: 16px;
  height: 16px;
}

.result-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.result-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;
  color: var(--text-muted);
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #00BCD4;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.result-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 100%;
  color: var(--text-muted);
}

.result-empty svg {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

.result-empty span {
  font-size: 0.95rem;
}

.result-empty p {
  font-size: 0.8rem;
  margin: 0;
}

.result-message {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #EF4444;
}

.result-error svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.text-result {
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.result-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.result-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85em;
}

.form-field {
  margin-bottom: 16px;
}

.form-field:last-child {
  margin-bottom: 0;
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
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-select {
  width: 100%;
  padding: 10px 32px 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: border-color 0.2s;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #00BCD4;
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
  accent-color: #00BCD4;
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

.window-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  flex-shrink: 0;
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

.cancel-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  background: #00BCD4;
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

@media (max-width: 768px) {
  .skill-form-window {
    width: 95%;
    max-height: 80vh;
  }
  
  .window-body {
    flex-direction: column;
  }
  
  .form-panel,
  .result-panel {
    width: 100%;
    border-right: none;
  }
  
  .form-panel {
    border-bottom: 1px solid var(--border-color);
    max-height: 40vh;
  }
  
  .window-header {
    padding: 16px;
  }
  
  .window-footer {
    padding: 12px 16px;
    flex-direction: column;
  }
  
  .cancel-btn,
  .submit-btn {
    width: 100%;
  }
}
</style>
