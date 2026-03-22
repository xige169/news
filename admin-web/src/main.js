import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus'

import App from './App.vue'
import { refreshAdminToken } from './services/auth.js'
import { configureApiClient } from './services/http.js'
import pinia from './store/index.js'
import { useAuthStore } from './store/auth.js'
import router from './router/index.js'
import './style.css'

const app = createApp(App)

const authStore = useAuthStore(pinia)

configureApiClient({
  getToken: () => authStore.accessToken,
  refreshAccessToken: async () => {
    if (!authStore.refreshToken) {
      authStore.clearSession()
      return ''
    }

    const payload = await refreshAdminToken(authStore.refreshToken)
    authStore.setSession({
      ...payload,
      userInfo: authStore.userInfo,
    })
    return authStore.accessToken
  },
  onUnauthorized: () => {
    authStore.clearSession()
    if (router.currentRoute.value.path !== '/login') {
      ElMessage.error('登录状态已失效，请重新登录')
      router.push('/login')
    }
  },
})

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
