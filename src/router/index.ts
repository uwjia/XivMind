import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/Search.vue')
  },
  {
    path: '/paper/:id',
    name: 'PaperDetail',
    component: () => import('@/views/PaperDetail.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue')
  },
  {
    path: '/bookmarks',
    name: 'Bookmarks',
    component: () => import('@/views/Bookmarks.vue')
  },
  {
    path: '/downloads',
    name: 'Downloads',
    component: () => import('@/views/Downloads.vue')
  },
  {
    path: '/assistant',
    name: 'Assistant',
    component: () => import('@/views/Assistant.vue')
  },
  {
    path: '/data-manager',
    name: 'DataManager',
    component: () => import('@/views/DataManager.vue')
  },
  {
    path: '/skills',
    name: 'SkillManager',
    component: () => import('@/views/SkillManager.vue')
  },
  {
    path: '/subagents',
    name: 'SubAgentManager',
    component: () => import('@/views/SubAgentManager.vue')
  },
  {
    path: '/memory',
    name: 'Memory',
    component: () => import('@/views/Memory.vue')
  },
  {
    path: '/team',
    name: 'TeamManager',
    component: () => import('@/views/TeamManager.vue')
  },
  {
    path: '/reader/:paperId',
    name: 'PdfReader',
    component: () => import('@/components/pdf-reader/PdfReader.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

export default router
