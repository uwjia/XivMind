<template>
  <div class="graph-statistics">
    <div class="stat-item">
      <div class="stat-value">{{ statistics?.totalPapers ?? 0 }}</div>
      <div class="stat-label">Papers</div>
    </div>
    
    <div class="stat-item">
      <div class="stat-value">{{ statistics?.totalConnections ?? 0 }}</div>
      <div class="stat-label">Connections</div>
    </div>
    
    <div class="stat-item">
      <div class="stat-value">{{ avgSimilarityPercent }}</div>
      <div class="stat-label">Avg Similarity</div>
    </div>
    
    <div class="stat-item" v-if="statistics?.topCategories?.length">
      <div class="stat-value">{{ statistics.topCategories[0]?.categoryId ?? '-' }}</div>
      <div class="stat-label">Top Category</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GraphStatistics } from '../../types/graph'

const props = defineProps<{
  statistics: GraphStatistics | null
}>()

const avgSimilarityPercent = computed(() => {
  if (!props.statistics?.avgSimilarity) return '0%'
  return (props.statistics.avgSimilarity * 100).toFixed(0) + '%'
})
</script>

<style scoped>
.graph-statistics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 80px;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
</style>
