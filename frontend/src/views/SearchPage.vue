<template>
  <div class="page page-search">
    <section class="hero-card hero-card--editorial">
      <p class="eyebrow">Search Desk</p>
      <h1 class="hero-title">搜索新闻主题与关键词</h1>
      <p class="hero-subtitle">用关键词、分类和分页结果快速定位你关心的新闻线索。</p>
    </section>

    <section class="section-card">
      <form class="search-panel" @submit.prevent="handleSearch">
        <input
          v-model.trim="keyword"
          class="search-input"
          type="search"
          placeholder="输入关键词，例如 AI、芯片、国际局势"
        />
        <button class="hero-button hero-button--primary click-effect" type="submit" :disabled="submitting">
          {{ submitting ? '搜索中...' : '开始搜索' }}
        </button>
      </form>
      <div v-if="categories.length" class="category-grid">
        <button
          class="category-chip click-effect"
          :class="{ active: activeCategory === null }"
          type="button"
          @click="activeCategory = null"
        >
          全部
        </button>
        <button
          v-for="item in categories"
          :key="item.id"
          class="category-chip click-effect"
          :class="{ active: activeCategory === item.id }"
          type="button"
          @click="activeCategory = item.id"
        >
          {{ item.name }}
        </button>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>搜索结果</h2>
        <span class="section-hint">{{ resultTotal }} 条结果</span>
      </div>
      <p v-if="submitting" class="preference-copy">正在搜索新闻...</p>
      <p v-else-if="!hasSearched" class="preference-copy">输入关键词后开始搜索。</p>
      <p v-else-if="results.length === 0" class="preference-copy">没有找到匹配结果，试试更宽泛的关键词。</p>
      <div v-else class="news-list">
        <article
          v-for="item in results"
          :key="item.id"
          class="news-card click-effect"
          @click="router.push(`/news/${item.id}`)"
        >
          <van-image
            class="news-cover"
            fit="cover"
            radius="14"
            :src="item.image"
          />
          <div class="news-copy">
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
            <div class="topic-tags" v-if="item.tags.length">
              <span v-for="tag in item.tags" :key="tag" class="topic-tag">{{ tag }}</span>
            </div>
            <div class="news-meta">
              <span>{{ item.source }}</span>
              <span>{{ item.time }}</span>
            </div>
          </div>
        </article>
        <button
          v-if="hasMore"
          class="load-more-button click-effect"
          type="button"
          :disabled="loadingMore"
          @click="loadMore"
        >
          {{ loadingMore ? '加载中...' : '加载更多结果' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

import { fetchCategories, searchNews } from '../services/news.js'
import { getNewsImageUrl } from '../utils/media.js'
import { mergeNewsPage, resetPaginationState } from '../utils/news-pagination.js'

const route = useRoute()
const router = useRouter()

const categories = ref([])
const keyword = ref(String(route.query.q || ''))
const activeCategory = ref(route.query.categoryId ? Number(route.query.categoryId) : null)
const results = ref([])
const resultTotal = ref(0)
const currentPage = ref(1)
const hasMore = ref(false)
const hasSearched = ref(Boolean(keyword.value))
const submitting = ref(false)
const loadingMore = ref(false)

const formatDate = (value) => {
  if (!value) {
    return '刚刚'
  }

  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const formatNewsItem = (item) => ({
  id: item.id,
  title: item.title,
  summary: item.summary || item.description || '暂无摘要',
  image: getNewsImageUrl(item.image),
  source: item.author || '未知来源',
  time: formatDate(item.publishTime),
  tags: item.tags || []
})

const runSearch = async (page = 1) => {
  if (!keyword.value) {
    results.value = []
    resultTotal.value = 0
    hasMore.value = false
    hasSearched.value = false
    return
  }

  hasSearched.value = true
  if (page === 1) {
    submitting.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const payload = await searchNews({
      keyword: keyword.value,
      categoryId: activeCategory.value,
      page,
      pageSize: 10
    })
    const nextState = mergeNewsPage(
      {
        items: results.value,
        page: currentPage.value,
        hasMore: hasMore.value
      },
      payload.list.map(formatNewsItem),
      payload.hasMore,
      page
    )

    results.value = nextState.items
    currentPage.value = nextState.page
    hasMore.value = nextState.hasMore
    resultTotal.value = payload.total
  } catch (error) {
    showToast(error instanceof Error ? error.message : '搜索失败')
  } finally {
    if (page === 1) {
      submitting.value = false
    } else {
      loadingMore.value = false
    }
  }
}

const syncRouteQuery = () => {
  router.replace({
    path: '/search',
    query: {
      ...(keyword.value ? { q: keyword.value } : {}),
      ...(activeCategory.value ? { categoryId: String(activeCategory.value) } : {})
    }
  })
}

const handleSearch = async () => {
  const resetState = resetPaginationState()
  results.value = resetState.items
  currentPage.value = resetState.page
  hasMore.value = resetState.hasMore
  syncRouteQuery()
  await runSearch(1)
}

const loadMore = async () => {
  if (!hasMore.value || loadingMore.value) {
    return
  }
  await runSearch(currentPage.value + 1)
}

watch(activeCategory, async () => {
  if (!hasSearched.value) {
    return
  }
  await handleSearch()
})

onMounted(async () => {
  try {
    categories.value = await fetchCategories()
  } catch (error) {
    showToast(error instanceof Error ? error.message : '分类加载失败')
  }

  if (keyword.value) {
    await runSearch(1)
  }
})
</script>
