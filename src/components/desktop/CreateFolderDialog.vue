<template>
  <div class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog">
      <div class="dialog-header">
        <h3>Create New Folder</h3>
        <button class="close-btn" @click="$emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-width="2"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-width="2"/>
          </svg>
        </button>
      </div>
      <div class="dialog-body">
        <label for="folder-name">Folder Name</label>
        <input
          id="folder-name"
          ref="inputRef"
          v-model="folderName"
          type="text"
          placeholder="Enter folder name..."
          @keyup.enter="handleCreate"
          @keyup.escape="$emit('close')"
        />
      </div>
      <div class="dialog-footer">
        <button class="btn cancel" @click="$emit('close')">Cancel</button>
        <button 
          class="btn create" 
          :disabled="!folderName.trim()"
          @click="handleCreate"
        >
          Create
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', name: string): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const folderName = ref('')

onMounted(async () => {
  await nextTick()
  inputRef.value?.focus()
})

function handleCreate() {
  const name = folderName.value.trim()
  if (name) {
    emit('create', name)
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  min-width: 320px;
  max-width: 400px;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.dialog-body {
  padding: 20px;
}

.dialog-body label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.dialog-body input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.dialog-body input:focus {
  border-color: var(--accent-color);
}

.dialog-body input::placeholder {
  color: var(--text-muted);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.cancel {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn.cancel:hover {
  background: var(--border-color);
}

.btn.create {
  background: var(--accent-color);
  color: white;
}

.btn.create:hover:not(:disabled) {
  opacity: 0.9;
}

.btn.create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
