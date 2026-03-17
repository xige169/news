<template>
  <div class="page">
    <section class="hero-card compact">
      <p class="eyebrow">History</p>
      <h1 class="hero-title">浏览历史</h1>
      <p class="hero-subtitle">自动记录你看过的新闻，便于回溯和继续阅读。</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>最近浏览</h2>
        <button class="text-button" type="button" @click="handleClear">清空历史</button>
      </div>
      <div v-if="items.length" class="news-list">
        <article v-for="item in items" :key="item.historyId" class="news-card">
          <div class="news-copy" @click="router.push(`/news/${item.id}`)">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description || '暂无摘要' }}</p>
            <div class="news-meta">
              <span>{{ item.author || '未知来源' }}</span>
              <span>{{ formatDate(item.viewTime) }}</span>
            </div>
          </div>
          <button class="text-button" type="button" @click="handleDelete(item.historyId)">删除</button>
        </article>
      </div>
      <van-empty v-else description="还没有浏览记录" />
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { clearHistoryEntries, fetchHistoryList, removeHistoryEntry } from '../services/history.js'

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

const loadHistory = async () => {
  try {
    const payload = await fetchHistoryList({ page: 1, pageSize: 20 })
    items.value = payload.list || []
  } catch (error) {
    items.value = []
    showToast(error instanceof Error ? error.message : '历史记录加载失败')
  }
}

const handleDelete = async (historyId) => {
  try {
    await removeHistoryEntry(historyId)
    items.value = items.value.filter((item) => item.historyId !== historyId)
    showToast('删除成功')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '删除失败')
  }
}

const handleClear = async () => {
  try {
    await clearHistoryEntries()
    items.value = []
    showToast('已清空历史')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '清空历史失败')
  }
}

onMounted(async () => {
  await loadHistory()
})
</script>
