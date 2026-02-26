<template>
  <div 
    class="subagent-card"
    :class="{ 
      disabled: !agent.available,
      dynamic: agent.source === 'dynamic',
      selected: selected
    }"
    @click="$emit('select', agent)"
  >
    <div class="card-header">
      <div class="agent-icon">
        <svg v-if="agent.icon === 'search'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <svg v-else-if="agent.icon === 'chart-bar'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="20" x2="18" y2="10"/>
          <line x1="12" y1="20" x2="12" y2="4"/>
          <line x1="6" y1="20" x2="6" y2="14"/>
        </svg>
        <svg v-else-if="agent.icon === 'pen'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M12 19l7-7 3 3-7 7-3-3z"/>
          <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/>
          <path d="M2 2l7.586 7.586"/>
          <circle cx="11" cy="11" r="2"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="11" width="18" height="10" rx="2"/>
          <circle cx="12" cy="5" r="2"/>
          <path d="M12 7v4"/>
          <line x1="8" y1="16" x2="8" y2="16"/>
          <line x1="16" y1="16" x2="16" y2="16"/>
        </svg>
      </div>
      <div class="agent-info">
        <h3 class="agent-name">{{ agent.name }}</h3>
        <p class="agent-desc">{{ agent.description }}</p>
      </div>
      <div class="agent-status">
        <span 
          class="status-indicator"
          :class="{ available: agent.available }"
          :title="agent.available ? 'Available' : 'Unavailable'"
        ></span>
      </div>
    </div>

    <div class="card-body">
      <div v-if="agent.skills.length > 0" class="tags-section">
        <span class="tags-label">Skills:</span>
        <div class="tags-list">
          <span v-for="skill in agent.skills.slice(0, 3)" :key="skill" class="tag skill-tag">
            {{ skill }}
          </span>
          <span v-if="agent.skills.length > 3" class="tag more-tag">
            +{{ agent.skills.length - 3 }}
          </span>
        </div>
      </div>

      <div v-if="agent.tools.length > 0" class="tags-section">
        <span class="tags-label">Tools:</span>
        <div class="tags-list">
          <span v-for="tool in agent.tools.slice(0, 3)" :key="tool" class="tag tool-tag">
            {{ tool }}
          </span>
          <span v-if="agent.tools.length > 3" class="tag more-tag">
            +{{ agent.tools.length - 3 }}
          </span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="agent-meta">
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          {{ agent.max_turns }} turns
        </span>
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          {{ agent.temperature }}
        </span>
        <span class="meta-item language-tag" :class="agent.language">
          {{ agent.language === 'zh' ? '中文' : 'EN' }}
        </span>
      </div>
      <div class="source-badge" :class="agent.source">
        {{ agent.source === 'dynamic' ? 'Dynamic' : 'Built-in' }}
      </div>
    </div>

    <div v-if="showActions" class="card-actions">
      <button 
        class="action-btn execute-btn"
        :disabled="!agent.available"
        @click.stop="$emit('execute', agent)"
        title="Execute"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
      </button>
      <button 
        v-if="agent.source === 'dynamic'"
        class="action-btn edit-btn"
        @click.stop="$emit('edit', agent)"
        title="Edit"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
      <button 
        v-if="agent.source === 'dynamic'"
        class="action-btn reload-btn"
        @click.stop="$emit('reload', agent)"
        title="Reload"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
      </button>
      <button 
        v-if="agent.source === 'dynamic'"
        class="action-btn delete-btn"
        @click.stop="$emit('delete', agent)"
        title="Delete"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SubAgent } from '../../types/subagent'

defineProps<{
  agent: SubAgent
  showActions?: boolean
  selected?: boolean
}>()

defineEmits<{
  select: [agent: SubAgent]
  execute: [agent: SubAgent]
  edit: [agent: SubAgent]
  reload: [agent: SubAgent]
  delete: [agent: SubAgent]
}>()
</script>

<style scoped>
.subagent-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.subagent-card:hover:not(.disabled) {
  border-color: #00BCD4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.15);
}

.subagent-card.selected {
  border-color: #00BCD4;
  box-shadow: 0 0 0 2px rgba(0, 188, 212, 0.2);
}

.subagent-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.subagent-card.dynamic {
  border-left: 3px solid #00BCD4;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.agent-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 188, 212, 0.1);
  border-radius: 10px;
}

.agent-icon svg {
  width: 24px;
  height: 24px;
  stroke: #00BCD4;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.agent-status {
  flex-shrink: 0;
}

.status-indicator {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #EF4444;
}

.status-indicator.available {
  background: #00BCD4;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tags-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.skill-tag {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.tool-tag {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.more-tag {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.agent-meta {
  display: flex;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.source-badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}

.source-badge.dynamic {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.source-badge.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.execute-btn:hover:not(:disabled) {
  border-color: #00BCD4;
  color: #00BCD4;
  background: rgba(0, 188, 212, 0.1);
}

.edit-btn:hover:not(:disabled) {
  border-color: #6366F1;
  color: #6366F1;
  background: rgba(99, 102, 241, 0.1);
}

.delete-btn:hover:not(:disabled) {
  border-color: #EF4444;
  color: #EF4444;
  background: rgba(239, 68, 68, 0.1);
}

.language-tag {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.language-tag.en {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.language-tag.zh {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}
</style>
