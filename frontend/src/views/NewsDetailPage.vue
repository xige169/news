<template>
  <article class="detail">
    <div class="detail__back">
      <router-link to="/" class="detail__back-link">← 返回</router-link>
    </div>

    <div v-if="loading" class="detail__loading">
      <LoadingSkeleton variant="card" />
    </div>

    <template v-else-if="news">
      <header class="detail__header">
        <div class="detail__eyebrow">
          <span v-if="categoryName" class="detail__category">{{ categoryName }}</span>
          <span v-if="publishLabel" class="detail__time">{{ publishLabel }}</span>
        </div>

        <h1 class="detail__title">{{ news.title }}</h1>

        <p v-if="news.summary || news.description" class="detail__summary">
          {{ news.summary || news.description }}
        </p>

        <div class="detail__meta">
          <div class="detail__meta-info">
            <span v-if="news.author">{{ news.author }}</span>
            <span v-if="typeof news.views === 'number'">{{ news.views }} 阅读</span>
          </div>
          <div class="detail__actions">
            <button
              type="button"
              class="detail__favorite"
              :class="{ 'detail__favorite--active': favorited }"
              @click="onToggleFavorite"
            >
              <span class="detail__favorite-icon">{{ favorited ? '♥' : '♡' }}</span>
              {{ favorited ? '已收藏' : '收藏' }}
            </button>
            <button type="button" class="detail__share" @click="onShare">↗ 分享</button>
          </div>
        </div>
      </header>

      <figure v-if="news.image" class="detail__cover">
        <img :src="news.image" :alt="news.title" />
      </figure>

      <div class="detail__body prose" v-html="renderedContent" />

      <CommentSection v-if="news?.id" :news-id="news.id" />

      <section v-if="related.length" class="detail__related">
        <header class="detail__related-header">
          <h2 class="detail__related-title">相关推荐</h2>
        </header>
        <div class="detail__related-grid">
          <NewsCard
            v-for="item in related"
            :key="item.id"
            :news="item"
            :categories="categories"
          />
        </div>
      </section>
    </template>

    <EmptyState
      v-else
      icon="📭"
      title="新闻不存在"
      description="这篇内容已被移除或链接错误"
    >
      <router-link to="/">
        <n-button>返回首页</n-button>
      </router-link>
    </EmptyState>

    <button
      v-show="showBackToTop"
      type="button"
      class="detail__top"
      aria-label="回到顶部"
      @click="scrollToTop"
    >
      ↑
    </button>

    <n-modal v-model:show="showLoginModal" preset="card" title="登录后再操作" style="width: 360px">
      <p class="detail__modal-text">收藏新闻需要先登录，是否前往登录？</p>
      <template #footer>
        <div class="detail__modal-actions">
          <n-button @click="showLoginModal = false">取消</n-button>
          <n-button type="primary" @click="goLogin">前往登录</n-button>
        </div>
      </template>
    </n-modal>
  </article>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { NButton, NModal, useMessage } from 'naive-ui'

import NewsCard from '../components/news/NewsCard.vue'
import CommentSection from '../components/news/CommentSection.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'
import {
  fetchCategories,
  fetchNewsDetail,
  fetchNewsList,
  fetchRecommendedNews
} from '../services/news'
import {
  addFavorite,
  checkFavorite,
  removeFavorite
} from '../services/favorite'
import { addHistoryEntry } from '../services/history'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const message = useMessage()

const news = ref(null)
const loading = ref(false)
const favorited = ref(false)
const categories = ref([])
const related = ref([])
const showLoginModal = ref(false)
const showBackToTop = ref(false)

const categoryName = computed(() => {
  if (!news.value?.categoryId) return ''
  const match = categories.value.find((c) => c.id === news.value.categoryId)
  return match ? match.name : ''
})

const publishLabel = computed(() => {
  const value = news.value?.publishTime
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
})

const renderedContent = computed(() => {
  const raw = news.value?.content || news.value?.description || ''
  if (!raw) return ''
  const html = marked.parse(raw, { breaks: true, gfm: true })
  return DOMPurify.sanitize(html)
})

const loadCategories = async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
}

const loadDetail = async (id) => {
  loading.value = true
  news.value = null
  try {
    const data = await fetchNewsDetail(id)
    news.value = data
  } catch (err) {
    message.error(err?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadFavoriteStatus = async (id) => {
  if (!auth.isLoggedIn) {
    favorited.value = false
    return
  }
  try {
    const data = await checkFavorite(id)
    favorited.value = Boolean(data?.favorite ?? data?.favorited ?? data === true)
  } catch {
    favorited.value = false
  }
}

const loadRelated = async () => {
  if (!news.value) return
  try {
    if (news.value.categoryId) {
      const data = await fetchNewsList({
        categoryId: news.value.categoryId,
        page: 1,
        pageSize: 5
      })
      related.value = (data?.list || []).filter((it) => it.id !== news.value.id).slice(0, 4)
    }
    if (!related.value.length) {
      const data = await fetchRecommendedNews({ page: 1, pageSize: 5 })
      related.value = (data?.list || []).filter((it) => it.id !== news.value.id).slice(0, 4)
    }
  } catch {
    related.value = []
  }
}

const recordHistory = async (id) => {
  if (!auth.isLoggedIn) return
  try {
    await addHistoryEntry(id)
  } catch {
    // ignore
  }
}

const onToggleFavorite = async () => {
  if (!auth.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  if (!news.value) return
  try {
    if (favorited.value) {
      await removeFavorite(news.value.id)
      favorited.value = false
      message.success('已取消收藏')
    } else {
      await addFavorite(news.value.id)
      favorited.value = true
      message.success('已加入收藏')
    }
  } catch (err) {
    message.error(err?.message || '操作失败')
  }
}

const onShare = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    message.success('链接已复制')
  } catch {
    message.warning('请手动复制地址栏链接')
  }
}

const goLogin = () => {
  showLoginModal.value = false
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const onScroll = () => {
  showBackToTop.value = window.scrollY > 600
}

const initAll = async (id) => {
  await loadDetail(id)
  if (news.value) {
    await Promise.all([loadFavoriteStatus(id), loadRelated(), recordHistory(id)])
  }
}

watch(
  () => route.params.id,
  (raw) => {
    const id = Number(raw)
    if (Number.isFinite(id)) {
      initAll(id)
      window.scrollTo({ top: 0 })
    }
  }
)

onMounted(async () => {
  window.addEventListener('scroll', onScroll, { passive: true })
  await loadCategories()
  const id = Number(route.params.id)
  if (Number.isFinite(id)) {
    await initAll(id)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.detail {
  max-width: 960px;
  margin: 0 auto;
  position: relative;
}

.detail__back {
  margin-bottom: var(--sp-6);
}

.detail__back-link {
  font-size: var(--fs-14);
  color: var(--text-secondary);
}

.detail__back-link:hover {
  color: var(--accent);
}

.detail__loading {
  max-width: 760px;
  margin: 0 auto;
}

.detail__header {
  max-width: 760px;
  margin: 0 auto var(--sp-8);
  text-align: center;
}

.detail__eyebrow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-3);
  margin-bottom: var(--sp-4);
  font-size: var(--fs-12);
  letter-spacing: 0.06em;
}

.detail__category {
  color: var(--accent);
  font-weight: 700;
  text-transform: uppercase;
}

.detail__time {
  color: var(--text-muted);
}

.detail__title {
  font-family: var(--font-serif);
  font-size: var(--fs-48);
  font-weight: 800;
  line-height: var(--lh-tight);
  margin-bottom: var(--sp-5);
}

.detail__summary {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: var(--fs-20);
  color: var(--text-secondary);
  line-height: var(--lh-normal);
  margin-bottom: var(--sp-6);
}

.detail__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--sp-5);
  border-top: 1px solid var(--border);
}

.detail__meta-info {
  display: flex;
  gap: var(--sp-4);
  font-size: var(--fs-14);
  color: var(--text-muted);
}

.detail__actions {
  display: flex;
  gap: var(--sp-2);
}

.detail__favorite,
.detail__share {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-4);
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg-page);
  font-size: var(--fs-14);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.detail__favorite:hover,
.detail__share:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.detail__favorite--active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-on-accent);
}

.detail__favorite--active:hover {
  background: var(--accent-hover);
  color: var(--text-on-accent);
}

.detail__favorite-icon {
  font-size: var(--fs-16);
}

.detail__cover {
  max-width: 760px;
  margin: 0 auto var(--sp-8);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.detail__cover img {
  width: 100%;
  display: block;
}

.detail__body {
  max-width: 720px;
  margin: 0 auto;
}

.detail__related {
  max-width: 1200px;
  margin: var(--sp-16) auto 0;
  padding-top: var(--sp-8);
  border-top: 1px solid var(--border);
}

.detail__related-header {
  margin-bottom: var(--sp-6);
  padding-bottom: var(--sp-3);
  border-bottom: 2px solid var(--text-primary);
}

.detail__related-title {
  font-family: var(--font-serif);
  font-size: var(--fs-24);
  font-weight: 800;
}

.detail__related-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-6);
}

.detail__top {
  position: fixed;
  bottom: var(--sp-8);
  right: var(--sp-8);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--text-on-accent);
  border: 0;
  font-size: var(--fs-20);
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  z-index: 50;
  transition: background var(--transition-fast);
}

.detail__top:hover {
  background: var(--accent-hover);
}

.detail__modal-text {
  font-size: var(--fs-14);
  color: var(--text-secondary);
  line-height: var(--lh-normal);
}

.detail__modal-actions {
  display: flex;
  gap: var(--sp-2);
  justify-content: flex-end;
}

@media (max-width: 899px) {
  .detail__title {
    font-size: var(--fs-30);
  }
  .detail__related-grid {
    grid-template-columns: 1fr 1fr;
  }
  .detail__meta {
    flex-direction: column;
    gap: var(--sp-3);
    align-items: flex-start;
  }
}
</style>
