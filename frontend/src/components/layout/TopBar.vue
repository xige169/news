<template>
  <header class="top-bar">
    <div class="top-bar__inner">
      <router-link to="/" class="top-bar__logo">
        <span class="top-bar__logo-text">新闻</span>
      </router-link>

      <nav class="top-bar__nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="top-bar__nav-link"
          :class="{ 'top-bar__nav-link--active': isActive(item.path) }"
        >
          {{ item.label }}
        </router-link>

        <n-popselect
          v-if="categories.length"
          v-model:value="activeCategoryId"
          :options="categoryOptions"
          trigger="click"
          @update:value="onCategorySelect"
        >
          <button class="top-bar__nav-link top-bar__nav-link--button" type="button">
            分类 <span class="top-bar__caret">▾</span>
          </button>
        </n-popselect>
      </nav>

      <div class="top-bar__search">
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索新闻"
          clearable
          @keydown.enter="onSubmitSearch"
        >
          <template #prefix>
            <span class="top-bar__search-icon">🔍</span>
          </template>
        </n-input>
      </div>

      <div class="top-bar__auth">
        <template v-if="auth.isLoggedIn">
          <n-dropdown
            trigger="click"
            :options="userMenuOptions"
            placement="bottom-end"
            @select="onUserMenu"
          >
            <button class="top-bar__user" type="button">
              <span class="top-bar__avatar">{{ avatarInitial }}</span>
              <span class="top-bar__username">{{ auth.username || '我的' }}</span>
            </button>
          </n-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="top-bar__auth-link">登录</router-link>
          <span class="top-bar__sep">/</span>
          <router-link to="/register" class="top-bar__auth-link">注册</router-link>
        </template>
      </div>

      <button
        class="top-bar__menu-trigger"
        type="button"
        aria-label="打开菜单"
        @click="emit('open-drawer')"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDropdown, NInput, NPopselect, useMessage } from 'naive-ui'

import { useAuthStore } from '../../store/auth'
import { fetchCategories } from '../../services/news'
import { logoutSession } from '../../services/auth'

const emit = defineEmits(['open-drawer'])

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const message = useMessage()

const navItems = [
  { path: '/', label: '首页' },
  { path: '/hot', label: '热门' }
]

const categories = ref([])
const activeCategoryId = ref(null)
const searchKeyword = ref('')

const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const categoryOptions = computed(() =>
  categories.value.map((item) => ({
    label: item.name,
    value: item.id
  }))
)

const onCategorySelect = (categoryId) => {
  router.push({ path: '/', query: { category: categoryId } })
}

const onSubmitSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    return
  }
  router.push({ path: '/search', query: { keyword } })
}

const avatarInitial = computed(() => {
  const name = auth.username || ''
  return name ? name.charAt(0).toUpperCase() : '我'
})

const userMenuOptions = [
  { key: 'profile', label: '个人中心' },
  { key: 'favorites', label: '我的收藏' },
  { key: 'history', label: '浏览历史' },
  { type: 'divider', key: 'd1' },
  { key: 'logout', label: '退出登录' }
]

const onUserMenu = async (key) => {
  if (key === 'profile') {
    router.push('/profile')
  } else if (key === 'favorites') {
    router.push('/favorites')
  } else if (key === 'history') {
    router.push('/history')
  } else if (key === 'logout') {
    try {
      await logoutSession()
    } catch {
      // ignore — server-side blacklist may already have expired
    }
    auth.clearAuth()
    message.success('已退出登录')
    if (route.meta.requiresAuth) {
      router.push('/login')
    }
  }
}

onMounted(async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
})

watch(
  () => route.query.keyword,
  (keyword) => {
    searchKeyword.value = typeof keyword === 'string' ? keyword : ''
  },
  { immediate: true }
)
</script>

<style scoped>
.top-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
  height: var(--top-bar-height);
}

.top-bar__inner {
  max-width: var(--content-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--sp-6);
  display: flex;
  align-items: center;
  gap: var(--sp-6);
}

.top-bar__logo {
  font-family: var(--font-serif);
  font-size: var(--fs-24);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.top-bar__logo:hover {
  color: var(--accent);
}

.top-bar__logo-text {
  display: inline-block;
  border-bottom: 3px solid var(--accent);
  padding-bottom: 2px;
}

.top-bar__nav {
  display: flex;
  align-items: center;
  gap: var(--sp-5);
  flex: 0 0 auto;
}

.top-bar__nav-link {
  position: relative;
  padding: var(--sp-2) 0;
  font-size: var(--fs-14);
  color: var(--text-primary);
  font-weight: 500;
  background: none;
  border: 0;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.top-bar__nav-link--button {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-1);
}

.top-bar__nav-link:hover {
  color: var(--accent);
}

.top-bar__nav-link--active {
  color: var(--accent);
}

.top-bar__nav-link--active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -22px;
  height: 2px;
  background: var(--accent);
}

.top-bar__caret {
  font-size: 10px;
  color: var(--text-muted);
}

.top-bar__search {
  flex: 1;
  max-width: 320px;
  margin-left: auto;
}

.top-bar__search-icon {
  color: var(--text-muted);
}

.top-bar__auth {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  flex-shrink: 0;
}

.top-bar__auth-link {
  font-size: var(--fs-14);
  color: var(--text-primary);
  font-weight: 500;
}

.top-bar__auth-link:hover {
  color: var(--accent);
}

.top-bar__sep {
  color: var(--text-muted);
}

.top-bar__user {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: none;
  border: 0;
  padding: var(--sp-1) var(--sp-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.top-bar__user:hover {
  background: var(--bg-elevated);
}

.top-bar__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--text-on-accent);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--fs-14);
  font-weight: 600;
}

.top-bar__username {
  font-size: var(--fs-14);
  color: var(--text-primary);
}

.top-bar__menu-trigger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 24px;
  height: 18px;
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.top-bar__menu-trigger span {
  display: block;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
}

@media (max-width: 899px) {
  .top-bar__nav,
  .top-bar__search {
    display: none;
  }

  .top-bar__menu-trigger {
    display: flex;
  }

  .top-bar__inner {
    padding: 0 var(--sp-4);
    gap: var(--sp-3);
  }

  .top-bar__auth {
    margin-left: auto;
  }
}
</style>
