<template>
  <div class="graph-controls">
    <div class="control-section">
      <label class="control-label">Similarity Threshold</label>
      <div class="slider-container">
        <input
          type="range"
          v-model.number="localThreshold"
          min="0.1"
          max="0.9"
          step="0.05"
          class="slider"
        />
        <span class="slider-value">{{ (localThreshold * 100).toFixed(0) }}%</span>
      </div>
    </div>

    <div class="control-section">
      <label class="control-label">Layout</label>
      <div class="layout-buttons">
        <button
          v-for="layout in layouts"
          :key="layout.value"
          :class="['layout-btn', { active: currentLayout === layout.value }]"
          @click="$emit('layoutChange', layout.value)"
          :title="layout.label"
        >
          <component :is="layout.icon" />
        </button>
      </div>
    </div>

    <div class="control-section">
      <label class="control-label">
        <input type="checkbox" v-model="localShowLabels" />
        Show Labels
      </label>
    </div>

    <div class="control-section categories-section">
      <label class="control-label">Categories</label>
      <div class="category-list">
        <label
          v-for="cat in categories"
          :key="cat.name"
          class="category-item"
        >
          <input
            type="checkbox"
            :checked="!selectedCategories.includes(cat.name) || selectedCategories.length === 0"
            @change="toggleCategory(cat.name)"
          />
          <span class="category-color" :style="{ background: cat.color }"></span>
          <span class="category-name">{{ cat.name }}</span>
          <span class="category-count">{{ cat.count }}</span>
        </label>
      </div>
    </div>

    <div class="control-section">
      <button class="reset-btn" @click="$emit('reset')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
        Reset
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, h } from 'vue'
import type { GraphConfig } from '../../types/graph'

const props = defineProps<{
  config: GraphConfig
  categories: Array<{ name: string; count: number; color: string }>
}>()

const emit = defineEmits<{
  configChange: [config: Partial<GraphConfig>]
  layoutChange: [layout: GraphConfig['layoutType']]
  reset: []
}>()

const localThreshold = ref(props.config.similarityThreshold)
const localShowLabels = ref(props.config.showLabels)
const currentLayout = ref(props.config.layoutType)
const selectedCategories = ref<string[]>(props.config.selectedCategories)

watch(localThreshold, (val) => {
  emit('configChange', { similarityThreshold: val })
})

watch(localShowLabels, (val) => {
  emit('configChange', { showLabels: val })
})

watch(() => props.config, (newConfig) => {
  localThreshold.value = newConfig.similarityThreshold
  localShowLabels.value = newConfig.showLabels
  currentLayout.value = newConfig.layoutType
  selectedCategories.value = newConfig.selectedCategories
}, { deep: true })

const toggleCategory = (categoryName: string) => {
  if (selectedCategories.value.includes(categoryName)) {
    selectedCategories.value = selectedCategories.value.filter(c => c !== categoryName)
  } else {
    selectedCategories.value = [...selectedCategories.value, categoryName]
  }
  emit('configChange', { selectedCategories: selectedCategories.value })
}

const ForceIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('circle', { cx: '12', cy: '12', r: '3' }),
  h('circle', { cx: '5', cy: '5', r: '2' }),
  h('circle', { cx: '19', cy: '5', r: '2' }),
  h('circle', { cx: '5', cy: '19', r: '2' }),
  h('circle', { cx: '19', cy: '19', r: '2' }),
  h('line', { x1: '7', y1: '7', x2: '10', y2: '10' }),
  h('line', { x1: '14', y1: '10', x2: '17', y2: '7' }),
  h('line', { x1: '7', y1: '17', x2: '10', y2: '14' }),
  h('line', { x1: '17', y1: '17', x2: '14', y2: '14' })
])

const CircularIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('circle', { cx: '12', cy: '12', r: '9' }),
  h('circle', { cx: '12', cy: '3', r: '2' }),
  h('circle', { cx: '19.5', cy: '8', r: '2' }),
  h('circle', { cx: '19.5', cy: '16', r: '2' }),
  h('circle', { cx: '12', cy: '21', r: '2' }),
  h('circle', { cx: '4.5', cy: '16', r: '2' }),
  h('circle', { cx: '4.5', cy: '8', r: '2' })
])

const HierarchicalIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('circle', { cx: '12', cy: '4', r: '2' }),
  h('circle', { cx: '6', cy: '12', r: '2' }),
  h('circle', { cx: '18', cy: '12', r: '2' }),
  h('circle', { cx: '4', cy: '20', r: '2' }),
  h('circle', { cx: '8', cy: '20', r: '2' }),
  h('circle', { cx: '16', cy: '20', r: '2' }),
  h('circle', { cx: '20', cy: '20', r: '2' }),
  h('line', { x1: '12', y1: '6', x2: '6', y2: '10' }),
  h('line', { x1: '12', y1: '6', x2: '18', y2: '10' }),
  h('line', { x1: '6', y1: '14', x2: '4', y2: '18' }),
  h('line', { x1: '6', y1: '14', x2: '8', y2: '18' }),
  h('line', { x1: '18', y1: '14', x2: '16', y2: '18' }),
  h('line', { x1: '18', y1: '14', x2: '20', y2: '18' })
])

const layouts = [
  { value: 'force' as const, label: 'Force-directed', icon: ForceIcon },
  { value: 'circular' as const, label: 'Circular', icon: CircularIcon },
  { value: 'hierarchical' as const, label: 'Hierarchical', icon: HierarchicalIcon }
]
</script>

<style scoped>
.graph-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  min-width: 200px;
}

.control-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.control-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent-color);
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-tertiary);
  appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-color);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-value {
  min-width: 40px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.layout-buttons {
  display: flex;
  gap: 8px;
}

.layout-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.layout-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.layout-btn.active {
  border-color: var(--accent-color);
  background: var(--accent-color);
  color: white;
}

.layout-btn svg {
  width: 20px;
  height: 20px;
}

.categories-section {
  max-height: 200px;
  overflow-y: auto;
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
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.category-item:hover {
  background: var(--bg-tertiary);
}

.category-item input[type="checkbox"] {
  width: 14px;
  height: 14px;
  accent-color: var(--accent-color);
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.category-name {
  flex: 1;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.category-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 10px;
}

.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.reset-btn svg {
  width: 18px;
  height: 18px;
}
</style>
