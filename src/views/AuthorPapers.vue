<template>
  <div class="author-papers">
    <div class="author-header">
      <button class="back-btn" @click="goBack" title="Back">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="author-info">
        <h1 class="author-name">{{ decodedAuthorName }}</h1>
        <p class="paper-count">{{ total }} papers found</p>
      </div>
      <router-link 
        :to="{ name: 'AuthorProfile', params: { authorName: authorName } }" 
        class="profile-btn"
        title="View Author Profile"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        Profile
      </router-link>
      <button 
        class="follow-btn" 
        :class="{ followed: isFollowed }"
        @click="toggleFollow"
        :disabled="followLoading"
        title="Follow author"
      >
        <svg v-if="isFollowed" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        {{ isFollowed ? 'Followed' : 'Follow' }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading papers...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchPapers">Retry</button>
    </div>

    <div v-else-if="papers.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M9.172 16.172a4 4 0 0 1-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
      </svg>
      <p>No papers found for this author</p>
    </div>

    <template v-else>
      <div class="papers-grid">
        <PaperCard
          v-for="(paper, index) in papers"
          :key="paper.id"
          :paper="paper"
          :index="currentPage * pageSize + index + 1"
          :highlight-author="decodedAuthorName"
        />
      </div>

      <div v-if="total > pageSize" class="pagination">
        <button class="pagination-btn" @click="goToFirstPage" :disabled="currentPage === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
          </svg>
          First
        </button>
        <button class="pagination-btn" @click="goToPreviousPage" :disabled="currentPage === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Previous
        </button>
        <div class="pagination-jump">
          <span class="pagination-info">Page {{ currentPage + 1 }}/{{ totalPages }}</span>
          <input 
            type="number" 
            v-model.number="jumpPageInput" 
            class="pagination-input" 
            placeholder="num"
            min="1"
            :max="totalPages"
            @input="handleJumpPageInput"
            @keyup.enter="handleGoToPage"
          />
          <button class="pagination-btn" @click="handleGoToPage">Go</button>
        </div>
        <button class="pagination-btn" @click="goToNextPage" :disabled="currentPage >= totalPages - 1">
          Next
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config-store'
import { useFollowedAuthorStore } from '@/stores/followed-author-store'
import { arxivBackendAPI } from '@/services/arxivBackend'
import PaperCard from '@/components/PaperCard.vue'
import type { Paper } from '@/services/arxivBackend'

const configStore = useConfigStore()
const router = useRouter()
const store = useFollowedAuthorStore()

const props = defineProps<{
  authorName: string
}>()

const papers = ref<Paper[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref<string | null>(null)
const currentPage = ref(0)
const pageSize = configStore.maxResults
const jumpPageInput = ref<number | null>(null)
const isFollowed = ref(false)
const followLoading = ref(false)

const decodedAuthorName = computed(() => {
  return decodeURIComponent(props.authorName)
})

const totalPages = computed(() => {
  return Math.ceil(total.value / pageSize)
})

async function fetchPapers() {
  loading.value = true
  error.value = null

  try {
    const start = currentPage.value * pageSize
    const result = await arxivBackendAPI.fetchPapersByAuthor(
      decodedAuthorName.value,
      pageSize,
      start,
      configStore.defaultSubject
    )
    papers.value = result.papers
    total.value = result.total
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to fetch papers'
    papers.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function goToFirstPage() {
  if (currentPage.value !== 0) {
    currentPage.value = 0
    fetchPapers()
  }
}

function goToPreviousPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    fetchPapers()
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
    fetchPapers()
  }
}

const handleJumpPageInput = () => {
  const value = jumpPageInput.value
  if (typeof value === 'number' && value > totalPages.value) {
    jumpPageInput.value = totalPages.value
  }
}

function handleGoToPage() {
  if (jumpPageInput.value && jumpPageInput.value >= 1 && jumpPageInput.value <= totalPages.value) {
    currentPage.value = jumpPageInput.value - 1
    fetchPapers()
    jumpPageInput.value = null
  }
}

watch(() => props.authorName, () => {
  currentPage.value = 0
  total.value = 0
  fetchPapers()
  checkFollowStatus()
}, { immediate: true })

async function checkFollowStatus() {
  isFollowed.value = await store.checkIfFollowed(decodedAuthorName.value)
}

async function toggleFollow() {
  if (followLoading.value) return
  
  followLoading.value = true
  try {
    if (isFollowed.value) {
      await store.unfollowAuthor(decodedAuthorName.value)
      isFollowed.value = false
    } else {
      await store.followAuthor(decodedAuthorName.value)
      isFollowed.value = true
    }
  } finally {
    followLoading.value = false
  }
}
</script>

<style scoped>
.author-papers {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.author-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--accent-color);
  color: white;
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.author-info {
  flex: 1;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--accent-color);
  background: rgba(59, 130, 246, 0.1);
  text-decoration: none;
  transition: all 0.2s;
}

.profile-btn:hover {
  background: var(--accent-color);
  color: white;
}

.profile-btn svg {
  width: 16px;
  height: 16px;
}

.follow-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--accent-color);
  background: rgba(59, 130, 246, 0.1);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.follow-btn:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
}

.follow-btn.followed {
  color: var(--accent-color);
  background: rgba(59, 130, 246, 0.1);
}

.follow-btn.followed:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
}

.follow-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.follow-btn svg {
  width: 16px;
  height: 16px;
}

.author-name {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.paper-count {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-state svg,
.error-state svg,
.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  stroke: var(--text-muted);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  border: none;
  border-radius: 6px;
  background: var(--accent-color);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.retry-btn:hover {
  opacity: 0.9;
}

.papers-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color);
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--bg-secondary);
  border-color: var(--accent-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 16px;
  height: 16px;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-info {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.pagination-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  text-align: center;
}

.pagination-input:focus {
  outline: none;
  border-color: var(--accent-color);
}
</style>
