<template>
  <div class="search">
    <div class="search-container">

      <div class="results-header">
        <h2 class="results-title">
          {{ filteredPapers.length }} {{ filteredPapers.length === 1 ? 'paper' : 'papers' }} found
        </h2>
        <div class="sort-options">
          <select v-model="sortBy" class="sort-select">
            <option value="date">Newest First</option>
            <option value="citations">Most Cited</option>
            <option value="views">Most Viewed</option>
          </select>
        </div>
      </div>

      <div class="papers-list">
        <PaperCard
          v-for="(paper, index) in sortedPapers"
          :key="paper.id"
          :paper="paper"
          :index="index + 1"
        />
      </div>

      <div v-if="filteredPapers.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <h3>No papers found</h3>
        <p>Try adjusting your search terms or filters</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePaperStore } from '../stores/paper-store'
import PaperCard from '../components/PaperCard.vue'

const route = useRoute()
const paperStore = usePaperStore()

const searchQuery = ref('')
const sortBy = ref('date')

const filteredPapers = computed(() => {
  return paperStore.getFilteredPapers()
})

const sortedPapers = computed(() => {
  const papers = [...filteredPapers.value]
  switch (sortBy.value) {
    case 'date':
      return papers.sort((a, b) => new Date(b.date) - new Date(a.date))
    case 'citations':
      return papers.sort((a, b) => b.citations - a.citations)
    case 'views':
      return papers.sort((a, b) => b.views - a.views)
    default:
      return papers
  }
})

const performSearch = async () => {
  paperStore.setSearchQuery(searchQuery.value)
  if (searchQuery.value.trim()) {
    try {
      await paperStore.searchPapers(searchQuery.value, 'cs*', 50)
    } catch (err) {
      console.error('Failed to search papers:', err)
    }
  }
}

watch(() => route.query.q, async (newQuery) => {
  if (newQuery !== undefined) {
    searchQuery.value = newQuery
    await performSearch()
  }
}, { immediate: true })

onMounted(async () => {
  
})
</script>

<style scoped>
.search {
  min-height: 100vh;
  padding-top: 64px;
  background: var(--bg-secondary);
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.search-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 8px 16px;
  transition: var(--transition);
}

.search-input-wrapper:focus-within {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1);
}

.search-icon {
  width: 24px;
  height: 24px;
  color: var(--text-muted);
  margin-right: 12px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1.1rem;
  color: var(--text-primary);
  outline: none;
  padding: 8px 0;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-button {
  padding: 12px 32px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.search-button:hover {
  background: var(--accent-hover);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sort-select {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.empty-state p {
  font-size: 1rem;
}

@media (max-width: 768px) {
  .search-container {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 2rem;
  }

  .search-input-wrapper {
    flex-direction: column;
    gap: 12px;
  }

  .search-button {
    width: 100%;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
