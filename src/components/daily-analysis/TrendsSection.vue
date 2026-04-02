<template>
  <div class="trends-section">
    <h4 class="section-title">🔥 Research Trends</h4>
    <div class="trends-list">
      <div v-for="trend in trends" :key="trend.name" class="trend-item">
        <div class="trend-header">
          <span class="trend-name">{{ trend.name }}</span>
          <span class="trend-count">{{ trend.paper_count }} papers</span>
        </div>
        <p class="trend-description">{{ trend.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Trend } from '@/types/dailyAnalysis'

defineProps<{
  trends: Trend[]
}>()
</script>

<style scoped>
.trends-section {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.trends-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trend-item {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.trend-name {
  font-weight: 500;
  color: var(--text-primary);
}

.trend-count {
  font-size: 0.8rem;
  color: var(--accent-color, #3b82f6);
  background: var(--accent-color-light, rgba(59, 130, 246, 0.1));
  padding: 2px 8px;
  border-radius: 10px;
}

.trend-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}
</style>
