<template>
  <div class="config-tab">
    <div class="config-header">
      <h4>Memory Configuration</h4>
      <button @click="saveConfig" class="save-btn" :disabled="isSaving">
        <svg v-if="isSaving" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
        </svg>
        <span>{{ isSaving ? 'Saving...' : 'Save Config' }}</span>
      </button>
    </div>

    <div class="config-form">
      <div class="config-section">
        <h5>Auto Memory</h5>
        
        <div class="form-group toggle-group">
          <div class="toggle-setting">
            <div class="toggle-info">
              <label>Auto Capture</label>
              <p class="toggle-description">Automatically save important conversations to memory.</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="memoryStore.config.auto_capture" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="form-group toggle-group">
          <div class="toggle-setting">
            <div class="toggle-info">
              <label>Auto Recall</label>
              <p class="toggle-description">Automatically recall relevant memories when starting a conversation.</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="memoryStore.config.auto_recall" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="form-group toggle-group">
          <div class="toggle-setting">
            <div class="toggle-info">
              <label>Extract Profile</label>
              <p class="toggle-description">Automatically extract and update user profile from conversations.</p>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="memoryStore.config.extract" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <div class="config-section">
        <h5>Parameters</h5>
        
        <div class="form-group">
          <label>Max Capture Characters</label>
          <input 
            type="number" 
            v-model.number="memoryStore.config.capture_max_chars" 
            min="100" 
            max="2000"
            class="form-input"
          />
          <p class="input-hint">Maximum characters to capture per conversation (100-2000).</p>
        </div>

        <div class="form-group">
          <label>Recall Top K</label>
          <input 
            type="number" 
            v-model.number="memoryStore.config.recall_top_k" 
            min="1" 
            max="20"
            class="form-input"
          />
          <p class="input-hint">Number of memories to recall (1-20).</p>
        </div>

        <div class="form-group">
          <label>Recall Min Score</label>
          <input 
            type="number" 
            v-model.number="memoryStore.config.recall_min_score" 
            min="0" 
            max="1"
            step="0.01"
            class="form-input"
          />
          <p class="input-hint">Minimum similarity score for recall (0.0-1.0).</p>
        </div>
      </div>

      <div class="config-section">
        <h5>Auto Cleanup</h5>
        
        <div class="form-group">
          <label>Auto Forget Days</label>
          <input 
            type="number" 
            v-model.number="memoryStore.config.auto_forget_days" 
            min="7" 
            max="365"
            class="form-input"
          />
          <p class="input-hint">Automatically forget low-importance memories older than this (7-365 days).</p>
        </div>

        <div class="form-group">
          <label>Importance Threshold</label>
          <input 
            type="number" 
            v-model.number="memoryStore.config.importance_threshold" 
            min="0" 
            max="1"
            step="0.01"
            class="form-input"
          />
          <p class="input-hint">Memories with importance below this threshold will be cleaned up (0.0-1.0).</p>
        </div>

        <div class="form-group">
          <button @click="runCleanup" class="cleanup-btn" :disabled="isCleaningUp">
            <svg v-if="isCleaningUp" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            <span>{{ isCleaningUp ? 'Cleaning...' : 'Run Cleanup Now' }}</span>
          </button>
          <p v-if="cleanupResult" class="cleanup-result">{{ cleanupResult }} memories cleaned up.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMemoryConfig } from '@/composables/memory'
import { useMemoryStore } from '@/stores/memory-store'

const memoryStore = useMemoryStore()
const { isSaving, isCleaningUp, cleanupResult, saveConfig, runCleanup } = useMemoryConfig()
</script>

<style scoped>
.config-tab {
  padding: 0;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.config-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
}

.config-section h5 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.config-section .form-group {
  margin-bottom: 16px;
}

.config-section .form-group:last-child {
  margin-bottom: 0;
}

.config-section .form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.config-section .form-input {
  width: 100%;
  max-width: 200px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.config-section .form-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.config-section .input-hint {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 6px 0 0 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toggle-setting {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  gap: 16px;
}

.toggle-group {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.toggle-group:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.toggle-info {
  flex: 1;
}

.toggle-info label {
  display: block;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.toggle-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary, #37474f);
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--accent-color);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
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

.cleanup-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--warning-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.cleanup-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.cleanup-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cleanup-btn svg {
  width: 16px;
  height: 16px;
}

.cleanup-btn .spinner {
  animation: spin 1s linear infinite;
}

.cleanup-result {
  font-size: 0.85rem;
  color: var(--success-color);
  margin: 8px 0 0 0;
}
</style>
