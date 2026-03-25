<template>
  <div class="author-profile">
    <div class="profile-header">
      <button class="back-btn" @click="goBack" title="Back">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="header-info">
        <h1 class="author-name">{{ decodedAuthorName }}</h1>
        <p class="subtitle">Author Profile</p>
      </div>
      <router-link 
        :to="{ name: 'AuthorPapers', params: { authorName: authorName } }" 
        class="view-papers-btn"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        View All Papers
      </router-link>
      <button 
        class="follow-btn" 
        :class="{ followed: isFollowed }"
        @click="toggleFollow"
        :disabled="followLoading"
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
      <p>Loading author profile...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchProfileData">Retry</button>
    </div>

    <div v-else-if="!profile || profile.total_papers === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M9.172 16.172a4 4 0 0 1-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
      </svg>
      <p>No papers found for this author</p>
    </div>

    <template v-else>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon papers">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ profile.total_papers }}</span>
            <span class="stat-label">Total Papers</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon years">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ profile.active_years }}</span>
            <span class="stat-label">Active Years</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon categories">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ profile.categories?.length || 0 }}</span>
            <span class="stat-label">Research Areas</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon collaborators">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ profile.collaborators?.length || 0 }}</span>
            <span class="stat-label">Top Collaborators</span>
          </div>
        </div>
      </div>

      <div class="main-content">
        <div class="panel-section yearly-trend">
          <h3 class="panel-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Yearly Trend
          </h3>
          <AuthorTimeline :yearly-papers="profile.yearly_papers" />
        </div>

        <div class="panel-section research-areas">
          <h3 class="panel-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
              <path d="M22 12A10 10 0 0 0 12 2v10z"/>
            </svg>
            Research Areas
          </h3>
          <CategoryDistribution :categories="profile.categories" />
        </div>

        <div class="panel-section collaborators">
          <h3 class="panel-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            Top Collaborators
          </h3>
          <button 
            v-if="(profile.collaborators?.length || 0) > 5"
            class="expand-btn"
            @click="showAllCollaborators = !showAllCollaborators"
            :title="showAllCollaborators ? 'Show less' : 'Show all'"
          >
            <svg v-if="!showAllCollaborators" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="16"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
          </button>
          <div class="collaborators-list" :class="{ expanded: showAllCollaborators }">
            <div 
              v-for="collab in displayedCollaborators" 
              :key="collab.name" 
              class="collaborator-item"
              @click="goToAuthor(collab.name)"
            >
              <span class="collaborator-name">{{ collab.name }}</span>
              <span class="collaborator-count">{{ collab.collaboration_count }} papers</span>
            </div>
          </div>
        </div>

        <div class="panel-section keywords">
          <h3 class="panel-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="4" y1="9" x2="20" y2="9"/>
              <line x1="4" y1="15" x2="20" y2="15"/>
              <line x1="10" y1="3" x2="8" y2="21"/>
              <line x1="16" y1="3" x2="14" y2="21"/>
            </svg>
            Top Keywords
          </h3>
          <div class="keywords-cloud">
            <span 
              v-for="keyword in (profile.keywords || []).slice(0, 15)" 
              :key="keyword.word"
              class="keyword-tag"
              :style="{ fontSize: getKeywordSize(keyword.frequency) + 'px' }"
            >
              {{ keyword.word }}
            </span>
          </div>
        </div>

        <div class="panel-section title-keywords">
          <h3 class="panel-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Title Keywords
          </h3>
          <div class="keywords-cloud">
            <span 
              v-for="keyword in (profile.title_keywords || []).slice(0, 15)" 
              :key="keyword.word"
              class="keyword-tag title-keyword"
              :style="{ fontSize: getTitleKeywordSize(keyword.frequency) + 'px' }"
            >
              {{ keyword.word }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthorProfile } from '@/composables/useAuthorProfile'
import { useFollowedAuthorStore } from '@/stores/followed-author-store'
import AuthorTimeline from '@/components/author/AuthorTimeline.vue'
import CategoryDistribution from '@/components/author/CategoryDistribution.vue'

const router = useRouter()
const store = useFollowedAuthorStore()

const props = defineProps<{
  authorName: string
}>()

const { profile, loading, error, fetchProfile } = useAuthorProfile()

const isFollowed = ref(false)
const followLoading = ref(false)
const showAllCollaborators = ref(false)

const decodedAuthorName = computed(() => {
  return decodeURIComponent(props.authorName)
})

const displayedCollaborators = computed(() => {
  const collaborators = profile.value?.collaborators || []
  if (showAllCollaborators.value) {
    return collaborators
  }
  return collaborators.slice(0, 5)
})

function fetchProfileData() {
  fetchProfile(decodedAuthorName.value)
}

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

function goBack() {
  router.back()
}

function goToAuthor(name: string) {
  router.push({ name: 'AuthorProfile', params: { authorName: encodeURIComponent(name) } })
}

function getKeywordSize(frequency: number): number {
  const minSize = 10
  const maxSize = 18
  const maxFreq = profile.value?.keywords?.[0]?.frequency || 1
  return minSize + ((frequency / maxFreq) * (maxSize - minSize))
}

function getTitleKeywordSize(frequency: number): number {
  const minSize = 10
  const maxSize = 18
  const maxFreq = profile.value?.title_keywords?.[0]?.frequency || 1
  return minSize + ((frequency / maxFreq) * (maxSize - minSize))
}

watch(() => props.authorName, () => {
  fetchProfileData()
  checkFollowStatus()
}, { immediate: true })
</script>

<style scoped>
.author-profile {
  padding: 88px 24px 24px 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.profile-header {
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

.header-info {
  flex: 1;
}

.author-name {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

.view-papers-btn {
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

.view-papers-btn:hover {
  background: var(--accent-color);
  color: white;
}

.view-papers-btn svg {
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

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-icon.papers {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.stat-icon.years {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-icon.categories {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-icon.collaborators {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.main-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: 16px;
}

.panel-section {
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.yearly-trend {
  grid-column: span 2;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.yearly-trend .panel-title {
  flex-shrink: 0;
}

.research-areas {
  grid-column: span 1;
}

.collaborators {
  grid-column: span 1;
}

.keywords {
  grid-column: span 1;
}

.title-keywords {
  grid-column: span 1;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.panel-title svg {
  width: 16px;
  height: 16px;
  color: var(--accent-color);
}

.collaborators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: hidden;
}

.collaborators-list.expanded {
  overflow-y: auto;
}

.panel-section.collaborators {
  position: relative;
}

.expand-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.dark .expand-btn {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
}

.dark .expand-btn:hover {
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.expand-btn svg {
  width: 16px;
  height: 16px;
}

.collaborator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.collaborator-item:hover {
  background: var(--bg-tertiary);
}

.collaborator-name {
  font-size: 0.85rem;
  color: var(--accent-color);
}

.collaborator-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  display: inline-block;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: 12px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.keyword-tag:hover {
  background: var(--accent-color);
  color: white;
}

.keyword-tag.title-keyword {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.keyword-tag.title-keyword:hover {
  background: #10b981;
  color: white;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: repeat(2, 1fr);
  }

  .yearly-trend {
    grid-column: span 2;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .research-areas {
    grid-column: span 1;
  }

  .collaborators {
    grid-column: span 1;
  }

  .keywords {
    grid-column: span 1;
  }

  .title-keywords {
    grid-column: span 1;
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .yearly-trend,
  .research-areas,
  .collaborators,
  .keywords,
  .title-keywords {
    grid-column: span 1;
  }

  .yearly-trend {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .profile-header {
    flex-wrap: wrap;
  }

  .view-papers-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
