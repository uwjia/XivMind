import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import PaperDetail from '../views/PaperDetail.vue'
import Settings from '../views/Settings.vue'
import Bookmarks from '../views/Bookmarks.vue'
import Downloads from '../views/Downloads.vue'
import Assistant from '../views/Assistant.vue'
import DataManager from '../views/DataManager.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  },
  {
    path: '/paper/:id',
    name: 'PaperDetail',
    component: PaperDetail
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/bookmarks',
    name: 'Bookmarks',
    component: Bookmarks
  },
  {
    path: '/downloads',
    name: 'Downloads',
    component: Downloads
  },
  {
    path: '/assistant',
    name: 'Assistant',
    component: Assistant
  },
  {
    path: '/data-manager',
    name: 'DataManager',
    component: DataManager
  }
]

const router = createRouter({
  history: createWebHistory(),
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
