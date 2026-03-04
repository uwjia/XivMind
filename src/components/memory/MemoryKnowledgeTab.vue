<template>
  <div class="knowledge-tab">
    <div class="knowledge-header">
      <h4>Knowledge Base</h4>
      <button @click="showNoteEditor = true" class="add-note-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>Add Note</span>
      </button>
    </div>

    <div class="knowledge-list" v-if="memoryStore.archivalMemories.length > 0">
      <div 
        v-for="memory in memoryStore.archivalMemories" 
        :key="memory.memory_id" 
        class="knowledge-item"
      >
        <div class="knowledge-info">
          <div class="knowledge-type-badge" :class="memory.content_type">
            {{ memory.content_type }}
          </div>
          <h5 class="knowledge-title">{{ memory.title || 'Untitled' }}</h5>
          <p class="knowledge-content">{{ memory.content?.slice(0, 150) }}{{ memory.content?.length > 150 ? '...' : '' }}</p>
          <div class="knowledge-meta">
            <span class="knowledge-date">{{ formatDate(memory.created_at) }}</span>
            <div class="knowledge-tags" v-if="memory.tags?.length">
              <span v-for="tag in memory.tags.slice(0, 3)" :key="tag" class="knowledge-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
        <div class="knowledge-actions">
          <button @click="deleteKnowledge(memory.memory_id)" class="delete-btn" title="Delete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <p>No notes yet. Create your first note to build your knowledge base!</p>
    </div>

    <Teleport to="body">
      <div v-if="showNoteEditor" class="modal-overlay" @click.self="showNoteEditor = false">
        <ArchivalMemoryEditor 
          @close="showNoteEditor = false" 
          @saved="onNoteSaved"
        />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useMemoryKnowledge } from '@/composables/memory'
import { useMemoryStore } from '@/stores/memory-store'
import { ArchivalMemoryEditor } from '@/components/memory'

const memoryStore = useMemoryStore()
const { showNoteEditor, deleteKnowledge, onNoteSaved, formatDate } = useMemoryKnowledge()
</script>

<style scoped>
.knowledge-tab {
  padding: 0;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.knowledge-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.add-note-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.add-note-btn:hover {
  opacity: 0.9;
}

.add-note-btn svg {
  width: 16px;
  height: 16px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.knowledge-info {
  flex: 1;
  min-width: 0;
}

.knowledge-type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.knowledge-type-badge.note {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.knowledge-type-badge.insight {
  background: rgba(255, 193, 7, 0.1);
  color: #FFC107;
}

.knowledge-type-badge.summary {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.knowledge-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.knowledge-content {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0 0 8px 0;
}

.knowledge-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.knowledge-tags {
  display: flex;
  gap: 4px;
}

.knowledge-tag {
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
}

.knowledge-actions {
  display: flex;
  align-items: flex-start;
}

.delete-btn {
  padding: 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.delete-btn:hover {
  border-color: var(--danger-color);
  color: var(--danger-color);
  background: rgba(239, 68, 68, 0.1);
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>
