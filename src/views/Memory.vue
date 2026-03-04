<template>
  <div class="memory-page">
    <div class="page-header">
      <div class="header-text">
        <h1>Memory</h1>
        <p class="subtitle">Manage your AI's long-term memory for personalized experience</p>
      </div>
    </div>

    <div class="memory-content">
      <div class="memory-stats" v-if="memoryStore.stats">
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.total_memories }}</div>
          <div class="stat-label">Total Memories</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.recall_memory_count }}</div>
          <div class="stat-label">Conversations</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ memoryStore.stats.archival_memory_count }}</div>
          <div class="stat-label">Notes</div>
        </div>
      </div>

      <div class="memory-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="tab-icon" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <MemoryConfigTab v-if="activeTab === 'config'" />
        <MemoryProfileTab v-else-if="activeTab === 'profile'" />
        <MemoryKnowledgeTab v-else-if="activeTab === 'knowledge'" />
        <MemoryHistoryTab v-else-if="activeTab === 'history'" />
        <MemoryDangerTab v-else-if="activeTab === 'danger'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, watch, h } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useMemoryStore } from '@/stores/memory-store'
import {
  MemoryConfigTab,
  MemoryProfileTab,
  MemoryKnowledgeTab,
  MemoryHistoryTab,
  MemoryDangerTab,
} from '@/components/memory'

const memoryStore = useMemoryStore()

type TabId = 'config' | 'profile' | 'knowledge' | 'history' | 'danger'

const activeTab = ref<TabId>('config')

const tabs: { id: TabId; label: string; icon: ReturnType<typeof h> }[] = [
  { id: 'config', label: 'Config', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('circle', { cx: '12', cy: '12', r: '3' }),
    h('path', { d: 'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z' }),
  ])},
  { id: 'profile', label: 'Profile', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '12', cy: '7', r: '4' }),
  ])},
  { id: 'knowledge', label: 'Knowledge', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
    h('polyline', { points: '14 2 14 8 20 8' }),
  ])},
  { id: 'history', label: 'History', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('polyline', { points: '12 6 12 12 16 14' }),
  ])},
  { id: 'danger', label: 'Danger', icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
    h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
    h('line', { x1: '12', y1: '9', x2: '12', y2: '13' }),
    h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' }),
  ])},
]

watch(activeTab, async (newTab) => {
  if (newTab === 'history' && memoryStore.recallMemories.length === 0) {
    await memoryStore.fetchRecallMemories()
  } else if (newTab === 'knowledge' && memoryStore.archivalMemories.length === 0) {
    await memoryStore.fetchArchivalMemories()
  }
})

onMounted(async () => {
  await memoryStore.init()
})

onActivated(async () => {
  await memoryStore.init()
  if (activeTab.value === 'history') {
    await memoryStore.fetchRecallMemories()
  } else if (activeTab.value === 'knowledge') {
    await memoryStore.fetchArchivalMemories()
  }
})

onBeforeRouteLeave(() => {
  memoryStore.searchResults = []
})
</script>

<style scoped>
.memory-page {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-text h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.header-text .subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

.memory-content {
  padding: 0;
}

.memory-stats {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  margin-bottom: 24px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--accent-color);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.memory-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}

.tab-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.tab-btn.active {
  color: white;
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.tab-icon {
  width: 16px;
  height: 16px;
}

.tab-content {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

@media (max-width: 768px) {
  .header-text h1 {
    font-size: 1.25rem;
  }

  .memory-stats {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>
