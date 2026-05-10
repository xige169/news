<template>
  <div class="search">
    <header class="search__header">
      <h1 class="search__title">搜索</h1>
      <form class="search__form" @submit.prevent="onSubmit">
        <n-input
          v-model:value="keyword"
          size="large"
          placeholder="输入关键词搜索新闻"
          clearable
        />
        <n-button type="primary" size="large" attr-type="submit">搜索</n-button>
      </form>

      <div v-if="history.length" class="search__history">
        <span class="search__history-label">最近搜索</span>
        <button
          v-for="word in history"
          :key="word"
          type="button"
          class="search__history-chip"
          @click="onHistoryClick(word)"
        >
          {{ word }}
        </button>
        <button type="button" class="search__history-clear" @click="clearHistory">
          清空
        </button>
      </div>
    </header>

    <section v-if="hasSearched" class="search__results">
      <header class="search__results-header">
        <span>共找到 <strong>{{ total }}</strong> 条结果</span>
      </header>

      <div v-if="loading && !list.length" class="search__skeletons">
        <LoadingSkeleton v-for="n in 4" :key="n" variant="row" />
      </div>

      <div v-else-if="list.length" class="search__list">
        <NewsListRow
          v-for="item in list"
          :key="item.id"
          :news="item"
          :categories="categories"
          :highlight="submittedKeyword"
        />
      </div>

      <EmptyState
        v-else
        icon="🔍"
        title="未找到相关新闻"
        description="尝试更换关键词，或浏览首页推荐"
      >
        <router-link to="/">
          <n-button>返回首页</n-button>
        </router-link>
      </EmptyState>

      <div v-if="hasMore" class="search__more">
        <n-button :loading="loadingMore" size="large" @click="loadMore">加载更多</n-button>
      </div>
    </section>

    <section v-else class="search__placeholder">
      <EmptyState
        icon="🔎"
        title="搜索新闻"
        description="输入关键词开始搜索"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NInput, useMessage } from 'naive-ui'

import NewsListRow from '../components/news/NewsListRow.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'
import { fetchCategories, searchNews } from '../services/news'

const HISTORY_KEY = 'news.search.history'
const HISTORY_MAX = 10

const route = useRoute()
const router = useRouter()
const message = useMessage()

const keyword = ref('')
const submittedKeyword = ref('')
const categories = ref([])
const history = ref([])

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const loadingMore = ref(false)
const hasSearched = ref(false)
const hasMore = computed(() => list.value.length < total.value)

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    history.value = raw ? JSON.parse(raw) : []
  } catch {
    history.value = []
  }
}

const saveHistory = (word) => {
  if (!word) return
  const next = [word, ...history.value.filter((w) => w !== word)].slice(0, HISTORY_MAX)
  history.value = next
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next))
  } catch {
    // ignore
  }
}

const clearHistory = () => {
  history.value = []
  try {
    localStorage.removeItem(HISTORY_KEY)
  } catch {
    // ignore
  }
}

const runSearch = async ({ append = false } = {}) => {
  const query = submittedKeyword.value.trim()
  if (!query) return

  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    list.value = []
    page.value = 1
  }

  try {
    const data = await searchNews({
      keyword: query,
      page: page.value,
      pageSize
    })
    const next = data?.list || []
    list.value = append ? [...list.value, ...next] : next
    total.value = data?.total ?? list.value.length
    hasSearched.value = true
  } catch (err) {
    message.error(err?.message || '搜索失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const onSubmit = () => {
  const next = keyword.value.trim()
  if (!next) return
  router.replace({ path: '/search', query: { keyword: next } })
  saveHistory(next)
  submittedKeyword.value = next
  runSearch()
}

const onHistoryClick = (word) => {
  keyword.value = word
  router.replace({ path: '/search', query: { keyword: word } })
  submittedKeyword.value = word
  runSearch()
}

const loadMore = async () => {
  page.value += 1
  await runSearch({ append: true })
}

const loadCategories = async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
}

watch(
  () => route.query.keyword,
  (raw) => {
    const next = typeof raw === 'string' ? raw.trim() : ''
    keyword.value = next
    submittedKeyword.value = next
    if (next) {
      runSearch()
    } else {
      list.value = []
      hasSearched.value = false
      total.value = 0
    }
  },
  { immediate: true }
)

onMounted(() => {
  loadHistory()
  loadCategories()
})
</script>

<style scoped>
.search {
  max-width: 900px;
  margin: 0 auto;
}

.search__header {
  margin-bottom: var(--sp-8);
  padding-bottom: var(--sp-6);
  border-bottom: 1px solid var(--border);
}

.search__title {
  font-family: var(--font-serif);
  font-size: var(--fs-36);
  margin-bottom: var(--sp-5);
}

.search__form {
  display: flex;
  gap: var(--sp-3);
  margin-bottom: var(--sp-5);
}

.search__history {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--sp-2);
}

.search__history-label {
  font-size: var(--fs-12);
  color: var(--text-muted);
  margin-right: var(--sp-2);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.search__history-chip {
  background: var(--bg-elevated);
  border: 0;
  padding: var(--sp-1) var(--sp-3);
  border-radius: 999px;
  font-size: var(--fs-13, 13px);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search__history-chip:hover {
  background: var(--accent-soft);
  color: var(--accent);
}

.search__history-clear {
  background: none;
  border: 0;
  color: var(--text-muted);
  font-size: var(--fs-12);
  cursor: pointer;
  margin-left: var(--sp-2);
}

.search__history-clear:hover {
  color: var(--accent);
}

.search__results-header {
  margin-bottom: var(--sp-3);
  color: var(--text-secondary);
  font-size: var(--fs-14);
}

.search__results-header strong {
  color: var(--accent);
  margin: 0 var(--sp-1);
}

.search__list {
  display: flex;
  flex-direction: column;
}

.search__skeletons {
  display: flex;
  flex-direction: column;
}

.search__more {
  display: flex;
  justify-content: center;
  margin-top: var(--sp-8);
}

.search__placeholder {
  padding: var(--sp-12) 0;
}
</style>
