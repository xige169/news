<template>
  <div class="home">
    <section v-if="hero" class="home__hero">
      <NewsCard :news="hero" :categories="categories" feature />
    </section>
    <section v-else-if="loading" class="home__hero">
      <LoadingSkeleton variant="card" />
    </section>

    <div class="home__body">
      <div class="home__main">
        <header class="home__section-header">
          <h2 class="home__section-title">推荐</h2>
          <button v-if="categoryId" type="button" class="home__filter-clear" @click="clearCategory">
            清除筛选 ✕
          </button>
        </header>

        <div v-if="loading && !feed.length" class="home__feed-grid">
          <LoadingSkeleton v-for="n in 4" :key="n" variant="card" />
        </div>

        <div v-else-if="feedRest.length" class="home__feed-grid">
          <NewsCard
            v-for="item in feedRest"
            :key="item.id"
            :news="item"
            :categories="categories"
          />
        </div>

        <EmptyState
          v-else-if="!feed.length"
          icon="📰"
          title="暂无新闻"
          description="当前栏目下没有可显示的新闻"
        />

        <div v-if="hasMore" class="home__more">
          <n-button :loading="loadingMore" size="large" @click="loadMore">加载更多</n-button>
        </div>
      </div>

      <div class="home__aside">
        <HotList :items="hotItems" :loading="hotLoading" />
        <CategoryNav
          v-model="categoryId"
          :items="categories"
          @change="onCategoryChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, useMessage } from 'naive-ui'

import NewsCard from '../components/news/NewsCard.vue'
import HotList from '../components/news/HotList.vue'
import CategoryNav from '../components/news/CategoryNav.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'

import {
  fetchCategories,
  fetchHotNews,
  fetchNewsList,
  fetchRecommendedNews
} from '../services/news'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const categories = ref([])
const hotItems = ref([])
const hotLoading = ref(false)

const feed = ref([])
const page = ref(1)
const pageSize = 12
const total = ref(0)
const hasMore = computed(() => feed.value.length < total.value)

const loading = ref(false)
const loadingMore = ref(false)

const categoryId = ref(route.query.category ? Number(route.query.category) : null)

const hero = computed(() => feed.value[0] || null)
const feedRest = computed(() => feed.value.slice(1))

const loadCategories = async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
}

const loadHot = async () => {
  hotLoading.value = true
  try {
    const data = await fetchHotNews({ page: 1, pageSize: 10 })
    hotItems.value = data?.list || []
  } catch {
    hotItems.value = []
  } finally {
    hotLoading.value = false
  }
}

const loadFeed = async ({ append = false } = {}) => {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    feed.value = []
    page.value = 1
  }

  try {
    const data = categoryId.value
      ? await fetchNewsList({ categoryId: categoryId.value, page: page.value, pageSize })
      : await fetchRecommendedNews({ page: page.value, pageSize })

    const list = data?.list || []
    feed.value = append ? [...feed.value, ...list] : list
    total.value = data?.total ?? feed.value.length
  } catch (err) {
    message.error(err?.message || '加载失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = async () => {
  page.value += 1
  await loadFeed({ append: true })
}

const onCategoryChange = (id) => {
  categoryId.value = id
  router.replace({ path: '/', query: id ? { category: id } : {} })
  loadFeed()
}

const clearCategory = () => onCategoryChange(null)

watch(
  () => route.query.category,
  (raw) => {
    const next = raw ? Number(raw) : null
    if (next !== categoryId.value) {
      categoryId.value = next
      loadFeed()
    }
  }
)

onMounted(async () => {
  await loadCategories()
  await Promise.all([loadFeed(), loadHot()])
})
</script>

<style scoped>
.home__hero {
  margin-bottom: var(--sp-12);
  padding-bottom: var(--sp-8);
  border-bottom: 1px solid var(--border);
}

.home__body {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--sp-12);
  align-items: start;
}

.home__main {
  min-width: 0;
}

.home__section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--sp-6);
  padding-bottom: var(--sp-3);
  border-bottom: 2px solid var(--text-primary);
}

.home__section-title {
  font-family: var(--font-serif);
  font-size: var(--fs-24);
  font-weight: 800;
}

.home__filter-clear {
  background: none;
  border: 0;
  font-size: var(--fs-14);
  color: var(--text-muted);
  cursor: pointer;
}

.home__filter-clear:hover {
  color: var(--accent);
}

.home__feed-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-8);
}

.home__more {
  display: flex;
  justify-content: center;
  margin-top: var(--sp-8);
}

.home__aside {
  display: flex;
  flex-direction: column;
  gap: var(--sp-6);
  position: sticky;
  top: calc(var(--top-bar-height) + var(--sp-6));
}

@media (max-width: 1199px) {
  .home__body {
    gap: var(--sp-8);
  }
}

@media (max-width: 899px) {
  .home__body {
    grid-template-columns: 1fr;
  }
  .home__feed-grid {
    grid-template-columns: 1fr;
    gap: var(--sp-6);
  }
  .home__aside {
    position: static;
  }
}
</style>
