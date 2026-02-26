<template>
  <div 
    class="skill-card" 
    :class="{ 
      dynamic: skill.source === 'dynamic',
      disabled: !skill.available,
      selected: selected
    }"
    @click="$emit('select', skill)"
  >
    <div class="skill-header">
      <div class="skill-icon">
        <svg v-if="skill.icon === 'file-text'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <svg v-else-if="skill.icon === 'languages'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
        <svg v-else-if="skill.icon === 'quote'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/>
          <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/>
        </svg>
        <svg v-else-if="skill.icon === 'search'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4"/>
          <path d="M12 8h.01"/>
        </svg>
      </div>
      <div class="skill-info">
        <div class="skill-name">{{ skill.name }}</div>
        <div class="skill-desc">{{ skill.description }}</div>
      </div>
      <div class="skill-meta">
        <span class="skill-category">{{ skill.category }}</span>
        <span 
          v-if="skill.source === 'dynamic'" 
          class="skill-source dynamic"
          title="Dynamically loaded from SKILL.md"
        >
          Dynamic
        </span>
        <span 
          v-else 
          class="skill-source builtin"
          title="Built-in skill"
        >
          Built-in
        </span>
      </div>
    </div>
    
    <div v-if="showActions" class="skill-actions" @click.stop>
      <button 
        class="action-btn execute" 
        @click="$emit('execute', skill)"
        :disabled="!skill.available"
        title="Execute this skill"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        Execute
      </button>
      <button 
        v-if="skill.source === 'dynamic'" 
        class="action-btn edit" 
        @click="$emit('edit', skill)"
        title="Edit skill definition"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
      <button 
        v-if="skill.source === 'dynamic'" 
        class="action-btn reload" 
        @click="$emit('reload', skill)"
        title="Reload skill from file"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M23 4v6h-6"/>
          <path d="M1 20v-6h6"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Skill } from '../../types/skill'

defineProps<{
  skill: Skill
  selected?: boolean
  showActions?: boolean
}>()

defineEmits<{
  (e: 'select', skill: Skill): void
  (e: 'execute', skill: Skill): void
  (e: 'edit', skill: Skill): void
  (e: 'reload', skill: Skill): void
}>()
</script>

<style scoped>
.skill-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.skill-card:hover:not(.disabled) {
  border-color: #00BCD4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.1);
}

.skill-card.selected {
  border-color: #00BCD4;
  background: rgba(0, 188, 212, 0.05);
}

.skill-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.skill-card.dynamic {
  border-left: 3px solid #00BCD4;
}

.skill-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.skill-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border-radius: 10px;
}

.skill-icon svg {
  width: 24px;
  height: 24px;
  stroke: #00BCD4;
}

.skill-info {
  flex: 1;
  min-width: 0;
}

.skill-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.skill-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.skill-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.skill-category {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  color: var(--text-muted);
  text-transform: capitalize;
}

.skill-source {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}

.skill-source.dynamic {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.skill-source.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.skill-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.action-btn.execute {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.action-btn.execute:hover:not(:disabled) {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.action-btn.edit {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 8px;
}

.action-btn.edit:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.action-btn.reload {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  padding: 8px;
}

.action-btn.reload:hover {
  background: rgba(99, 102, 241, 0.2);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
