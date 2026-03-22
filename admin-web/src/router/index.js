import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

import pinia from '../store/index.js'
import { useAuthStore } from '../store/auth.js'
import DashboardPage from '../views/DashboardPage.vue'
import LoginPage from '../views/LoginPage.vue'
import NewsEditorPage from '../views/NewsEditorPage.vue'
import NewsManagementPage from '../views/NewsManagementPage.vue'
import CategoriesPage from '../views/CategoriesPage.vue'
import UsersPage from '../views/UsersPage.vue'
import AdminLayout from '../views/layout/AdminLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: {
      title: '后台登录',
      guestOnly: true,
    },
  },
  {
    path: '/',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: '/dashboard',
        name: 'dashboard',
        component: DashboardPage,
        meta: { title: '仪表盘', requiresAuth: true },
      },
      {
        path: '/news',
        name: 'news',
        component: NewsManagementPage,
        meta: { title: '新闻管理', requiresAuth: true },
      },
      {
        path: '/news/create',
        name: 'news-create',
        component: NewsEditorPage,
        meta: { title: '创建新闻', requiresAuth: true },
      },
      {
        path: '/news/:id/edit',
        name: 'news-edit',
        component: NewsEditorPage,
        meta: { title: '编辑新闻', requiresAuth: true },
      },
      {
        path: '/categories',
        name: 'categories',
        component: CategoriesPage,
        meta: { title: '分类管理', requiresAuth: true },
      },
      {
        path: '/users',
        name: 'users',
        component: UsersPage,
        meta: { title: '用户管理', requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const authStore = useAuthStore(pinia)

  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      return {
        path: '/login',
        query: {
          redirect: to.fullPath,
        },
      }
    }

    if (!authStore.isAdmin) {
      authStore.clearSession()
      ElMessage.error('当前账号没有后台权限')
      return {
        path: '/login',
      }
    }
  }

  if (to.meta.guestOnly && authStore.isLoggedIn && authStore.isAdmin) {
    return { path: '/dashboard' }
  }

  return true
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '管理后台'} - 头条新闻管理后台`
})

export default router
