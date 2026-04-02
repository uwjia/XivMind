<template>
  <div class="daily-analysis-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Back
      </button>
      <div class="header-info">
        <h1 class="page-title">AI Daily Analysis</h1>
        <span class="date-badge">{{ date }}</span>
      </div>
    </div>

    <DailyAnalysisPanel 
      :date="date"
      :user-interests="userInterests"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import DailyAnalysisPanel from '@/components/daily-analysis/DailyAnalysisPanel.vue'

const props = defineProps<{
  date: string
}>()

const router = useRouter()

const userInterests = [] as string[]

function goBack() {
  router.push({ name: 'Home' })
}
</script>

<style scoped>
.daily-analysis-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 12px;
  padding-bottom: 10px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--bg-tertiary);
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.date-badge {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-family: 'Courier New', monospace;
}

@media (max-width: 768px) {
  .daily-analysis-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .page-title {
    font-size: 1.25rem;
  }
}
</style>
