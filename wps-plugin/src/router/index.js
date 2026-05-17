import { createRouter, createWebHashHistory } from 'vue-router'
//import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history:  createWebHashHistory(''),
  routes: [
    {
      path: '/',
      name: '默认页',
      component: () => import('../components/Root.vue')
    },
    {
      path: '/login',
      name: '登录',
      component: () => import('../components/Login.vue')
    },
    {
      path: '/dialog',
      name: '对话框',
      component: () => import('../components/Dialog.vue')
    },
    {
      path: '/taskpane',
      name: '任务窗格',
      component: () => import('../components/TaskPane.vue')
    },
    {
      path: '/aichat',
      name: 'AI助手',
      component: () => import('../views/AIChatView.vue')
    }
  ]
})

export default router
