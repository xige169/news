import { createApp } from 'vue'
import {
  Button,
  Cell,
  CellGroup,
  Empty,
  Field,
  Form,
  Grid,
  GridItem,
  Icon,
  Image,
  List,
  NavBar,
  Popup,
  PullRefresh,
  Tab,
  Tabbar,
  TabbarItem,
  Tabs
} from 'vant'

import App from './App.vue'
import router from './router'
import pinia from './store'
import { setupI18n } from './i18n'
import { configureApiClient } from './services/http'
import { useAuthStore } from './store/auth'
import { useThemeStore } from './store/theme'

import 'vant/lib/index.css'
import './style.css'

const app = createApp(App)
const i18n = setupI18n()
const authStore = useAuthStore(pinia)

app.use(i18n)
app.use(router)
app.use(pinia)
app.use(Button)
app.use(NavBar)
app.use(Tabbar)
app.use(TabbarItem)
app.use(Tab)
app.use(Tabs)
app.use(List)
app.use(PullRefresh)
app.use(Cell)
app.use(CellGroup)
app.use(Grid)
app.use(GridItem)
app.use(Empty)
app.use(Form)
app.use(Field)
app.use(Image)
app.use(Icon)
app.use(Popup)

const themeStore = useThemeStore(pinia)
themeStore.initTheme()

configureApiClient({
  getToken: () => authStore.token,
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
