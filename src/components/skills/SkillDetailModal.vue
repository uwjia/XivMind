<template>
  <div v-if="skill" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content detail-modal" @click.stop>
      <div class="modal-header">
        <div class="detail-header">
          <h3>{{ skill.name }}</h3>
          <div class="detail-meta">
            <span class="skill-category">{{ skill.category }}</span>
            <span 
              v-if="skill.source === 'dynamic'" 
              class="skill-source dynamic"
            >
              Dynamic
            </span>
            <span v-else class="skill-source builtin">Built-in</span>
          </div>
        </div>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      <div class="detail-body">
        <div class="detail-section">
          <h4>Description</h4>
          <p>{{ skill.description }}</p>
        </div>
        
        <div v-if="skill.requires_paper" class="detail-section">
          <h4>Requirements</h4>
          <div class="requirement-tag">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Requires Paper ID
          </div>
        </div>
        
        <div v-if="skill.input_schema" class="detail-section">
          <h4>Parameters</h4>
          <div class="params-list">
            <div 
              v-for="(prop, key) in skill.input_schema.properties" 
              :key="key" 
              class="param-item"
            >
              <span class="param-name">{{ key }}</span>
              <span class="param-type">{{ prop.type }}</span>
              <span v-if="skill.input_schema.required?.includes(key)" class="param-required">required</span>
              <span v-if="prop.description" class="param-desc">{{ prop.description }}</span>
              <span v-if="prop.default" class="param-default">default: {{ prop.default }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-actions">
        <button @click="$emit('close')" class="cancel-btn">Close</button>
        <button 
          @click="$emit('execute', skill)" 
          class="execute-btn"
          :disabled="!skill.available"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Execute
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Skill } from '../../types/skill'

defineProps<{
  skill: Skill | null
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'execute', skill: Skill): void
}>()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
}

.detail-modal {
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.detail-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.detail-meta {
  display: flex;
  gap: 8px;
}

.skill-category {
  font-size: 0.75rem;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  color: var(--text-muted);
  text-transform: capitalize;
}

.skill-source {
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 600;
}

.skill-source.dynamic {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.skill-source.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.detail-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-section p {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

.requirement-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  color: #F59E0B;
  font-size: 0.85rem;
}

.requirement-tag svg {
  width: 16px;
  height: 16px;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.param-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.param-type {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
  border-radius: 4px;
}

.param-required {
  font-size: 0.65rem;
  padding: 2px 6px;
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  border-radius: 4px;
  text-transform: uppercase;
}

.param-desc {
  flex: 1 1 100%;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.param-default {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.cancel-btn {
  padding: 10px 20px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

.execute-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #00BCD4;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background: #059669;
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.execute-btn svg {
  width: 16px;
  height: 16px;
}

@media (max-width: 480px) {
  .modal-content {
    margin: 10px;
    max-height: 85vh;
  }
  
  .modal-header {
    padding: 16px;
  }
  
  .detail-body {
    padding: 16px;
  }
  
  .modal-actions {
    padding: 12px 16px;
    flex-direction: column;
  }
  
  .cancel-btn,
  .execute-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
