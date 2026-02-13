<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="confirm-overlay" @click.self="handleCancel">
        <div class="confirm-dialog">
          <div class="confirm-icon" :class="type">
            <svg v-if="type === 'danger'" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="type === 'warning'" viewBox="0 0 24 24" fill="none">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="currentColor" stroke-width="2"/>
              <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="8" x2="12.01" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          
          <h3 class="confirm-title">{{ title }}</h3>
          <p class="confirm-message">{{ message }}</p>
          
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="handleCancel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              {{ cancelText }}
            </button>
            <button class="confirm-btn confirm" :class="type" @click="handleConfirm">
              <svg v-if="type === 'danger'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  visible: boolean
  title?: string
  message?: string
  type?: 'danger' | 'warning' | 'info'
  confirmText?: string
  cancelText?: string
}>(), {
  title: 'Confirm',
  message: 'Are you sure you want to proceed?',
  type: 'danger',
  confirmText: 'Confirm',
  cancelText: 'Cancel'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.confirm-overlay {
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
  z-index: 2000;
  padding: 20px;
}

.confirm-dialog {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.confirm-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon svg {
  width: 28px;
  height: 28px;
}

.confirm-icon.danger {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.confirm-icon.warning {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
}

.confirm-icon.info {
  background: rgba(33, 150, 243, 0.1);
  color: #2196F3;
}

.confirm-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.confirm-message {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0 0 28px 0;
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.confirm-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  max-width: 160px;
}

.confirm-btn svg {
  width: 18px;
  height: 18px;
}

.confirm-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.confirm-btn.cancel:hover {
  background: var(--bg-primary);
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.confirm-btn.confirm {
  border: none;
  color: white;
}

.confirm-btn.confirm.danger {
  background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
}

.confirm-btn.confirm.danger:hover {
  background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

.confirm-btn.confirm.warning {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
}

.confirm-btn.confirm.warning:hover {
  background: linear-gradient(135deg, #F57C00 0%, #E65100 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.confirm-btn.confirm.info {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
}

.confirm-btn.confirm.info:hover {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-active .confirm-dialog,
.modal-leave-active .confirm-dialog {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-dialog,
.modal-leave-to .confirm-dialog {
  transform: scale(0.9);
  opacity: 0;
}

@media (max-width: 480px) {
  .confirm-dialog {
    padding: 24px;
  }
  
  .confirm-actions {
    flex-direction: column;
  }
  
  .confirm-btn {
    max-width: none;
  }
}
</style>
