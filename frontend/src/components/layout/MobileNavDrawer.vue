<template>
  <n-drawer :show="show" :width="280" placement="left" @update:show="onToggle">
    <n-drawer-content title="导航" closable>
      <div class="mobile-nav__search">
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索新闻"
          @keydown.enter="onSubmitSearch"
        />
      </div>

      <div class="mobile-nav__group">
        <router-link to="/" class="mobile-nav__link" @click="close">首页</router-link>
        <router-link to="/search" class="mobile-nav__link" @click="close">搜索</router-link>
      </div>

      <div v-if="categories.length" class="mobile-nav__group">
        <h4 class="mobile-nav__title">分类</h4>
        <button
          v-for="item in categories"
          :key="item.id"
          class="mobile-nav__link mobile-nav__link--button"
          type="button"
          @click="onCategoryClick(item.id)"
        >
          {{ item.name }}
        </button>
      </div>

      <div class="mobile-nav__group">
        <h4 class="mobile-nav__title">账户</h4>
        <template v-if="auth.isLoggedIn">
          <router-link to="/profile" class="mobile-nav__link" @click="close">个人中心</router-link>
          <router-link to="/favorites" class="mobile-nav__link" @click="close">我的收藏</router-link>
          <router-link to="/history" class="mobile-nav__link" @click="close">浏览历史</router-link>
          <button class="mobile-nav__link mobile-nav__link--button" type="button" @click="onLogout">
            退出登录
          </button>
        </template>
        <template v-else>
          <router-link to="/login" class="mobile-nav__link" @click="close">登录</router-link>
          <router-link to="/register" class="mobile-nav__link" @click="close">注册</router-link>
        </template>
      </div>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDrawer, NDrawerContent, NInput, useMessage } from 'naive-ui'

import { useAuthStore } from '../../store/auth'
import { fetchCategories } from '../../services/news'
import { logoutSession } from '../../services/auth'

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['update:show'])

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const message = useMessage()

const categories = ref([])
const searchKeyword = ref('')

const onToggle = (value) => {
  emit('update:show', value)
}

const close = () => {
  emit('update:show', false)
}

const onSubmitSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return
  router.push({ path: '/search', query: { keyword } })
  close()
}

const onCategoryClick = (categoryId) => {
  router.push({ path: '/', query: { category: categoryId } })
  close()
}

const onLogout = async () => {
  try {
    await logoutSession()
  } catch {
    // ignore
  }
  auth.clearAuth()
  message.success('已退出登录')
  close()
  if (route.meta.requiresAuth) {
    router.push('/login')
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
</script>

<style scoped>
.mobile-nav__search {
  margin-bottom: var(--sp-5);
}

.mobile-nav__group {
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
  padding: var(--sp-4) 0;
  border-bottom: 1px solid var(--border);
}

.mobile-nav__group:last-child {
  border-bottom: 0;
}

.mobile-nav__title {
  font-family: var(--font-sans);
  font-size: var(--fs-12);
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--sp-2);
}

.mobile-nav__link {
  display: block;
  padding: var(--sp-3);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--fs-16);
  text-align: left;
  background: none;
  border: 0;
  width: 100%;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.mobile-nav__link:hover {
  background: var(--bg-elevated);
  color: var(--accent);
}

.mobile-nav__link--button {
  font-family: inherit;
}
</style>
