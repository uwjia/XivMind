<template>
  <div v-if="paper" class="paper-card-simple-container">
    <div class="paper-card-simple" :style="cardStyle">
      <div class="paper-title-section">
        <h3 class="paper-title" @click="goToDetail">{{ paper.title || 'Untitled' }}</h3>
        <span class="paper-primary-category" :style="categoryStyle">{{ paper.primaryCategory || paper.category || 'CS' }}</span>
        <span class="paper-index">{{ index || 'N/A' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme-store'
import { getCategoryColor } from '@/utils/categoryColors'
import type { Paper } from '@/types'

const props = defineProps<{
  paper: Paper
  index?: number
}>()

const router = useRouter()
const themeStore = useThemeStore()

const cardStyle = computed(() => {
  return {
    transformStyle: 'preserve-3d' as const,
    transition: 'all 0.3s ease'
  }
})

const isMinimal = computed(() => themeStore.iconStyle === 'minimal')

const categoryStyle = computed(() => {
  if (isMinimal.value) {
    return {
      backgroundColor: 'var(--tag-primary-category-bg)',
      color: 'var(--tag-primary-category)',
      border: '1px solid var(--tag-primary-category-border)'
    }
  }
  const color = getCategoryColor(props.paper?.primaryCategory || props.paper?.category || 'cs.AI')
  return {
    backgroundColor: color + '20',
    color: color,
    border: `1px solid ${color}40`
  }
})

const goToDetail = () => {
  if (!props.paper?.id) {
    console.warn('Paper has no ID, cannot navigate to detail')
    return
  }
  router.push({ name: 'PaperDetail', params: { id: props.paper.id } })
}
</script>

<style scoped>
.paper-card-simple-container {
  perspective: 1000px;
  margin: 0px;
  width: 100%;
  max-width: 100%;
}

.paper-card-simple {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 12px 20px;
  cursor: default;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  transform-style: preserve-3d;
  width: 100%;
  min-height: 60px;
  height: auto;
  display: flex;
  flex-direction: column;
}

.paper-card-simple::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}

.paper-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.paper-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
  z-index: 1;
  position: relative;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.paper-title:hover {
  color: var(--accent-color);
}

.paper-primary-category {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  white-space: nowrap;
}

.paper-index {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  white-space: nowrap;
  color: var(--tag-index);
  background-color: color-mix(in srgb, var(--tag-index) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--tag-index) 30%, transparent);
}

@media (max-width: 768px) {
  .paper-card-simple-container {
    margin: 12px;
  }
  
  .paper-card-simple {
    padding: 14px 16px;
    min-height: 70px;
  }

  .paper-title {
    font-size: 1rem;
  }
  
  .paper-title-section {
    gap: 8px;
  }
}
</style>
