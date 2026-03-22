import { createRouter, createWebHistory } from 'vue-router'

import pinia from '../store'
import { useAuthStore } from '../store/auth'
import FavoritesPage from '../views/FavoritesPage.vue'
import HistoryPage from '../views/HistoryPage.vue'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import NewsDetailPage from '../views/NewsDetailPage.vue'
import ProfileEditPage from '../views/ProfileEditPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import ProfilePasswordPage from '../views/ProfilePasswordPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import SearchPage from '../views/SearchPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: {
      title: '首页',
      showTabBar: true
    }
  },
  {
    path: '/news/:id',
    name: 'news-detail',
    component: NewsDetailPage,
    meta: {
      title: '新闻详情'
    }
  },
  {
    path: '/search',
    name: 'search',
    component: SearchPage,
    meta: {
      title: '搜索',
      showTabBar: true
    }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: {
      title: '登录',
      guestOnly: true
    }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: {
      title: '注册',
      guestOnly: true
    }
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: FavoritesPage,
    meta: {
      title: '我的收藏',
      requiresAuth: true,
      showTabBar: true
    }
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryPage,
    meta: {
      title: '浏览历史',
      requiresAuth: true,
      showTabBar: true
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: {
      title: '个人中心',
      requiresAuth: true,
      showTabBar: true
    }
  },
  {
    path: '/profile/edit',
    name: 'profile-edit',
    component: ProfileEditPage,
    meta: {
      title: '编辑资料',
      requiresAuth: true
    }
  },
  {
    path: '/profile/password',
    name: 'profile-password',
    component: ProfilePasswordPage,
    meta: {
      title: '修改密码',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const authStore = useAuthStore(pinia)

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath
      }
    }
  }

  if (to.meta.guestOnly && authStore.isLoggedIn) {
    return {
      path: '/'
    }
  }

  return true
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '新闻'} - 新闻客户端`
})

export default router
