<template>
  <div class="author-ranking-page">
    <div class="page-header">
      <div class="header-title">
        <h1>Author Rankings</h1>
        <span class="total-count" v-if="totalAuthors > 0">(total {{ totalAuthors }})</span>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <input
            v-model="authorSearchQuery"
            type="text"
            placeholder="Search authors..."
            @keyup.enter="handleAuthorSearch"
          />
          <button @click="handleAuthorSearch" class="search-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="controls">
      <div class="metric-selector">
        <label>Sort by:</label>
        <select v-model="selectedMetric">
          <option value="pagerank">PageRank</option>
          <option value="paper_count">Paper Count</option>
          <option value="degree_centrality">Degree Centrality</option>
          <option value="betweenness_centrality">Betweenness</option>
        </select>
      </div>

      <div class="category-filter">
        <label>Category:</label>
        <select v-model="selectedCategory">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>

      <div class="control-actions">
        <button class="refresh-btn" @click="fetchAuthors" :disabled="loading">
          Refresh
        </button>
        <button 
          class="rebuild-btn" 
          @click="openRebuildOptions" 
          :disabled="loading || analysisStatus.running"
        >
          Rebuild
        </button>
      </div>
    </div>

    <div class="status-bar" v-if="analysisStatus.running">
      <div class="progress-info">
        <span>Analysis in progress...</span>
        <span>{{ analysisStatus.progress }} / {{ analysisStatus.total }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <div class="rebuild-options" v-if="showRebuildOptions">
      <div class="rebuild-modal" @click.stop>
        <h3>Rebuild Analysis</h3>
        <p class="modal-description">
          This will rebuild the author ranking analysis. The process may take several minutes to hours depending on the data size.
        </p>
        <div class="modal-error" v-if="rebuildError">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ rebuildError }}</span>
        </div>
        <div class="option-group">
          <label>Minimum Papers:</label>
          <input type="number" v-model.number="rebuildOptions.minPapers" min="1" max="100" />
        </div>
        <div class="option-group">
          <label>PageRank Alpha:</label>
          <input type="number" v-model.number="rebuildOptions.alpha" min="0.1" max="0.99" step="0.05" />
        </div>
        <div class="option-group">
          <label>
            <input type="checkbox" v-model="rebuildOptions.useDisambiguation" />
            Enable Author Disambiguation
          </label>
        </div>
        <div class="option-group" v-if="rebuildOptions.useDisambiguation">
          <label>Similarity Threshold:</label>
          <input type="number" v-model.number="rebuildOptions.similarityThreshold" min="0" max="1" step="0.05" />
        </div>
        <div class="option-group">
          <label>Algorithm:</label>
          <select v-model="rebuildOptions.algorithm">
            <option value="networkx">NetworkX</option>
            <option value="igraph">IGraph</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showRebuildOptions = false">Cancel</button>
          <button class="start-analysis-btn" @click="confirmRebuild" :disabled="rebuilding">
            <svg viewBox="0 0 24 24" fill="currentColor" v-if="!rebuilding">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            <div class="btn-spinner" v-if="rebuilding"></div>
            <span v-if="rebuilding">Starting...</span>
            <span v-else>Start Analysis</span>
          </button>
        </div>
      </div>
    </div>

    <div class="loading-state" v-if="loading">
      <div class="spinner"></div>
      <p>Loading author rankings...</p>
    </div>

    <div class="error-state" v-if="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchAuthors">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M23 4v6h-6"/>
          <path d="M1 20v-6h6"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        Retry
      </button>
    </div>

    <div class="empty-state" v-if="!loading && !error && authors.length === 0">
      <p>No author data available.</p>
      <button class="start-analysis-btn empty-state-btn" @click="openRebuildOptions" v-if="!analysisStatus.running">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        Start Analysis
      </button>
    </div>

    <div class="authors-table" v-if="!loading && authors.length > 0">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Author</th>
            <th>Papers</th>
            <th>PageRank</th>
            <th>Degree</th>
            <th>Betweenness</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(author, index) in authors" :key="author.author_id">
            <td class="rank">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td class="author-name">
              <span class="name" @click="goToAuthor(author)">{{ author.name }}</span>
            </td>
            <td class="paper-count">{{ author.paper_count }}</td>
            <td class="metric">{{ formatMetric(author.pagerank) }}</td>
            <td class="metric">{{ formatMetric(author.degree_centrality) }}</td>
            <td class="metric">{{ formatMetric(author.betweenness_centrality) }}</td>
            <td class="category">
              <span class="category-tag" :style="{ backgroundColor: getCategoryColor(author.primary_category) }">
                {{ author.primary_category || 'N/A' }}
              </span>
            </td>
            <td class="actions">
              <button class="action-btn" @click="viewPapers(author)" title="View Papers">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 9 11"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="totalAuthors > pageSize">
      <button class="pagination-btn" @click="goToFirstPage" :disabled="currentPage === 1">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        First
      </button>
      <button class="pagination-btn" @click="goToPreviousPage" :disabled="currentPage === 1">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Previous
      </button>
      <div class="pagination-jump">
        <span class="pagination-info">Page {{ currentPage }}/{{ totalPages }}</span>
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
      <button class="pagination-btn" @click="goToNextPage" :disabled="currentPage >= totalPages">
        Next
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthorRanking } from '@/composables/useAuthorRanking'

const {
  authors,
  loading,
  error,
  selectedMetric,
  selectedCategory,
  currentPage,
  pageSize,
  totalAuthors,
  authorSearchQuery,
  analysisStatus,
  showRebuildOptions,
  rebuilding,
  rebuildError,
  rebuildOptions,
  jumpPageInput,
  categories,
  totalPages,
  progressPercent,
  fetchAuthors,
  confirmRebuild,
  openRebuildOptions,
  handleAuthorSearch,
  handleJumpPageInput,
  handleGoToPage,
  goToFirstPage,
  goToPreviousPage,
  goToNextPage,
  formatMetric,
  getCategoryColor,
  goToAuthor,
  viewPapers,
} = useAuthorRanking()
</script>

<style scoped>
.author-ranking-page {
  padding: 88px 24px 24px 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.total-count {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
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
  width: 280px;
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
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

.subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
}

.controls {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.metric-selector,
.category-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-selector label,
.category-filter label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.metric-selector select,
.category-filter select {
  padding: 8px 32px 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.refresh-btn {
  padding: 8px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rebuild-btn {
  padding: 8px 16px;
  background: #FF5722;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.rebuild-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-actions {
  display: flex;
  gap: 8px;
}

.rebuild-options {
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

.rebuild-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.rebuild-modal h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 1.25rem;
}

.option-group {
  margin-bottom: 16px;
}

.option-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.option-group input[type="number"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.option-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.option-group select {
  width: 100%;
  padding: 8px 32px 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.option-group select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 20px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: var(--bg-primary);
  border-color: var(--text-secondary);
}

.start-analysis-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  transition: all 0.3s ease;
}

.start-analysis-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.start-analysis-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.start-analysis-btn svg {
  width: 18px;
  height: 18px;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.confirm-btn {
  padding: 10px 20px;
  background: #FF5722;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-description {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.modal-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
  color: #f44336;
  font-size: 0.9rem;
}

.modal-error svg {
  width: 20px;
  height: 20px;
  stroke-width: 2;
  flex-shrink: 0;
}

.status-bar {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.progress-bar {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-color);
  transition: width 0.3s ease;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-secondary);
}

.empty-state-btn {
  margin-top: 20px;
}

.retry-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #FF5722 0%, #E64A19 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(255, 87, 34, 0.3);
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 87, 34, 0.4);
}

.retry-btn svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.authors-table {
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.authors-table table {
  width: 100%;
  border-collapse: collapse;
}

.authors-table th,
.authors-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.authors-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

.authors-table tr:hover {
  background: var(--bg-secondary);
}

.rank {
  font-weight: 600;
  color: var(--text-secondary);
  width: 60px;
}

.author-name .name {
  color: var(--accent-color);
  cursor: pointer;
}

.author-name .name:hover {
  text-decoration: underline;
}

.paper-count {
  font-weight: 500;
}

.metric {
  font-family: monospace;
  font-size: 0.85rem;
}

.category-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: white;
}

.actions {
  width: 80px;
}

.action-btn {
  padding: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.action-btn:hover {
  background: var(--bg-secondary);
  color: var(--accent-color);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 32px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn svg {
  width: 20px;
  height: 20px;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  min-width: 80px;
}

.pagination-input {
  padding: 6px 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  width: 60px;
  text-align: center;
}

.pagination-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.1);
}

.pagination-input::placeholder {
  color: var(--text-muted);
}
</style>
