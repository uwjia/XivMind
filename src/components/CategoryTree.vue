<template>
  <div class="category-tree">
    <!-- Current subject group -->
    <div class="group-section">
      <div
        class="tree-node root-node"
        :class="{ selected: selectedCategory === currentGroup?.wildcard }"
        @click="handleSelect(currentGroup?.wildcard || null)"
        :title="currentGroup?.name"
      >
        <div class="node-content">
          <svg class="folder-icon" viewBox="0 0 24 24" fill="none">
            <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" :fill="selectedCategory === currentGroup?.wildcard ? currentGroup?.color : currentGroup?.color + '80'" :stroke="currentGroup?.color" stroke-width="1.5"/>
          </svg>
          <span class="node-label">{{ currentGroup?.id?.toUpperCase() }}</span>
          <span class="node-count">{{ getGroupCount(currentGroup!) }}</span>
        </div>
        <svg
          class="expand-icon"
          :class="{ expanded: isGroupExpanded }"
          viewBox="0 0 24 24"
          fill="none"
          @click.stop="toggleGroup"
        >
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <Transition name="expand">
        <div v-show="isGroupExpanded" class="children-container">
          <div
            v-for="category in getGroupCategories(currentGroup!)"
            :key="category.id"
            class="tree-node child-node"
            :class="{ selected: selectedCategory === category.id }"
            @click="handleSelect(category.id)"
            :title="category.name"
          >
            <div class="node-content">
              <svg class="folder-icon" viewBox="0 0 24 24" fill="none">
                <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" :fill="getCategoryColor(category.id) + '40'" :stroke="getCategoryColor(category.id)" stroke-width="1.5"/>
              </svg>
              <span class="node-label">{{ getCategoryShortName(category.id) }}</span>
              <span class="node-count">{{ getCategoryCount(category.id) }}</span>
            </div>
          </div>

          <!-- Other categories (as sub-item under subject group) -->
          <div
            v-if="otherCount > 0"
            class="tree-node child-node other-node"
            :class="{ selected: selectedCategory === 'other' }"
            @click="handleSelect('other')"
            title="Other categories (primary category not in current subject)"
          >
            <div class="node-content">
              <svg class="folder-icon" viewBox="0 0 24 24" fill="none">
                <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" :fill="selectedCategory === 'other' ? '#9E9E9E' : '#9E9E9E80'" stroke="#9E9E9E" stroke-width="1.5"/>
              </svg>
              <span class="node-label">Other</span>
              <span class="node-count">{{ otherCount }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useConfigStore } from '@/stores/config-store'
import {
  CATEGORY_GROUPS,
  getCategoryShortName,
  getCategoryColor,
  isKnownCategory,
  type CategoryGroup,
} from '@/utils/categoryColors'

const props = defineProps<{
  selectedCategory: string | null
  categoryCounts: Record<string, number>
  totalPapers?: number  // Actual total papers in the view (for listings)
}>()

const emit = defineEmits<{
  select: [categoryId: string | null]
}>()

const configStore = useConfigStore()

// Get current subject group based on configuration
const currentGroup = computed<CategoryGroup | undefined>(() => {
  return CATEGORY_GROUPS.find(g => g.id === configStore.defaultSubject)
})

// Expanded state for current group (default expanded)
const isGroupExpanded = ref<boolean>(true)

const toggleGroup = () => {
  isGroupExpanded.value = !isGroupExpanded.value
}

// Get sub-categories under subject group (with paper counts)
const getGroupCategories = (group: CategoryGroup) => {
  const children = group.categories.filter(
    cat => (props.categoryCounts[cat.id] || 0) > 0
  )
  return children.sort((a, b) => {
    const countA = props.categoryCounts[a.id] || 0
    const countB = props.categoryCounts[b.id] || 0
    return countB - countA
  })
}

// Get total paper count for subject group
const getGroupCount = (group: CategoryGroup): number => {
  if (!group) return 0

  // If totalPapers is provided (for listings), use it directly
  if (props.totalPapers !== undefined) {
    return props.totalPapers
  }

  // Otherwise, sum category counts (for other views like Home)
  let count = 0
  for (const cat of group.categories) {
    count += props.categoryCounts[cat.id] || 0
  }
  return count
}

// Get paper count for single category
const getCategoryCount = (categoryId: string): number => {
  return props.categoryCounts[categoryId] || 0
}

// Other category count (primary category not in current subject)
const otherCount = computed(() => {
  const group = currentGroup.value
  if (!group) return 0

  // If totalPapers is provided, calculate Other as: totalPapers - sum of current subject categories
  if (props.totalPapers !== undefined) {
    let subjectCount = 0
    for (const cat of group.categories) {
      subjectCount += props.categoryCounts[cat.id] || 0
    }
    return props.totalPapers - subjectCount
  }

  // Otherwise, count papers whose primary category is not in current subject
  let count = 0
  for (const [categoryId, categoryCount] of Object.entries(props.categoryCounts)) {
    // Skip the wildcard entry
    if (categoryId === group.wildcard) continue

    // Check if primary category belongs to current subject
    const belongsToCurrentSubject = group.categories.some(cat => cat.id === categoryId)
    if (!belongsToCurrentSubject) {
      count += categoryCount
    }
  }
  return count
})

const handleSelect = (categoryId: string | null) => {
  if (props.selectedCategory === categoryId) {
    emit('select', null)
  } else {
    emit('select', categoryId)
  }
}
</script>

<style scoped>
.category-tree {
  padding: 12px 0;
  user-select: none;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.category-tree::-webkit-scrollbar {
  display: none;
}

.group-section {
  margin-bottom: 4px;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin: 2px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tree-node:hover {
  background: var(--bg-secondary);
}

.tree-node.selected {
  background: var(--accent-color)15;
}

.tree-node.selected .node-label {
  color: var(--accent-color);
  font-weight: 600;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.folder-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.node-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  font-family: 'Consolas', 'Monaco', monospace;
}

.node-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: auto;
}

.expand-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.expand-icon:hover {
  color: var(--text-primary);
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.children-container {
  margin-left: 16px;
  border-left: 1px solid var(--border-color);
  padding-left: 4px;
}

.child-node {
  padding: 6px 12px;
}

.child-node .folder-icon {
  width: 18px;
  height: 18px;
}

.child-node .node-label {
  font-size: 0.85rem;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 2000px;
}
</style>