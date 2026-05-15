import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue'),
  },
  {
    path: '/review',
    name: 'Review',
    component: () => import('./views/Review.vue'),
  },
  {
    path: '/experts',
    name: 'Experts',
    component: () => import('./views/Experts.vue'),
  },
  {
    path: '/skills',
    name: 'Skills',
    component: () => import('./views/Skills.vue'),
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('./views/Knowledge.vue'),
  },
  {
    path: '/cases',
    name: 'Cases',
    component: () => import('./views/Cases.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
