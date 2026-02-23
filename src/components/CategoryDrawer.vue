<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="drawer-overlay" @click="$emit('close')"></div>
    </Transition>
    <Transition name="drawer">
      <div v-if="isOpen" class="category-drawer">
        <div class="drawer-header">
          <h3>Categories</h3>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="drawer-content">
          <CategoryTree
            :selected-category="selectedCategory"
            :category-counts="categoryCounts"
            @select="(categoryId) => $emit('select', categoryId)"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import CategoryTree from './CategoryTree.vue'

defineProps<{
  isOpen: boolean
  selectedCategory: string | null
  categoryCounts: Record<string, number>
}>()

defineEmits<{
  close: []
  select: [categoryId: string | null]
}>()
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 999;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.category-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 230px;
  height: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.drawer-header h3 {
  margin: 0;
  font-size: 1.1rem;
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
  background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.close-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
}

.close-btn svg {
  width: 18px;
  height: 18px;
  color: white;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.drawer-content::-webkit-scrollbar {
  display: none;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(100%);
}
</style>
