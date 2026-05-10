<template>
  <div class="profile">
    <div class="profile__grid">
      <aside class="profile__sidebar">
        <div class="profile__avatar">
          <img :src="avatarUrl" :alt="username" />
        </div>
        <h2 class="profile__name">{{ username }}</h2>
        <p class="profile__handle">@{{ usernameSlug }}</p>
        <p v-if="bio" class="profile__bio">{{ bio }}</p>

        <ul class="profile__details">
          <li>
            <span class="profile__detail-label">性别</span>
            <span class="profile__detail-value">{{ genderLabel }}</span>
          </li>
          <li v-if="email">
            <span class="profile__detail-label">邮箱</span>
            <span class="profile__detail-value">{{ email }}</span>
          </li>
          <li v-if="registerLabel">
            <span class="profile__detail-label">注册时间</span>
            <span class="profile__detail-value">{{ registerLabel }}</span>
          </li>
        </ul>

        <div class="profile__actions">
          <router-link to="/profile/edit">
            <n-button block>编辑资料</n-button>
          </router-link>
          <router-link to="/profile/password">
            <n-button block>修改密码</n-button>
          </router-link>
          <n-button block @click="onLogout">退出登录</n-button>
        </div>
      </aside>

      <section class="profile__main">
        <div class="profile__stats">
          <article class="profile__stat-card">
            <span class="profile__stat-label">收藏</span>
            <strong class="profile__stat-value">{{ stats.favorites }}</strong>
            <router-link to="/favorites" class="profile__stat-link">查看 →</router-link>
          </article>
          <article class="profile__stat-card">
            <span class="profile__stat-label">浏览历史</span>
            <strong class="profile__stat-value">{{ stats.history }}</strong>
            <router-link to="/history" class="profile__stat-link">查看 →</router-link>
          </article>
          <article class="profile__stat-card">
            <span class="profile__stat-label">阅读时长</span>
            <strong class="profile__stat-value">—</strong>
            <span class="profile__stat-link profile__stat-link--muted">数据未开放</span>
          </article>
        </div>

        <div class="profile__recent">
          <header class="profile__section-header">
            <h3>最近浏览</h3>
            <router-link to="/history" class="profile__section-link">查看全部 →</router-link>
          </header>
          <div v-if="recentLoading" class="profile__recent-loading">
            <LoadingSkeleton variant="row" />
          </div>
          <div v-else-if="recent.length" class="profile__recent-list">
            <NewsListRow
              v-for="item in recent"
              :key="item.historyId"
              :news="item"
              :categories="categories"
            />
          </div>
          <EmptyState
            v-else
            icon="📭"
            title="暂无浏览记录"
            description="去首页阅读几篇新闻"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, useMessage } from 'naive-ui'

import NewsListRow from '../components/news/NewsListRow.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'
import { useAuthStore } from '../store/auth'
import { fetchCurrentUser, logoutSession } from '../services/auth'
import { fetchFavoriteList } from '../services/favorite'
import { fetchHistoryList } from '../services/history'
import { fetchCategories } from '../services/news'
import { toGenderLabel } from '../utils/profile'
import { getAvatarUrl } from '../utils/media'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const stats = ref({ favorites: 0, history: 0 })
const recent = ref([])
const recentLoading = ref(false)
const categories = ref([])

const username = computed(() => auth.userInfo?.nickname || auth.userInfo?.username || '未登录')
const usernameSlug = computed(() => auth.userInfo?.username || '')
const email = computed(() => auth.userInfo?.email || '')
const bio = computed(() => auth.userInfo?.bio || auth.userInfo?.signature || '')
const genderLabel = computed(() => toGenderLabel(auth.userInfo?.gender))
const avatarUrl = computed(() => getAvatarUrl(auth.userInfo?.avatar))

const registerLabel = computed(() => {
  const ts = auth.userInfo?.createdAt || auth.userInfo?.registerTime
  if (!ts) return ''
  const date = new Date(ts)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
})

const refreshUserInfo = async () => {
  try {
    const data = await fetchCurrentUser()
    auth.setUserInfo(data)
  } catch {
    // ignore
  }
}

const loadStats = async () => {
  try {
    const [fav, hist] = await Promise.all([
      fetchFavoriteList({ page: 1, pageSize: 1 }),
      fetchHistoryList({ page: 1, pageSize: 1 })
    ])
    stats.value.favorites = fav?.total ?? 0
    stats.value.history = hist?.total ?? 0
  } catch {
    // ignore
  }
}

const loadRecent = async () => {
  recentLoading.value = true
  try {
    const data = await fetchHistoryList({ page: 1, pageSize: 5 })
    recent.value = data?.list || []
  } catch {
    recent.value = []
  } finally {
    recentLoading.value = false
  }
}

const loadCategories = async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
}

const onLogout = async () => {
  try {
    await logoutSession()
  } catch {
    // ignore
  }
  auth.clearAuth()
  message.success('已退出登录')
  router.push('/login')
}

onMounted(async () => {
  await Promise.all([refreshUserInfo(), loadCategories(), loadStats(), loadRecent()])
})
</script>

<style scoped>
.profile__grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--sp-8);
  align-items: start;
}

.profile__sidebar {
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
  text-align: center;
  position: sticky;
  top: calc(var(--top-bar-height) + var(--sp-6));
}

.profile__avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto var(--sp-4);
  background: var(--bg-page);
}

.profile__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile__name {
  font-family: var(--font-serif);
  font-size: var(--fs-20);
  margin-bottom: var(--sp-1);
}

.profile__handle {
  color: var(--text-muted);
  font-size: var(--fs-12);
}

.profile__bio {
  margin-top: var(--sp-3);
  color: var(--text-secondary);
  font-size: var(--fs-14);
  line-height: var(--lh-normal);
}

.profile__details {
  margin: var(--sp-6) 0;
  padding: var(--sp-4) 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.profile__details li {
  display: flex;
  justify-content: space-between;
  font-size: var(--fs-14);
}

.profile__detail-label {
  color: var(--text-muted);
}

.profile__detail-value {
  color: var(--text-primary);
}

.profile__actions {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.profile__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-8);
}

.profile__stat-card {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.profile__stat-label {
  color: var(--text-muted);
  font-size: var(--fs-12);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.profile__stat-value {
  font-family: var(--font-serif);
  font-size: var(--fs-30);
  font-weight: 800;
}

.profile__stat-link {
  color: var(--accent);
  font-size: var(--fs-12);
}

.profile__stat-link--muted {
  color: var(--text-muted);
}

.profile__section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--sp-4);
  padding-bottom: var(--sp-3);
  border-bottom: 2px solid var(--text-primary);
}

.profile__section-header h3 {
  font-family: var(--font-serif);
  font-size: var(--fs-20);
}

.profile__section-link {
  font-size: var(--fs-12);
  color: var(--text-muted);
}

.profile__section-link:hover {
  color: var(--accent);
}

@media (max-width: 899px) {
  .profile__grid {
    grid-template-columns: 1fr;
  }
  .profile__sidebar {
    position: static;
  }
  .profile__stats {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
