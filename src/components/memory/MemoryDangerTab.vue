<template>
  <div class="danger-tab">
    <div class="danger-section">
      <h4>Danger Zone</h4>
      <p class="danger-description">Clear specific types of memories. These actions cannot be undone.</p>
      
      <div class="danger-actions">
        <div class="danger-action-item">
          <div class="danger-action-info">
            <h5>Clear Profile (Core Memory)</h5>
            <p>Delete your user profile including research interests, preferred domains, and custom instructions.</p>
          </div>
          <button @click="confirmClearCore" class="danger-btn" :disabled="memoryStore.isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            <span>Clear Profile</span>
          </button>
        </div>
        
        <div class="danger-action-item">
          <div class="danger-action-info">
            <h5>Clear Conversation History (Recall Memory)</h5>
            <p>Delete all conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }} items). Your profile and knowledge base will remain.</p>
          </div>
          <button @click="confirmClearRecall" class="danger-btn" :disabled="memoryStore.isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            <span>Clear History</span>
          </button>
        </div>
        
        <div class="danger-action-item">
          <div class="danger-action-info">
            <h5>Clear Knowledge Base (Archival Memory)</h5>
            <p>Delete all saved notes and insights ({{ memoryStore.stats?.archival_memory_count || 0 }} items). Your profile and conversation history will remain.</p>
          </div>
          <button @click="confirmClearArchival" class="danger-btn" :disabled="memoryStore.isLoading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            <span>Clear Knowledge</span>
          </button>
        </div>
      </div>
      
      <div class="danger-divider"></div>
      
      <div class="danger-section-all">
        <h5>Clear All Memories</h5>
        <p class="danger-description">Permanently delete all memories including profile, conversation history, and knowledge base.</p>
        <button @click="showClearConfirm = true" class="danger-btn danger-btn-all" :disabled="memoryStore.isLoading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>Clear All Memories</span>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showClearConfirm" class="modal-overlay" @click.self="showClearConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear All Memories</h3>
          <p>Are you sure you want to clear all memories? This will delete:</p>
          <ul>
            <li>Your user profile</li>
            <li>All conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }})</li>
            <li>All saved notes ({{ memoryStore.stats?.archival_memory_count || 0 }})</li>
          </ul>
          <div class="modal-actions">
            <button @click="showClearConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearAllMemories" class="confirm-btn danger">Clear All</button>
          </div>
        </div>
      </div>

      <div v-if="showClearCoreConfirm" class="modal-overlay" @click.self="showClearCoreConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear Profile</h3>
          <p>Are you sure you want to clear your profile? This will delete:</p>
          <ul>
            <li>Research interests</li>
            <li>Preferred domains</li>
            <li>Custom instructions</li>
          </ul>
          <div class="modal-actions">
            <button @click="showClearCoreConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearCoreMemory" class="confirm-btn danger">Clear Profile</button>
          </div>
        </div>
      </div>

      <div v-if="showClearRecallConfirm" class="modal-overlay" @click.self="showClearRecallConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear History</h3>
          <p>Are you sure you want to clear all conversation memories ({{ memoryStore.stats?.recall_memory_count || 0 }} items)?</p>
          <p class="modal-note">Your profile and knowledge base will remain intact.</p>
          <div class="modal-actions">
            <button @click="showClearRecallConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearRecallMemories" class="confirm-btn danger">Clear History</button>
          </div>
        </div>
      </div>

      <div v-if="showClearArchivalConfirm" class="modal-overlay" @click.self="showClearArchivalConfirm = false">
        <div class="modal-content">
          <h3>Confirm Clear Knowledge Base</h3>
          <p>Are you sure you want to clear all saved notes and insights ({{ memoryStore.stats?.archival_memory_count || 0 }} items)?</p>
          <p class="modal-note">Your profile and conversation history will remain intact.</p>
          <div class="modal-actions">
            <button @click="showClearArchivalConfirm = false" class="cancel-btn">Cancel</button>
            <button @click="clearArchivalMemories" class="confirm-btn danger">Clear Knowledge</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useMemoryDanger } from '@/composables/memory'
import { useMemoryStore } from '@/stores/memory-store'

const memoryStore = useMemoryStore()
const {
  showClearConfirm,
  showClearCoreConfirm,
  showClearRecallConfirm,
  showClearArchivalConfirm,
  confirmClearCore,
  confirmClearRecall,
  confirmClearArchival,
  clearAllMemories,
  clearCoreMemory,
  clearRecallMemories,
  clearArchivalMemories,
} = useMemoryDanger()
</script>

<style scoped>
.danger-tab {
  padding: 0;
}

.danger-section {
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--danger-color);
}

.danger-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--danger-color);
  margin: 0 0 8px 0;
}

.danger-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
}

.danger-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.danger-action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  gap: 16px;
}

.danger-action-info {
  flex: 1;
}

.danger-action-info h5 {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.danger-action-info p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.danger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  flex-shrink: 0;
}

.danger-btn:hover:not(:disabled) {
  background: var(--danger-color);
  color: white;
}

.danger-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-btn svg {
  width: 16px;
  height: 16px;
}

.danger-divider {
  height: 1px;
  background: var(--border-color);
  margin: 24px 0;
}

.danger-section-all {
  padding: 16px;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid var(--danger-color);
  border-radius: 8px;
}

.danger-section-all h5 {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--danger-color);
}

.danger-section-all .danger-description {
  margin: 0 0 16px 0;
}

.danger-btn-all {
  background: var(--danger-color);
  color: white;
}

.danger-btn-all:hover:not(:disabled) {
  background: #d32f2f;
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

.modal-content {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.modal-content p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.modal-content ul {
  margin: 0 0 16px 20px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.modal-content li {
  margin-bottom: 4px;
}

.modal-note {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-style: italic;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.confirm-btn.danger {
  background: var(--danger-color);
  color: white;
}

.confirm-btn.danger:hover {
  background: #d32f2f;
}

@media (max-width: 768px) {
  .danger-action-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .danger-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
