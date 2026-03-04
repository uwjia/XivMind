<template>
  <div class="profile-tab">
    <div class="tab-header">
      <h4>Profile Settings</h4>
      <button @click="handleSave" class="save-btn" :disabled="isSaving">
        <svg v-if="isSaving" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
        </svg>
        <span>{{ isSaving ? 'Saving...' : 'Save Profile' }}</span>
      </button>
    </div>

    <div class="profile-form">
      <div class="form-group">
        <label>Research Interests</label>
        <div class="tags-input">
          <div class="tags-container">
            <span v-for="interest in profile?.research_interests || []" :key="interest" class="tag">
              {{ interest }}
              <button @click="removeInterest(interest)" class="tag-remove">&times;</button>
            </span>
          </div>
          <div class="input-row">
            <input
              v-model="newInterest"
              @keydown.enter.prevent="addInterest"
              placeholder="Add research interest..."
              class="tag-input"
            />
            <button @click="addInterest" class="add-tag-btn" :disabled="!newInterest.trim()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Preferred Domains</label>
        <div class="tags-input">
          <div class="tags-container">
            <span v-for="domain in profile?.preferred_domains || []" :key="domain" class="tag domain">
              {{ domain }}
              <button @click="removeDomain(domain)" class="tag-remove">&times;</button>
            </span>
          </div>
          <div class="input-row">
            <input
              v-model="newDomain"
              @keydown.enter.prevent="addDomain"
              placeholder="Add preferred domain..."
              class="tag-input"
            />
            <button @click="addDomain" class="add-tag-btn" :disabled="!newDomain.trim()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group half">
          <label>Preferred Language</label>
          <select :value="profile?.language_preference || 'en-US'" @change="setLanguagePreference(($event.target as HTMLSelectElement).value)" class="form-select">
            <option value="en-US">English</option>
            <option value="zh-CN">中文</option>
          </select>
        </div>

        <div class="form-group half">
          <label>Summary Style</label>
          <select :value="profile?.summary_style || 'detailed'" @change="setSummaryStyle(($event.target as HTMLSelectElement).value as 'detailed' | 'brief' | 'bullet_points')" class="form-select">
            <option value="detailed">Detailed</option>
            <option value="brief">Brief</option>
            <option value="bullet_points">Bullet Points</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Custom Instructions</label>
        <textarea
          :value="profile?.custom_instructions || ''"
          @change="updateCustomInstructions(($event.target as HTMLTextAreaElement).value)"
          placeholder="Add custom instructions for the AI..."
          class="form-textarea"
          rows="3"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMemoryProfile } from '@/composables/memory'

const {
  profile,
  newInterest,
  newDomain,
  isSaving,
  addInterest,
  removeInterest,
  addDomain,
  removeDomain,
  setLanguagePreference,
  setSummaryStyle,
  updateCustomInstructions,
  handleSave,
} = useMemoryProfile()
</script>

<style scoped>
.profile-tab {
  padding: 0;
}

.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.tab-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.tags-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent-color);
  color: white;
  border-radius: 16px;
  font-size: 0.85rem;
}

.tag.domain {
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

.tag-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.tag-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-row .tag-input {
  flex: 1;
}

.add-tag-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.add-tag-btn:hover:not(:disabled) {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.add-tag-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-tag-btn svg {
  width: 18px;
  height: 18px;
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
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
  min-height: 80px;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
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
