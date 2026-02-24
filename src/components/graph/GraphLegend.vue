<template>
  <div class="graph-legend">
    <h4 class="legend-title">Legend</h4>
    
    <div class="legend-section">
      <div class="legend-subtitle">Categories</div>
      <div class="legend-items">
        <div
          v-for="cat in displayCategories"
          :key="cat.name"
          class="legend-item"
        >
          <span class="legend-color" :style="{ background: cat.color }"></span>
          <span class="legend-label">{{ cat.name }}</span>
          <span class="legend-count">{{ cat.count }}</span>
        </div>
        <div v-if="categories.length > maxVisible" class="legend-more">
          +{{ categories.length - maxVisible }} more
        </div>
      </div>
    </div>

    <div class="legend-section">
      <div class="legend-subtitle">Node Size</div>
      <div class="size-legend">
        <div class="size-item">
          <span class="size-dot small"></span>
          <span class="size-label">Few citations</span>
        </div>
        <div class="size-item">
          <span class="size-dot medium"></span>
          <span class="size-label">Some citations</span>
        </div>
        <div class="size-item">
          <span class="size-dot large"></span>
          <span class="size-label">Many citations</span>
        </div>
      </div>
    </div>

    <div class="legend-section">
      <div class="legend-subtitle">Edge Width</div>
      <div class="edge-legend">
        <div class="edge-item">
          <span class="edge-line thin"></span>
          <span class="edge-label">Low similarity</span>
        </div>
        <div class="edge-item">
          <span class="edge-line medium"></span>
          <span class="edge-label">Medium similarity</span>
        </div>
        <div class="edge-item">
          <span class="edge-line thick"></span>
          <span class="edge-label">High similarity</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  categories: Array<{ name: string; count: number; color: string }>
}>()

const maxVisible = 5

const displayCategories = computed(() => {
  return props.categories.slice(0, maxVisible)
})
</script>

<style scoped>
.graph-legend {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.legend-title {
  margin: 0 0 16px 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.legend-section {
  margin-bottom: 16px;
}

.legend-section:last-child {
  margin-bottom: 0;
}

.legend-subtitle {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.legend-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 10px;
}

.legend-more {
  font-size: 0.75rem;
  color: var(--text-muted);
  padding-left: 20px;
}

.size-legend,
.edge-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.size-item,
.edge-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.size-dot {
  border-radius: 50%;
  background: var(--accent-color);
}

.size-dot.small {
  width: 8px;
  height: 8px;
}

.size-dot.medium {
  width: 14px;
  height: 14px;
}

.size-dot.large {
  width: 20px;
  height: 20px;
}

.size-label,
.edge-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.edge-line {
  height: 2px;
  background: var(--text-muted);
  border-radius: 1px;
}

.edge-line.thin {
  width: 20px;
  height: 1px;
}

.edge-line.medium {
  width: 20px;
  height: 2px;
}

.edge-line.thick {
  width: 20px;
  height: 4px;
}
</style>
