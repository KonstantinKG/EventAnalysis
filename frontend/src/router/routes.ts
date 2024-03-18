import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/default.vue'),
    redirect: '/events',
    children: [
      { path: '/events', component: () => import('pages/main.vue') },
      {
        path: '/events/:id',
        name: 'Event',
        component: () => import('pages/event.vue')
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/error-page.vue')
  }
]

export default routes
