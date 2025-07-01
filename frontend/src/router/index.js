import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Feeds from '@/views/Feeds.vue'
import Config from '@/views/Config.vue'
import History from '@/views/History.vue'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
      },
      {
        path: 'feeds',
        name: 'Feeds',
        component: Feeds,
      },
      {
        path: 'config',
        name: 'Config',
        component: Config,
      },
      {
        path: 'history',
        name: 'History',
        component: History,
      }
    ],
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router