<template>
  <div v-if="visible" class="toast" :class="type">
    <div class="toast-content">
      <svg v-if="type === 'loading'" class="toast-icon" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="32" stroke-dashoffset="32" class="spinner"/>
      </svg>
      <svg v-else-if="type === 'success'" class="toast-icon" viewBox="0 0 24 24" fill="none">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <svg v-else-if="type === 'error'" class="toast-icon" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <svg v-else-if="type === 'info'" class="toast-icon" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="12" y1="8" x2="12.01" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span class="toast-message">{{ message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'loading',
    validator: (value) => ['loading', 'success', 'error', 'info'].includes(value)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(calc(-50% + 100px));
  z-index: 1000;
  padding: 16px 24px;
  border-radius: 12px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.toast.loading {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%);
  color: #FF9800;
  border-color: rgba(255, 152, 0, 0.3);
}

.toast.success {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(46, 125, 50, 0.05) 100%);
  color: #4CAF50;
  border-color: rgba(76, 175, 80, 0.3);
}

.toast.error {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(183, 28, 28, 0.05) 100%);
  color: #F44336;
  border-color: rgba(244, 67, 54, 0.3);
}

.toast.info {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(25, 118, 210, 0.05) 100%);
  color: #2196F3;
  border-color: rgba(33, 150, 243, 0.3);
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  font-weight: 500;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    stroke-dashoffset: 0;
  }
}

.toast-message {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .toast {
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    max-width: calc(100% - 40px);
  }
}
</style>
