<template>
  <div class="pdf-sidebar">
    <div class="sidebar-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'outline' }"
        @click="activeTab = 'outline'"
      >
        Outline
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'thumbnails' }"
        @click="activeTab = 'thumbnails'"
      >
        Thumbnails
      </button>
    </div>

    <div class="sidebar-content">
      <PdfOutline
        v-if="activeTab === 'outline'"
        :outline="outline"
        @outline-click="$emit('outline-click', $event)"
      />
      <PdfThumbnails
        v-if="activeTab === 'thumbnails'"
        :thumbnails="thumbnails"
        :current-page="currentPage"
        :loading="loading"
        @thumbnail-click="$emit('thumbnail-click', $event)"
        @generate-thumbnails="$emit('generate-thumbnails')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onActivated } from 'vue'
import PdfOutline from '@/components/pdf-reader/PdfOutline.vue'
import PdfThumbnails from '@/components/pdf-reader/PdfThumbnails.vue'
import type { PdfOutlineItem, PdfThumbnail } from '@/types/pdf'

const props = defineProps<{
  outline: PdfOutlineItem[]
  thumbnails: PdfThumbnail[]
  currentPage: number
  loading: boolean
}>()

const emit = defineEmits<{
  'outline-click': [item: PdfOutlineItem]
  'thumbnail-click': [page: number]
  'generate-thumbnails': []
}>()

const activeTab = ref<'outline' | 'thumbnails'>('outline')

onActivated(() => {
  activeTab.value = 'outline'
})

watch(activeTab, (newTab) => {
  if (newTab === 'thumbnails' && props.thumbnails.length === 0 && !props.loading) {
    emit('generate-thumbnails')
  }
}, { immediate: true })
</script>

<style scoped>
.pdf-sidebar {
  width: 240px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.tab-btn.active {
  color: var(--accent-color);
  border-bottom: 2px solid var(--accent-color);
}

.sidebar-content {
  flex: 1;
  overflow: auto;
}
</style>
