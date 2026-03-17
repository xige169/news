<template>
  <div class="page">
    <section class="hero-card compact">
      <p class="eyebrow">Favorites</p>
      <h1 class="hero-title">我的收藏</h1>
      <p class="hero-subtitle">管理已收藏的新闻，随时回看重点内容。</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>收藏列表</h2>
        <button class="text-button" type="button" @click="handleClear">清空收藏</button>
      </div>
      <div v-if="items.length" class="news-list">
        <article
          v-for="item in items"
          :key="item.favoriteId"
          class="news-card click-effect"
          @click="router.push(`/news/${item.id}`)"
        >
          <div class="news-copy">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description || '暂无摘要' }}</p>
            <div class="news-meta">
              <span>{{ item.author || '未知来源' }}</span>
              <span>{{ formatDate(item.favoriteTime) }}</span>
            </div>
          </div>
        </article>
      </div>
      <van-empty v-else description="还没有收藏内容" />
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { clearFavorites, fetchFavoriteList } from '../services/favorite.js'

const router = useRouter()
const items = ref([])

const formatDate = (value) => {
  if (!value) {
    return '未知时间'
  }

  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const loadFavorites = async () => {
  try {
    const payload = await fetchFavoriteList({ page: 1, pageSize: 20 })
    items.value = payload.list || []
  } catch (error) {
    items.value = []
    showToast(error instanceof Error ? error.message : '收藏加载失败')
  }
}

const handleClear = async () => {
  try {
    await clearFavorites()
    items.value = []
    showToast('已清空收藏')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '清空收藏失败')
  }
}

onMounted(async () => {
  await loadFavorites()
})
</script>
