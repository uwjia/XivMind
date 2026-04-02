<template>
  <div class="summary-section">
    <h4 class="section-title">📊 Daily Summary</h4>
    <p class="summary-text">{{ summary }}</p>
    <div v-if="themes?.length" class="themes-list">
      <span class="theme-label">Main Themes:</span>
      <span v-for="theme in themes" :key="theme" class="theme-tag">{{ theme }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  summary: string
  themes?: string[] | null
}>()
</script>

<style scoped>
.summary-section {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.themes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.theme-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.theme-tag {
  padding: 4px 10px;
  background: var(--accent-color-light, rgba(59, 130, 246, 0.1));
  color: var(--accent-color, #3b82f6);
  border-radius: 12px;
  font-size: 0.8rem;
}
</style>
