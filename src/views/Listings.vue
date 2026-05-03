<template>
  <div class="listings">
    <div class="content">
      <div class="content-header">
        <div class="header-row">
          <div class="tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'new' }"
              @click="switchTab('new')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
              New
              <span class="tab-count">{{ totalCounts.new }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'cross' }"
              @click="switchTab('cross')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/>
              </svg>
              Cross
              <span class="tab-count">{{ totalCounts.cross }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'replacement' }"
              @click="switchTab('replacement')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              Replacement
              <span class="tab-count">{{ totalCounts.replacement }}</span>
            </button>
          </div>
          <div class="header-actions">
            <div class="date-picker-container">
              <button 
                class="icon-btn date-picker-btn" 
                :class="{ active: selectedDate }" 
                @click="toggleDatePicker"
                type="button"
                title="Select date to view historical listings"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
              </button>
              <input 
                ref="dateInputRef"
                type="date" 
                v-model="selectedDate" 
                @change="onDateChange"
                class="date-picker-input"
                title="Select date to view historical listings"
              />
            </div>
            <button 
              class="icon-btn fetch-btn" 
              @click="fetchAndRefresh" 
              :disabled="isFetchingListings" 
              title="Fetch New Listings from arXiv"
            >
              <svg v-if="!isFetchingListings" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
            </button>
            <button class="icon-btn filter-btn" @click="toggleFilterDrawer" :title="isFilterDrawerOpen ? 'Hide categories' : 'Show categories'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" fill="currentColor" fill-opacity="0.2"/>
              </svg>
            </button>
            <button class="icon-btn toggle-btn" @click="configStore.setUseSimpleCard(!configStore.useSimpleCard)" :title="configStore.useSimpleCard ? 'Switch to detailed view' : 'Switch to simple view'">
              <svg v-if="configStore.useSimpleCard" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="3" y1="15" x2="21" y2="15"/>
                <line x1="9" y1="9" x2="9" y2="15"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="5" rx="1"/>
                <rect x="3" y="10" width="18" height="5" rx="1"/>
                <rect x="3" y="17" width="18" height="4" rx="1"/>
              </svg>
            </button>
            <button class="icon-btn code-filter-btn" :class="{ active: filterHasCodeUrl }" @click="toggleCodeUrlFilter" :title="filterHasCodeUrl ? 'Show all papers' : 'Filter papers with code'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="16 18 22 12 16 6"/>
                <polyline points="8 6 2 12 8 18"/>
              </svg>
            </button>
            <button class="icon-btn refresh-btn" @click="handleRefresh" :disabled="isLoadingListings" title="Refresh listings">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>
          </div>
        </div>
        <p v-if="listingsDate" class="date-info">
          {{ listingsDate }}
          <span class="total-count">Total: {{ totalCounts.new + totalCounts.cross + totalCounts.replacement }}</span>
        </p>
      </div>

      <div v-if="isLoadingListings" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading listings...</p>
      </div>

      <div v-else-if="listingsError" class="error-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p>{{ listingsError }}</p>
        <button class="retry-btn" @click="handleRefresh">Retry</button>
      </div>

      <div v-else class="papers-grid">
        <PaperCard
          v-for="(paper, index) in currentPapers"
          :key="paper.id"
          :paper="paper"
          :index="(currentPage - 1) * pageSize + index + 1"
        />
      </div>

      <div v-if="!isLoadingListings && !listingsError && totalItems > 0" class="pagination">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1" 
          @click="goToPage(currentPage - 1)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-num"
            :class="{ active: page === currentPage, ellipsis: page === '...' }"
            :disabled="page === '...'"
            @click="page !== '...' && goToPage(page as number)"
          >
            {{ page }}
          </button>
        </div>
        <button 
          class="page-btn" 
          :disabled="currentPage >= totalPages" 
          @click="goToPage(currentPage + 1)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        <div class="page-jump">
          <span>Go to</span>
          <input 
            type="number" 
            v-model.number="pageInput" 
            :min="1" 
            :max="totalPages"
            @keyup.enter="jumpToPage"
            @blur="jumpToPage"
            class="page-input"
          />
          <span>/ {{ totalPages }}</span>
        </div>
        <span class="page-info">
          {{ totalItems }} items
        </span>
        <div class="page-size-selector">
          <select 
            :value="pageSize" 
            @change="changePageSize(Number(($event.target as HTMLSelectElement).value))"
            class="page-size-select"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">
              {{ size }} / page
            </option>
          </select>
        </div>
      </div>

      <div v-if="!isLoadingListings && !listingsError && currentPapers.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9.172 16.172a4 4 0 0 1-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
        </svg>
        <p>No papers found</p>
      </div>
    </div>

    <ScrollTopButton />

    <CategoryDrawer
      :is-open="isFilterDrawerOpen"
      :selected-category="filterCategory"
      :category-counts="categoryCounts"
      @close="closeFilterDrawer"
      @select="handleFilterCategorySelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config-store'
import { useListings } from '@/composables/useListings'
import PaperCard from '@/components/PaperCard.vue'
import ScrollTopButton from '@/components/ScrollTopButton.vue'
import CategoryDrawer from '@/components/CategoryDrawer.vue'

const configStore = useConfigStore()

const dateInputRef = ref<HTMLInputElement | null>(null)

const toggleDatePicker = () => {
  if (dateInputRef.value) {
    try {
      if ('showPicker' in dateInputRef.value && typeof dateInputRef.value.showPicker === 'function') {
        dateInputRef.value.showPicker()
      } else {
        dateInputRef.value.click()
      }
    } catch (e) {
      dateInputRef.value.click()
    }
  }
}

const {
  isFetchingListings,
  isLoadingListings,
  listingsError,
  listingsDate,
  fetchAndRefresh,
  activeTab,
  selectedDate,
  currentPage,
  pageSize,
  pageSizeOptions,
  totalItems,
  totalCounts,
  currentPapers,
  pageInput,
  totalPages,
  visiblePages,
  switchTab,
  changePageSize,
  goToPage,
  jumpToPage,
  handleRefresh,
  onDateChange,
  initListings,
  filterCategory,
  categoryCounts,
  isFilterDrawerOpen,
  toggleFilterDrawer,
  closeFilterDrawer,
  handleFilterCategorySelect,
  filterHasCodeUrl,
  toggleCodeUrlFilter
} = useListings()

onMounted(() => {
  initListings()
})
</script>

<style scoped>
.listings {
  min-height: 100vh;
  padding-top: 64px;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 10px 20px;
}

.content-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 32px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.tab-btn.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.tab-btn svg {
  width: 18px;
  height: 18px;
}

.tab-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
}

.tab-btn:not(.active) .tab-count {
  background: var(--bg-tertiary);
}

.date-info {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-count {
  background: var(--bg-tertiary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-picker-container {
  position: relative;
  display: inline-block;
}

.date-picker-input {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 1px;
  padding: 0;
  margin: -5px 0px;
  opacity: 0;
  pointer-events: none;
}

.icon-btn.date-picker-btn {
  color: var(--icon-date);
  border-color: color-mix(in srgb, var(--icon-date) 20%, transparent);
}

.icon-btn.date-picker-btn:hover {
  background: color-mix(in srgb, var(--icon-date) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-date) 40%, transparent);
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.icon-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.icon-btn:hover svg {
  transform: scale(1.1);
}

.toggle-btn {
  color: var(--icon-toggle);
  border-color: color-mix(in srgb, var(--icon-toggle) 20%, transparent);
}

.toggle-btn:hover {
  background: color-mix(in srgb, var(--icon-toggle) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-toggle) 40%, transparent);
}

.code-filter-btn {
  color: var(--icon-code);
  border-color: color-mix(in srgb, var(--icon-code) 20%, transparent);
}

.code-filter-btn:hover {
  background: color-mix(in srgb, var(--icon-code) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-code) 40%, transparent);
}

.code-filter-btn.active {
  background: color-mix(in srgb, var(--icon-code) 20%, transparent);
  border-color: var(--icon-code);
  color: var(--icon-code);
}

.filter-btn {
  color: var(--icon-filter);
  border-color: color-mix(in srgb, var(--icon-filter) 20%, transparent);
}

.filter-btn:hover {
  background: color-mix(in srgb, var(--icon-filter) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-filter) 40%, transparent);
}

.refresh-btn {
  color: var(--icon-refresh);
  border-color: color-mix(in srgb, var(--icon-refresh) 20%, transparent);
}

.refresh-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--icon-refresh) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-refresh) 40%, transparent);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fetch-btn {
  color: var(--icon-downloads);
  border-color: color-mix(in srgb, var(--icon-downloads) 20%, transparent);
}

.fetch-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--icon-downloads) 10%, transparent);
  border-color: color-mix(in srgb, var(--icon-downloads) 40%, transparent);
}

.fetch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fetch-btn .spinner {
  animation: spin 1s linear infinite;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.loading-spinner {
  width: 48px;
  height: 48px;
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

.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.error-state svg {
  width: 60px;
  height: 60px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--icon-error);
}

.error-state p {
  font-size: 1.1rem;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 10px 24px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
}

.retry-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-color);
}

.papers-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 32px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  min-width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-num:hover:not(:disabled):not(.ellipsis):not(.active) {
  background: var(--bg-primary);
  border-color: var(--accent-color);
}

.page-num.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.page-num.active:hover {
  filter: brightness(1.1);
}

.page-num.ellipsis {
  border: none;
  background: transparent;
  cursor: default;
}

.page-info {
  margin-left: 12px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.page-size-selector {
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--border-color);
}

.page-size-select {
  padding: 6px 28px 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.page-size-select:hover {
  border-color: var(--accent-color);
}

.page-size-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-color) 20%, transparent);
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--border-color);
}

.page-jump span {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.page-input {
  width: 60px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.85rem;
  text-align: center;
  transition: all 0.3s ease;
}

.page-input:hover {
  border-color: var(--accent-color);
}

.page-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-color) 20%, transparent);
}

.page-input::-webkit-outer-spin-button,
.page-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.page-input[type=number] {
  -moz-appearance: textfield;
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

.empty-state p {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .tabs {
    flex-wrap: wrap;
  }

  .tab-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 12px;
  }

  .page-info {
    width: 100%;
    text-align: center;
    margin-left: 0;
    margin-top: 8px;
  }
}
</style>
