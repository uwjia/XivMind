<template>
  <div class="pdf-thumbnails">
    <div v-if="thumbnails.length === 0" class="empty-thumbnails">
      <button v-if="!loading" class="generate-btn" @click="$emit('generate-thumbnails')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2"/>
          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
          <polyline points="21 15 16 10 5 21" stroke-width="2"/>
        </svg>
        Generate Thumbnails
      </button>
      <div v-else class="loading">
        <div class="spinner"></div>
        <p>Generating thumbnails...</p>
      </div>
    </div>
    <div v-else class="thumbnail-list">
      <div
        v-for="thumbnail in thumbnails"
        :key="thumbnail.page_number"
        class="thumbnail-item"
        :class="{ active: thumbnail.page_number === currentPage }"
        @click="$emit('thumbnail-click', thumbnail.page_number)"
      >
        <img :src="thumbnail.src" :alt="`Page ${thumbnail.page_number}`" />
        <span class="page-number">{{ thumbnail.page_number }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PdfThumbnail } from '@/types/pdf'

defineProps<{
  thumbnails: PdfThumbnail[]
  currentPage: number
  loading: boolean
}>()

defineEmits<{
  'thumbnail-click': [page: number]
  'generate-thumbnails': []
}>()
</script>

<style scoped>
.pdf-thumbnails {
  padding: 12px;
}

.empty-thumbnails {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.generate-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.generate-btn svg {
  width: 32px;
  height: 32px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading .spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.thumbnail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.thumbnail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.thumbnail-item:hover {
  background: var(--bg-secondary);
}

.thumbnail-item.active {
  border-color: var(--accent-color);
  background: var(--bg-secondary);
}

.thumbnail-item img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.thumbnail-item .page-number {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}
</style>
