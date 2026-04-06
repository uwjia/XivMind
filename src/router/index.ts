import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import { ROUTES, ROUTE_NAMES } from '@/constants/routes'

const routes: RouteRecordRaw[] = [
  {
    path: ROUTES.HOME,
    name: ROUTE_NAMES.HOME,
    component: () => import('@/views/Home.vue')
  },
  {
    path: ROUTES.SEARCH,
    name: ROUTE_NAMES.SEARCH,
    component: () => import('@/views/Search.vue')
  },
  {
    path: ROUTES.PAPER_DETAIL,
    name: ROUTE_NAMES.PAPER_DETAIL,
    component: () => import('@/views/PaperDetail.vue')
  },
  {
    path: ROUTES.SETTINGS,
    name: ROUTE_NAMES.SETTINGS,
    component: () => import('@/views/Settings.vue')
  },
  {
    path: ROUTES.BOOKMARKS,
    name: ROUTE_NAMES.BOOKMARKS,
    component: () => import('@/views/Bookmarks.vue')
  },
  {
    path: ROUTES.FOLLOWED_AUTHORS,
    name: ROUTE_NAMES.FOLLOWED_AUTHORS,
    component: () => import('@/views/FollowedAuthors.vue')
  },
  {
    path: ROUTES.DOWNLOADS,
    name: ROUTE_NAMES.DOWNLOADS,
    component: () => import('@/views/Downloads.vue')
  },
  {
    path: ROUTES.ASSISTANT,
    name: ROUTE_NAMES.ASSISTANT,
    component: () => import('@/views/Assistant.vue')
  },
  {
    path: ROUTES.AUTHOR_RANKING,
    name: ROUTE_NAMES.AUTHOR_RANKING,
    component: () => import('@/views/AuthorRanking.vue')
  },
  {
    path: ROUTES.DATA_MANAGER,
    name: ROUTE_NAMES.DATA_MANAGER,
    component: () => import('@/views/DataManager.vue')
  },
  {
    path: ROUTES.SKILLS,
    name: ROUTE_NAMES.SKILLS,
    component: () => import('@/views/SkillManager.vue')
  },
  {
    path: ROUTES.SUBAGENTS,
    name: ROUTE_NAMES.SUBAGENTS,
    component: () => import('@/views/SubAgentManager.vue')
  },
  {
    path: ROUTES.MEMORY,
    name: ROUTE_NAMES.MEMORY,
    component: () => import('@/views/Memory.vue')
  },
  {
    path: ROUTES.TEAM,
    name: ROUTE_NAMES.TEAM,
    component: () => import('@/views/TeamManager.vue')
  },
  {
    path: ROUTES.READER,
    name: ROUTE_NAMES.READER,
    component: () => import('@/components/pdf-reader/PdfReader.vue')
  },
  {
    path: ROUTES.AUTHOR_PAPERS,
    name: ROUTE_NAMES.AUTHOR_PAPERS,
    component: () => import('@/views/AuthorPapers.vue'),
    props: true
  },
  {
    path: ROUTES.AUTHOR_PROFILE,
    name: ROUTE_NAMES.AUTHOR_PROFILE,
    component: () => import('@/views/AuthorProfile.vue'),
    props: true
  },
  {
    path: ROUTES.DAILY_ANALYSIS,
    name: ROUTE_NAMES.DAILY_ANALYSIS,
    component: () => import('@/views/DailyAnalysis.vue'),
    props: true
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
