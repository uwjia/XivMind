<template>
  <div class="timeline">
    <div class="bars-container">
      <div 
        v-for="item in yearlyPapers" 
        :key="item.year"
        class="bar-item"
        :style="{ height: getBarHeight(item.count) + '%' }"
        :title="`${item.year}: ${item.count} papers`"
      >
        <span class="bar-value">{{ item.count }}</span>
      </div>
    </div>
    <div class="labels-container">
      <span 
        v-for="item in yearlyPapers" 
        :key="item.year"
        class="year-label"
      >
        {{ item.year }}
      </span>
    </div>
    <div v-if="yearlyPapers.length === 0" class="empty-state">
      No data available
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { YearlyPaperCount } from '@/types/author'

const props = defineProps<{
  yearlyPapers: YearlyPaperCount[]
}>()

const maxCount = computed(() => {
  if (!props.yearlyPapers || props.yearlyPapers.length === 0) return 1
  return Math.max(...props.yearlyPapers.map(p => p.count))
})

function getBarHeight(count: number): number {
  return (count / maxCount.value) * 100
}
</script>

<style scoped>
.timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 120px;
}

.bars-container {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 4px;
  min-height: 0;
}

.bar-item {
  flex: 1;
  min-width: 20px;
  max-width: 50px;
  background: linear-gradient(180deg, var(--accent-color) 0%, rgba(59, 130, 246, 0.6) 100%);
  border-radius: 3px 3px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

.bar-item:hover {
  background: linear-gradient(180deg, #2563eb 0%, rgba(59, 130, 246, 0.8) 100%);
}

.bar-value {
  font-size: 0.65rem;
  font-weight: 600;
  color: white;
  padding-top: 4px;
}

.labels-container {
  display: flex;
  gap: 4px;
  border-top: 1px solid var(--border-color);
  padding-top: 4px;
  flex-shrink: 0;
}

.year-label {
  flex: 1;
  min-width: 20px;
  max-width: 50px;
  text-align: center;
  font-size: 0.65rem;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.85rem;
}
</style>
