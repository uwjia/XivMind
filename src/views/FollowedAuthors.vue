<template>
  <div class="followed-authors-page">
    <div class="page-header">
      <div class="header-title">
        <h1>Followed Authors</h1>
        <span class="total-count" v-if="total > 0">(total {{ total }})</span>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search authors..."
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Loading...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
    </div>

    <div v-else-if="filteredAuthors.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
      <span>{{ searchQuery ? 'No authors match your search' : 'No followed authors yet' }}</span>
      <p v-if="!searchQuery" class="hint">Click the follow button on an author's profile to add them here</p>
    </div>

    <div v-else class="authors-list">
      <div
        v-for="author in filteredAuthors"
        :key="author.id"
        class="author-card"
      >
        <div class="author-info">
          <h3 class="author-name" @click="goToAuthor(author.author_name)">
            {{ author.author_name }}
          </h3>
          <div class="author-meta">
            <span class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              {{ author.paper_count }} papers
            </span>
            <span v-if="author.latest_published" class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              Latest: {{ formatDate(author.latest_published) }}
            </span>
          </div>
          <div class="followed-date">
            Followed: {{ formatDate(author.followed_at) }}
          </div>
          <div v-if="author.notes" class="author-notes">
            {{ author.notes }}
          </div>
        </div>
        <div class="author-actions">
          <button class="action-btn papers-btn" @click="goToPapers(author.author_name)" title="View papers">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </button>
          <button class="action-btn profile-btn" @click="goToAuthor(author.author_name)" title="View profile">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </button>
          <button class="action-btn edit-btn" @click="openEditNotes(author)" title="Edit notes">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button class="action-btn unfollow-btn" @click="handleUnfollow(author)" title="Unfollow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="8.5" cy="7" r="4"/>
              <line x1="18" y1="8" x2="23" y2="13"/>
              <line x1="23" y1="8" x2="18" y2="13"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="editingAuthor" class="modal-overlay" @click.self="closeEditNotes">
      <div class="modal">
        <h3>Edit Notes for {{ editingAuthor.author_name }}</h3>
        <textarea
          v-model="editingNotes"
          placeholder="Add notes about this author..."
          rows="4"
        ></textarea>
        <div class="modal-actions">
          <button class="btn cancel" @click="closeEditNotes">Cancel</button>
          <button class="btn save" @click="saveNotes">Save</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :visible="showConfirmDialog"
      :title="confirmTitle"
      :message="confirmMessage"
      type="danger"
      confirmText="Unfollow"
      cancelText="Cancel"
      @confirm="confirmUnfollow"
      @cancel="cancelUnfollow"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFollowedAuthorStore } from '@/stores/followed-author-store'
import type { FollowedAuthor } from '@/types/followedAuthor'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const store = useFollowedAuthorStore()

const editingAuthor = ref<FollowedAuthor | null>(null)
const editingNotes = ref('')
const searchQuery = ref('')
const showConfirmDialog = ref(false)
const confirmTitle = ref('Unfollow Author')
const confirmMessage = ref('')
const pendingUnfollowAuthor = ref<FollowedAuthor | null>(null)

const authors = computed(() => store.sortedAuthors)
const total = computed(() => store.total)
const loading = computed(() => store.loading)
const error = computed(() => store.error)

const filteredAuthors = computed(() => {
  if (!searchQuery.value.trim()) {
    return authors.value
  }
  const query = searchQuery.value.toLowerCase().trim()
  return authors.value.filter(author => 
    author.author_name.toLowerCase().includes(query) ||
    (author.notes && author.notes.toLowerCase().includes(query))
  )
})

onMounted(() => {
  store.fetchFollowedAuthors()
})

function handleSearch() {
}

function goToAuthor(name: string) {
  router.push({ name: 'AuthorProfile', params: { authorName: encodeURIComponent(name) } })
}

function goToPapers(name: string) {
  router.push({ name: 'AuthorPapers', params: { authorName: encodeURIComponent(name) } })
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function openEditNotes(author: FollowedAuthor) {
  editingAuthor.value = author
  editingNotes.value = author.notes || ''
}

function closeEditNotes() {
  editingAuthor.value = null
  editingNotes.value = ''
}

async function saveNotes() {
  if (!editingAuthor.value) return
  
  const success = await store.updateNotes(editingAuthor.value.author_name, editingNotes.value)
  if (success) {
    closeEditNotes()
  }
}

function handleUnfollow(author: FollowedAuthor) {
  pendingUnfollowAuthor.value = author
  confirmMessage.value = `Are you sure you want to unfollow ${author.author_name}?`
  showConfirmDialog.value = true
}

async function confirmUnfollow() {
  if (pendingUnfollowAuthor.value) {
    await store.unfollowAuthor(pendingUnfollowAuthor.value.author_name)
  }
  showConfirmDialog.value = false
  pendingUnfollowAuthor.value = null
}

function cancelUnfollow() {
  showConfirmDialog.value = false
  pendingUnfollowAuthor.value = null
}
</script>

<style scoped>
.followed-authors-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.total-count {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 400;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-box input {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  width: 300px;
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 188, 212, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(0, 188, 212, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.search-btn svg {
  width: 18px;
  height: 18px;
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

.loading-state .spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: #fbbf24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.hint {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 8px;
}

.authors-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.author-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  transition: box-shadow 0.2s;
}

.author-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.author-info {
  flex: 1;
}

.author-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--accent-color);
  cursor: pointer;
  margin: 0 0 8px 0;
}

.author-name:hover {
  text-decoration: underline;
}

.author-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.followed-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.author-notes {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.author-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.edit-btn {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.edit-btn:hover {
  background: var(--accent-color);
  color: white;
}

.papers-btn {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.papers-btn:hover {
  background: #3b82f6;
  color: white;
}

.profile-btn {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.profile-btn:hover {
  background: #8b5cf6;
  color: white;
}

.unfollow-btn {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.unfollow-btn:hover {
  background: #ef4444;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90%;
}

.modal h3 {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.cancel {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn.cancel:hover {
  background: var(--border-color);
}

.btn.save {
  background: var(--accent-color);
  color: white;
}

.btn.save:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box input {
    width: 100%;
  }
}
</style>
