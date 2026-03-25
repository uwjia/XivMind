<template>
  <div class="category-distribution">
    <div class="pie-chart">
      <svg viewBox="0 0 100 100">
        <circle 
          v-for="(segment, index) in segments" 
          :key="index"
          :cx="50"
          :cy="50"
          :r="40"
          fill="transparent"
          :stroke="segment.color"
          :stroke-width="20"
          :stroke-dasharray="segment.dashArray"
          :stroke-dashoffset="segment.dashOffset"
          class="pie-segment"
        />
        <circle 
          cx="50" 
          cy="50" 
          r="30" 
          :fill="isDarkMode ? '#1e293b' : '#fff'"
        />
      </svg>
      <div class="center-text">
        <span class="total-count">{{ totalCategories }}</span>
        <span class="total-label">areas</span>
      </div>
    </div>
    <div class="category-list">
      <div 
        v-for="cat in categories.slice(0, 5)" 
        :key="cat.category"
        class="category-item"
      >
        <span class="category-color" :style="{ background: getCategoryColor(cat.category) }"></span>
        <span class="category-name">{{ cat.name || cat.category }}</span>
        <span class="category-count">{{ cat.count }}</span>
      </div>
    </div>
    <div v-if="categories.length === 0" class="empty-state">
      No data available
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme-store'
import type { CategoryDistribution } from '@/types/author'

const props = defineProps<{
  categories: CategoryDistribution[]
}>()

const themeStore = useThemeStore()
const isDarkMode = computed(() => themeStore.isDark)

const totalCategories = computed(() => props.categories?.length || 0)

function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    'cs.AI': '#3b82f6',
    'cs.LG': '#10b981',
    'cs.CL': '#f59e0b',
    'cs.CV': '#ef4444',
    'cs.NE': '#8b5cf6',
    'cs.RO': '#ec4899',
    'cs.SE': '#06b6d4',
    'cs.DB': '#84cc16',
    'cs.DC': '#f97316',
    'cs.CR': '#6366f1',
  }
  return colors[category] || '#64748b'
}

const segments = computed(() => {
  if (!props.categories || props.categories.length === 0) return []

  const total = props.categories.reduce((sum, cat) => sum + cat.count, 0)
  const circumference = 2 * Math.PI * 40
  let offset = 0

  return props.categories.slice(0, 5).map(cat => {
    const percentage = cat.count / total
    const dashLength = percentage * circumference
    const dashArray = `${dashLength} ${circumference - dashLength}`
    const dashOffset = -offset

    offset += dashLength

    return {
      color: getCategoryColor(cat.category),
      dashArray,
      dashOffset,
    }
  })
})
</script>

<style scoped>
.category-distribution {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pie-chart {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto;
}

.pie-chart svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.pie-segment {
  transition: all 0.3s;
}

.pie-segment:hover {
  opacity: 0.8;
}

.center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.total-count {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.total-label {
  display: block;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.category-color {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}

.category-name {
  flex: 1;
  font-size: 0.8rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 20px 0;
}
</style>
