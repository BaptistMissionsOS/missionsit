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
  { path: '/directory', name: 'Directory', component: () => import('./pages/Directory.vue') },
  { path: '/give', name: 'Give', component: () => import('./pages/Give.vue') },
  {
    path: '/portal',
    component: () => import('./components/PortalLayout.vue'),
    children: [
      { path: '', name: 'Portal', component: () => import('./pages/PortalHome.vue') },
      { path: 'trips', name: 'Trips', component: () => import('./pages/Trips.vue') },
      { path: ':module', name: 'Module', component: () => import('./pages/ModulePage.vue'), props: true },
      {
        path: ':module/:doctype/:name',
        name: 'Record',
        component: () => import('./pages/RecordPage.vue'),
        props: true,
      },
    ],
  },
  // Trips moved into the Member Portal; keep old links working.
  { path: '/trips', redirect: (to) => ({ path: '/portal/trips', hash: to.hash }) },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./pages/NotFound.vue') },
]

export default createRouter({
  history: createWebHistory('/missions'),
  routes,
  // Trips scrolls to its own #trip once the list has loaded; other hashes are on the page already.
  scrollBehavior: (to, from, saved) =>
    saved || (to.hash ? (to.name === 'Trips' ? false : { el: to.hash, top: 88 }) : { top: 0 }),
})
