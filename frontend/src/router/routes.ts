import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('pages/main.vue')
  },
  {
    path: '/event/:id',
    name: 'Event',
    component: () => import('pages/event.vue')
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/error-page.vue')
  }
]

export default routes
