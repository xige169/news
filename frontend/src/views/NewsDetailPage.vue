<template>
  <div class="page detail-page">
    <section class="hero-card compact">
      <p class="eyebrow">Article</p>
      <h1 class="hero-title">{{ detail.title || '新闻详情' }}</h1>
      <div class="detail-image-frame">
        <van-image
          class="detail-hero-image"
          fit="contain"
          radius="18"
          :src="detailImage"
        />
      </div>
      <div class="detail-meta">
        <span>{{ detail.author || '未知作者' }}</span>
        <span>{{ formatDate(detail.publishTime) }}</span>
        <span>{{ detail.views || 0 }} 次阅读</span>
      </div>
      <div class="hero-actions">
        <button
          class="favorite-toggle click-effect"
          :class="{ active: favoriteAction.pressed }"
          type="button"
          @click="toggleFavorite"
          :disabled="favoriteLoading"
          :aria-pressed="favoriteAction.pressed"
        >
          <span class="favorite-toggle__icon">
            <van-icon :name="favoriteAction.icon" />
          </span>
          <span class="favorite-toggle__label">{{ favoriteAction.label }}</span>
        </button>
        <button class="hero-button hero-button--ghost click-effect" type="button" @click="router.push('/')">
          返回首页
        </button>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>正文</h2>
      </div>
      <p class="detail-content">{{ detail.content || '暂无正文内容' }}</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>相关推荐</h2>
      </div>
      <div v-if="relatedNews.length" class="news-list">
        <article
          v-for="item in relatedNews"
          :key="item.id"
          class="news-card click-effect"
          @click="router.push(`/news/${item.id}`)"
        >
          <van-image
            class="news-cover"
            fit="cover"
            radius="14"
            :src="getNewsImageUrl(item.image)"
          />
          <div class="news-copy">
            <h3>{{ item.title }}</h3>
            <p>{{ item.content || '暂无摘要' }}</p>
          </div>
        </article>
      </div>
      <p v-else class="preference-copy">暂无相关推荐</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

import { addFavorite, checkFavorite, removeFavorite } from '../services/favorite.js'
import { addHistoryEntry } from '../services/history.js'
import { fetchNewsDetail } from '../services/news.js'
import { useAuthStore } from '../store/auth'
import { getFavoriteActionMeta } from '../utils/favorite.js'
import { getNewsImageUrl } from '../utils/media.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const detail = ref({})
const isFavorite = ref(false)
const favoriteLoading = ref(false)

const relatedNews = computed(() => detail.value.relatedNews || [])
const detailImage = computed(() => getNewsImageUrl(detail.value.image))
const favoriteAction = computed(() => getFavoriteActionMeta(isFavorite.value, favoriteLoading.value))

const formatDate = (value) => {
  if (!value) {
    return '未知时间'
  }

  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const syncFavoriteState = async (id) => {
  if (!authStore.isLoggedIn) {
    isFavorite.value = false
    return
  }

  try {
    const payload = await checkFavorite(id)
    isFavorite.value = Boolean(payload.isFavorite)
  } catch (error) {
    showToast(error instanceof Error ? error.message : '收藏状态获取失败')
  }
}

const writeHistory = async (id) => {
  if (!authStore.isLoggedIn) {
    return
  }

  try {
    await addHistoryEntry(id)
  } catch (error) {
    showToast(error instanceof Error ? error.message : '历史记录写入失败')
  }
}

const loadDetail = async (id) => {
  try {
    detail.value = await fetchNewsDetail(id)
    await Promise.all([syncFavoriteState(id), writeHistory(id)])
  } catch (error) {
    showToast(error instanceof Error ? error.message : '详情加载失败')
  }
}

const toggleFavorite = async () => {
  if (!authStore.isLoggedIn) {
    router.push({
      path: '/login',
      query: {
        redirect: route.fullPath
      }
    })
    return
  }

  favoriteLoading.value = true

  try {
    if (isFavorite.value) {
      await removeFavorite(detail.value.id)
      isFavorite.value = false
      showToast('已取消收藏')
    } else {
      await addFavorite(detail.value.id)
      isFavorite.value = true
      showToast('收藏成功')
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : '收藏操作失败')
  } finally {
    favoriteLoading.value = false
  }
}

watch(
  () => route.params.id,
  async (value) => {
    if (!value) {
      return
    }

    await loadDetail(Number(value))
  },
  { immediate: true }
)
</script>
