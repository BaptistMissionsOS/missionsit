// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/missionaries', name: 'Missionaries', component: () => import('./pages/Missionaries.vue') },
  {
    path: '/missionaries/:slug',
    name: 'Missionary',
    component: () => import('./pages/Missionary.vue'),
    props: true,
  },
  { path: '/trips', name: 'Trips', component: () => import('./pages/Trips.vue') },
  { path: '/give', name: 'Give', component: () => import('./pages/Give.vue') },
  { path: '/portal', name: 'Portal', component: () => import('./pages/Portal.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./pages/NotFound.vue') },
]

export default createRouter({
  history: createWebHistory('/missions'),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})
