import { createRouter, createWebHistory } from 'vue-router'
import NotFound from '@/views/NotFound.vue'

const ProgressionAnalyzerView = () => import('@/views/ProgressionAnalyzerView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'progression_analyzer',
      meta: { requiresAuth: false },
      component: ProgressionAnalyzerView
    },
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
  ]
})

export default router
