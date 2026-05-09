import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'DocumentList',
        component: () => import('../views/admin/DocumentList.vue')
      },
      {
        path: 'document/:id',
        name: 'DocumentEdit',
        component: () => import('../views/admin/DocumentEdit.vue')
      },
      {
        path: 'document/new',
        name: 'DocumentNew',
        component: () => import('../views/admin/DocumentEdit.vue')
      },
      {
        path: 'knowledge-base',
        name: 'KnowledgeBase',
        component: () => import('../views/admin/KnowledgeBase.vue')
      },
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('../views/admin/Permissions.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/admin/Settings.vue')
      }
    ]
  },
  {
    path: '/wiki',
    name: 'Wiki',
    component: () => import('../views/wiki/WikiLayout.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router