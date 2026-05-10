import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import pinia from './store'
import { refreshSession } from './services/auth.js'
import { setupI18n } from './i18n'
import { configureApiClient } from './services/http'
import { useAuthStore } from './store/auth'

import './style.css'

const app = createApp(App)
const i18n = setupI18n()
const authStore = useAuthStore(pinia)

app.use(i18n)
app.use(router)
app.use(pinia)

configureApiClient({
  getToken: () => authStore.token,
  refreshAccessToken: async () => {
    if (!authStore.refreshToken) {
      return ''
    }

    const payload = await refreshSession({
      refreshToken: authStore.refreshToken
    })

    authStore.setAuth({
      ...payload,
      userInfo: authStore.userInfo
    })

    return payload.accessToken || payload.token || ''
  },
  onUnauthorized: () => {
    authStore.clearAuth()

    if (router.currentRoute.value.path !== '/login') {
      router.push({
        path: '/login',
        query: {
          redirect: router.currentRoute.value.fullPath
        }
      })
    }
  }
})

app.mount('#app')
