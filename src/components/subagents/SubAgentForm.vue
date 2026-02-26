<template>
  <div class="subagent-form">
    <div class="form-header">
      <h3>Execute SubAgent</h3>
      <div class="agent-badge">
        <span class="agent-name">{{ agent.name }}</span>
        <span class="agent-id">{{ agent.id }}</span>
      </div>
    </div>

    <div class="form-body">
      <div class="form-group">
        <label for="instruction">Instruction</label>
        <textarea
          id="instruction"
          v-model="form.instruction"
          placeholder="Enter your task instruction..."
          rows="4"
          :disabled="executing"
        ></textarea>
      </div>

      <div class="form-group">
        <label>Paper IDs (Optional)</label>
        <div class="paper-ids-input">
          <input
            v-model="paperIdInput"
            type="text"
            placeholder="Enter paper IDs (comma or space separated)"
            @keydown.enter.prevent="addPaperId"
            :disabled="executing"
          />
          <button 
            class="add-btn"
            @click="addPaperId"
            :disabled="!paperIdInput.trim() || executing"
          >
            Add
          </button>
        </div>
        <p class="input-hint">Paper IDs in the input will be automatically included when you click Execute.</p>
        <div v-if="form.paper_ids && form.paper_ids.length > 0" class="paper-ids-list">
          <span v-for="id in form.paper_ids" :key="id" class="paper-id-tag">
            {{ id }}
            <button @click="removePaperId(id)" :disabled="executing">×</button>
          </span>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="maxTurns">Max Turns</label>
          <input
            id="maxTurns"
            v-model.number="form.max_turns"
            type="number"
            min="1"
            max="50"
            :disabled="executing"
          />
        </div>

        <div class="form-group">
          <label for="temperature">Temperature</label>
          <div class="temperature-input">
            <input
              id="temperature"
              v-model.number="form.temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              :disabled="executing"
            />
            <span class="temperature-value">{{ form.temperature }}</span>
          </div>
        </div>
      </div>

      <div class="llm-info">
        <div class="llm-label">Using Global LLM Settings:</div>
        <div class="llm-values">
          <span class="llm-tag provider">{{ llmStore.selectedProvider || 'default' }}</span>
          <span class="llm-tag model">{{ llmStore.selectedModel || 'default' }}</span>
        </div>
      </div>
    </div>

    <div class="form-footer">
      <button class="btn secondary" @click="$emit('cancel')" :disabled="executing">
        Cancel
      </button>
      <button 
        class="btn primary" 
        @click="handleExecute"
        :disabled="!canExecute || executing"
      >
        <svg v-if="executing" class="spinner" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4" stroke-dashoffset="10"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        {{ executing ? 'Executing...' : 'Execute' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import type { SubAgent, SubAgentExecuteRequest } from '../../types/subagent'
import { useLLMStore } from '../../stores/llm-store'

const props = defineProps<{
  agent: SubAgent
  executing?: boolean
}>()

const emit = defineEmits<{
  execute: [params: SubAgentExecuteRequest]
  cancel: []
}>()

const llmStore = useLLMStore()
const paperIdInput = ref('')

const form = reactive({
  instruction: '',
  paper_ids: [] as string[],
  max_turns: props.agent.max_turns,
  temperature: props.agent.temperature,
})

watch(() => props.agent, (newAgent) => {
  form.max_turns = newAgent.max_turns
  form.temperature = newAgent.temperature
}, { immediate: true })

const canExecute = computed(() => {
  return form.instruction.trim().length > 0
})

const addPaperId = () => {
  const id = paperIdInput.value.trim()
  if (id && !form.paper_ids.includes(id)) {
    form.paper_ids.push(id)
  }
  paperIdInput.value = ''
}

const removePaperId = (id: string) => {
  const index = form.paper_ids.indexOf(id)
  if (index > -1) {
    form.paper_ids.splice(index, 1)
  }
}

const handleExecute = () => {
  if (!canExecute.value) return
  
  let finalPaperIds = [...form.paper_ids]
  
  if (paperIdInput.value.trim()) {
    const ids = paperIdInput.value.trim().split(/[,\s]+/).filter(id => id && !finalPaperIds.includes(id))
    finalPaperIds = [...finalPaperIds, ...ids]
  }
  
  const params: SubAgentExecuteRequest = {
    instruction: form.instruction.trim(),
    paper_ids: finalPaperIds.length > 0 ? finalPaperIds : undefined,
    max_turns: form.max_turns,
    provider: llmStore.selectedProvider || undefined,
    model: llmStore.selectedModel || undefined,
  }
  
  emit('execute', params)
}
</script>

<style scoped>
.subagent-form {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.form-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.agent-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.agent-name {
  font-weight: 600;
  color: var(--text-primary);
}

.agent-id {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input,
.form-group textarea,
.form-group select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #00BCD4;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.paper-ids-input {
  display: flex;
  gap: 8px;
}

.input-hint {
  margin: 4px 0 0 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.paper-ids-input input {
  flex: 1;
}

.add-btn {
  padding: 10px 16px;
  background: rgba(0, 188, 212, 0.1);
  border: 1px solid #00BCD4;
  border-radius: 8px;
  color: #00BCD4;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn:hover:not(:disabled) {
  background: #00BCD4;
  color: white;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paper-ids-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.paper-id-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 6px;
  font-size: 0.8rem;
  color: #6366F1;
}

.paper-id-tag button {
  background: none;
  border: none;
  color: #6366F1;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0 2px;
}

.paper-id-tag button:hover {
  color: #EF4444;
}

.temperature-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.temperature-input input[type="range"] {
  flex: 1;
  height: 6px;
  padding: 0;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.temperature-input input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #00BCD4;
  cursor: pointer;
}

.temperature-value {
  min-width: 32px;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.llm-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.llm-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.llm-values {
  display: flex;
  gap: 8px;
}

.llm-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
}

.llm-tag.provider {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.llm-tag.model {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn.secondary {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn.secondary:hover:not(:disabled) {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.btn.primary {
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
  border: none;
  color: white;
  box-shadow: 0 0 20px rgba(0, 188, 212, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(0, 188, 212, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
