<template>
  <div id="app" :class="{ dark: isDark }">
    <Header />
    <Sidebar />
    <main class="main-content" :class="{ 'sidebar-collapsed': isCollapsed }">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>
    <Toast
      :visible="toastVisible"
      :message="toastMessage"
      :type="toastType"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useThemeStore } from './stores/theme-store'
import { useSidebarStore } from './stores/sidebar-store'
import { useToastStore } from './stores/toast-store'
import { useConfigStore } from './stores/config-store'
import { useLLMStore } from './stores/llm-store'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import Toast from './components/Toast.vue'

const themeStore = useThemeStore()
const sidebarStore = useSidebarStore()
const toastStore = useToastStore()
const configStore = useConfigStore()
const llmStore = useLLMStore()

const isDark = computed(() => themeStore.isDark)
const isCollapsed = computed(() => sidebarStore.isCollapsed)
const toastVisible = computed(() => toastStore.visible)
const toastMessage = computed(() => toastStore.message)
const toastType = computed(() => toastStore.type)

onMounted(() => {
  themeStore.initTheme()
  configStore.initConfig()
  llmStore.init()
})
</script>

<style scoped>
.main-content {
  margin-left: 224px;
  min-height: calc(100vh - 64px);
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 64px;
}

@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
