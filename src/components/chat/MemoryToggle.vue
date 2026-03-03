<template>
  <div class="memory-toggle">
    <label class="toggle-label">
      <input 
        type="checkbox" 
        v-model="useMemory"
        @change="onToggle"
      />
      <span class="toggle-slider"></span>
    </label>
    <span class="toggle-text">
      {{ useMemory ? 'Memory Enabled' : 'Memory Disabled' }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const useMemory = ref(true)

const emit = defineEmits<{
  (e: 'change', value: boolean): void
}>()

const onToggle = () => {
  localStorage.setItem('use_memory', String(useMemory.value))
  emit('change', useMemory.value)
}

onMounted(() => {
  const savedSetting = localStorage.getItem('use_memory')
  if (savedSetting !== null) {
    useMemory.value = savedSetting === 'true'
  }
  emit('change', useMemory.value)
})
</script>

<style scoped>
.memory-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  cursor: pointer;
}

.toggle-label input {
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
  background-color: #b2ebf2;
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider::before {
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

input:checked + .toggle-slider {
  background-color: var(--primary-color, #00BCD4);
}

input:checked + .toggle-slider::before {
  transform: translateX(20px);
}

.toggle-text {
  font-size: 0.85rem;
  color: var(--text-secondary, #90a4ae);
  white-space: nowrap;
}
</style>
