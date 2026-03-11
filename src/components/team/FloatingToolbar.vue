<template>
  <div class="floating-toolbar">
    <button 
      :class="['toolbar-btn', { active: activeView === 'task' }]"
      @click.stop="$emit('change-view', 'task')"
      title="Task View"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    </button>
    
    <button 
      :class="['toolbar-btn', { active: activeView === 'workflow' }]"
      @click.stop="$emit('change-view', 'workflow')"
      title="Workflow View"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="3" y="3" width="7" height="7"/>
        <rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/>
      </svg>
    </button>
    
    <div class="toolbar-divider"></div>
    
    <button 
      class="toolbar-btn"
      @click.stop="$emit('refresh-stats')"
      :disabled="loading"
      title="Refresh Stats"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" :class="{ spinning: loading }">
        <path d="M23 4v6h-6"/>
        <path d="M1 20v-6h6"/>
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  activeView: 'task' | 'workflow'
  loading?: boolean
}>()

defineEmits<{
  (e: 'change-view', view: 'task' | 'workflow'): void
  (e: 'refresh-stats'): void
}>()
</script>

<style scoped>
.floating-toolbar {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  padding: 6px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.toolbar-btn.active {
  background: rgba(139, 92, 246, 0.15);
  color: #8B5CF6;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn svg {
  width: 18px;
  height: 18px;
}

.toolbar-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.toolbar-divider {
  width: 20px;
  height: 1px;
  background: var(--border-color);
}
</style>
