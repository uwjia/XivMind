<template>
  <div class="team-manager">
    <TaskView 
      v-if="activeView === 'task'"
      @notify="showNotification"
      @change-view="activeView = $event"
    />

    <div v-if="activeView === 'workflow'" class="workflow-view">
      <WorkflowEditor 
        :active-view="activeView"
        @change-view="activeView = $event"
      />
    </div>

    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, onDeactivated } from 'vue'
import { useTeam } from '@/composables/useTeam'
import { useSidebarStore } from '@/stores/sidebar-store'
import TaskView from '@/components/team/TaskView.vue'
import WorkflowEditor from '@/components/team/WorkflowEditor.vue'

const sidebarStore = useSidebarStore()

const {
  loadStats,
} = useTeam()

const notification = ref<{ type: string; message: string } | null>(null)
const activeView = ref<'task' | 'workflow'>('workflow')

const showNotification = (type: string, message: string) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

onMounted(() => {
  loadStats()
})

onActivated(() => {
  sidebarStore.enterForceCollapse()
})

onDeactivated(() => {
  sidebarStore.exitForceCollapse()
})
</script>

<style scoped>
.team-manager {
  padding: 0;
  max-width: 100%;
  margin: 0;
  min-height: 100vh;
  padding-top: 64px;
}

.team-manager:has(.task-view) {
  padding: 88px 24px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.workflow-view {
  height: calc(100vh - 64px);
  background: var(--bg-secondary);
  overflow: hidden;
  border: none;
}

.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background: #10B981;
  color: white;
}

.notification.error {
  background: #EF4444;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
