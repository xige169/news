<template>
  <div class="page page-home">
    <section class="hero-card hero-card--editorial">
      <p class="eyebrow">Daily Briefing</p>
      <h1 class="hero-title">头条新闻前台</h1>
      <p class="hero-subtitle">
        以栏目切换、编辑推荐和即时阅读为核心，串起新闻、收藏、历史和个人资料。
      </p>
      <form class="hero-search" @submit.prevent="openSearchPage">
        <input
          v-model.trim="searchKeyword"
          class="search-input search-input--hero"
          type="search"
          placeholder="搜索今日议题、公司、人物"
        />
        <button class="hero-button hero-button--primary click-effect" type="submit">
          搜索新闻
        </button>
      </form>
      <div class="hero-actions">
        <button class="hero-button hero-button--primary click-effect" type="button" @click="openPrimaryAction">
          {{ authStore.isLoggedIn ? '查看我的资料' : '立即登录' }}
        </button>
        <button class="hero-button hero-button--ghost click-effect" type="button" @click="refreshCurrentCategory">
          刷新当前栏目
        </button>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>新闻栏目</h2>
        <span class="section-hint">{{ categories.length }} 个分类</span>
      </div>
      <div class="category-grid">
        <button
          v-for="item in categories"
          :key="item.id"
          class="category-chip click-effect"
          :class="{ active: item.id === activeCategory }"
          type="button"
          @click="activeCategory = item.id"
        >
          {{ item.name }}
        </button>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>为你推荐</h2>
        <span class="section-hint">{{ recommendSourceLabel }}</span>
      </div>
      <article class="feature-card click-effect" role="button" tabindex="0" @click="goToDetail(featuredNews.id)">
        <van-image
          class="feature-image"
          fit="cover"
          radius="18"
          :src="featuredNews.image"
        />
        <div class="feature-copy">
          <h3>{{ featuredNews.title }}</h3>
          <p>{{ featuredNews.summary }}</p>
        </div>
        <span class="feature-tag">{{ featuredNews.tag }}</span>
      </article>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>热门追踪</h2>
        <span class="section-hint">全站热度排行</span>
      </div>
      <div v-if="hotNews.length" class="news-list">
        <article
          v-for="item in hotNews"
          :key="item.id"
          class="news-card click-effect"
          @click="goToDetail(item.id)"
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
          </div>
        </article>
      </div>
      <p v-else class="preference-copy">暂无热门新闻</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>最新快讯</h2>
        <span class="section-hint">点击查看详情</span>
      </div>
      <p v-if="isLoading" class="preference-copy">新闻加载中...</p>
      <p v-else-if="newsList.length === 0" class="preference-copy">当前暂无新闻数据</p>
      <div v-else class="news-list">
        <article
          v-for="item in newsList"
          :key="item.id"
          class="news-card click-effect"
          @click="goToDetail(item.id)"
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
          :disabled="isLoadingMore"
          @click="loadMoreNews"
        >
          {{ isLoadingMore ? '加载中...' : '加载更多' }}
        </button>
        <p v-else class="preference-copy">该分类新闻已全部加载</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { fetchCategories, fetchHotNews, fetchNewsList, fetchRecommendedNews } from '../services/news.js'
import { useAuthStore } from '../store/auth'
import { getNewsImageUrl } from '../utils/media.js'
import { mergeNewsPage, resetPaginationState } from '../utils/news-pagination.js'

const router = useRouter()
const authStore = useAuthStore()

const categories = ref([])
const activeCategory = ref(null)
const newsList = ref([])
const hotNews = ref([])
const recommendedNews = ref([])
const recommendSource = ref('hot')
const searchKeyword = ref('')
const isLoading = ref(false)
const isLoadingMore = ref(false)
const currentPage = ref(1)
const hasMore = ref(true)

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

const loadNewsList = async (categoryId, page = 1) => {
  if (!categoryId) {
    newsList.value = []
    return
  }

  if (page === 1) {
    isLoading.value = true
  } else {
    isLoadingMore.value = true
  }

  try {
    const payload = await fetchNewsList({ categoryId, page, pageSize: 10 })
    const nextState = mergeNewsPage(
      {
        items: newsList.value,
        page: currentPage.value,
        hasMore: hasMore.value
      },
      payload.list.map(formatNewsItem),
      payload.hasMore,
      page
    )

    newsList.value = nextState.items
    currentPage.value = nextState.page
    hasMore.value = nextState.hasMore
  } catch (error) {
    if (page === 1) {
      newsList.value = []
    }
    showToast(error instanceof Error ? error.message : '新闻加载失败')
  } finally {
    if (page === 1) {
      isLoading.value = false
    } else {
      isLoadingMore.value = false
    }
  }
}

const loadHomePage = async () => {
  try {
    const [categoryList, hotPayload, recommendPayload] = await Promise.all([
      fetchCategories(),
      fetchHotNews({ page: 1, pageSize: 3 }),
      fetchRecommendedNews({ page: 1, pageSize: 3 })
    ])
    categories.value = categoryList
    hotNews.value = hotPayload.list.map(formatNewsItem)
    recommendedNews.value = recommendPayload.list.map(formatNewsItem)
    recommendSource.value = recommendPayload.source || 'hot'

    if (!activeCategory.value) {
      activeCategory.value = categoryList[0]?.id ?? null
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : '分类加载失败')
  }
}

const featuredNews = computed(() => {
  if (recommendedNews.value.length === 0) {
    return {
      id: null,
      title: '暂无推荐内容',
      summary: isLoading.value ? '正在加载新闻内容。' : '当前暂无可展示的推荐内容。',
      image: getNewsImageUrl(''),
      tag: '提示'
    }
  }

  return {
    id: recommendedNews.value[0].id,
    title: recommendedNews.value[0].title,
    summary: recommendedNews.value[0].summary,
    image: recommendedNews.value[0].image,
    tag: recommendSource.value === 'personalized' ? '为你推荐' : '热门推荐'
  }
})

const recommendSourceLabel = computed(() => (
  recommendSource.value === 'personalized' ? '结合你的阅读轨迹' : '基于全站热度'
))

const goToDetail = (id) => {
  if (!id) {
    return
  }

  router.push(`/news/${id}`)
}

const openPrimaryAction = () => {
  router.push(authStore.isLoggedIn ? '/profile' : '/login')
}

const openSearchPage = () => {
  router.push({
    path: '/search',
    query: searchKeyword.value ? { q: searchKeyword.value } : {}
  })
}

const refreshCurrentCategory = async () => {
  const resetState = resetPaginationState()
  newsList.value = resetState.items
  currentPage.value = resetState.page
  hasMore.value = resetState.hasMore
  await loadNewsList(activeCategory.value, 1)
}

const loadMoreNews = async () => {
  if (!activeCategory.value || !hasMore.value || isLoadingMore.value) {
    return
  }

  await loadNewsList(activeCategory.value, currentPage.value + 1)
}

watch(activeCategory, async (categoryId) => {
  const resetState = resetPaginationState()
  newsList.value = resetState.items
  currentPage.value = resetState.page
  hasMore.value = resetState.hasMore
  await loadNewsList(categoryId, 1)
})

onMounted(async () => {
  await loadHomePage()
})
</script>
