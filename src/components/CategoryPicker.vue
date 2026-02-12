<template>
  <div class="category-picker-overlay" v-if="isOpen" @click="closeOutside">
    <div class="category-picker" @click.stop>
      <div class="category-picker-header">
        <h3 class="picker-title">Select Category</h3>
        <button class="close-btn" @click="close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="search-section">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search categories..."
          class="search-input"
        />
      </div>

      <div class="category-list">
        <button
          v-for="category in filteredCategories"
          :key="category.id"
          class="category-item"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <svg class="category-icon" viewBox="0 0 24 24" fill="none" :stroke="getCategoryColor(category.id)">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-id">{{ category.id }}</span>
        </button>
      </div>

      <div class="category-picker-footer">
        <button class="clear-btn" @click="selectCategory('all')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          Clear Selection
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { categories, getCategoryColor } from '../utils/categoryColors'
import type { Category } from '../utils/categoryColors'

const props = defineProps<{
  isOpen: boolean
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:isOpen': [value: boolean]
}>()

const searchQuery = ref<string>('')

const filteredCategories = computed<Category[]>(() => {
  if (!searchQuery.value) return categories
  
  const query = searchQuery.value.toLowerCase()
  return categories.filter(cat => 
    cat.name.toLowerCase().includes(query) ||
    cat.id.toLowerCase().includes(query)
  )
})

const selectedCategory = computed<string>(() => props.modelValue)

const selectCategory = (categoryId: string) => {
  emit('update:modelValue', categoryId)
  emit('update:isOpen', false)
}

const close = () => {
  emit('update:isOpen', false)
}

const closeOutside = () => {
  emit('update:isOpen', false)
}
</script>

<style scoped>
.category-picker-overlay {
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

.category-picker {
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.category-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.picker-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.search-section {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 16px;
}

.search-section:focus-within {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  margin-right: 12px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  color: var(--text-primary);
  outline: none;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.category-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.category-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
}

.category-item.active {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.category-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.category-name {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
}

.category-id {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
}

.category-item.active .category-id {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.category-picker-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.clear-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.clear-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.clear-btn svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 768px) {
  .category-picker {
    padding: 20px;
    max-width: 95%;
  }

  .picker-title {
    font-size: 1.1rem;
  }

  .category-item {
    padding: 10px 12px;
  }

  .category-name {
    font-size: 0.9rem;
  }
}
</style>
