import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
    },
    {
      path: '/inbox',
      name: 'inbox',
      component: () => import('@/views/Inbox.vue'),
    },
    {
      path: '/notes/:id',
      name: 'note',
      component: () => import('@/views/NoteView.vue'),
      props: true,
    },
    {
      path: '/containers/:id',
      name: 'container',
      component: () => import('@/views/ContainerView.vue'),
      props: true,
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
  ],
})

export default router
