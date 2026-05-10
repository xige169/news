<template>
  <div class="history">
    <header class="page-header">
      <div>
        <h1 class="page-header__title">浏览历史</h1>
        <p class="page-header__subtitle">共 {{ total }} 条浏览记录</p>
      </div>
      <div class="page-header__actions">
        <n-popconfirm v-if="list.length" @positive-click="onClearAll">
          <template #trigger>
            <n-button>清空历史</n-button>
          </template>
          确认清空全部浏览历史？
        </n-popconfirm>
      </div>
    </header>

    <div v-if="loading && !list.length" class="history__skeletons">
      <LoadingSkeleton v-for="n in 4" :key="n" variant="row" />
    </div>

    <div v-else-if="grouped.length" class="history__groups">
      <section v-for="group in grouped" :key="group.label" class="history__group">
        <h2 class="history__group-label">{{ group.label }}</h2>
        <div class="history__group-list">
          <NewsListRow
            v-for="item in group.items"
            :key="item.historyId"
            :news="item"
            :categories="categories"
          >
            <template #meta>
              <span>{{ formatTime(item.viewTime) }} 阅读</span>
            </template>
            <template #actions>
              <n-popconfirm @positive-click="onRemove(item.historyId)">
                <template #trigger>
                  <button type="button" class="history__remove" aria-label="删除">✕</button>
                </template>
                确认删除这条记录？
              </n-popconfirm>
            </template>
          </NewsListRow>
        </div>
      </section>
    </div>

    <EmptyState
      v-else
      icon="🕒"
      title="还没有浏览记录"
      description="阅读过的新闻会出现在这里"
    >
      <router-link to="/">
        <n-button type="primary">去首页看看</n-button>
      </router-link>
    </EmptyState>

    <div v-if="hasMore" class="history__more">
      <n-button :loading="loadingMore" size="large" @click="loadMore">加载更多</n-button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { NButton, NPopconfirm, useMessage } from 'naive-ui'

import NewsListRow from '../components/news/NewsListRow.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'
import {
  clearHistoryEntries,
  fetchHistoryList,
  removeHistoryEntry
} from '../services/history'
import { fetchCategories } from '../services/news'

const message = useMessage()

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 15
const loading = ref(false)
const loadingMore = ref(false)
const categories = ref([])

const hasMore = computed(() => list.value.length < total.value)

const formatTime = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const groupKey = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(date)
  target.setHours(0, 0, 0, 0)
  const diff = Math.round((today - target) / 86400000)
  if (diff === 0) return '今天'
  if (diff === 1) return '昨天'
  return `${target.getFullYear()}-${String(target.getMonth() + 1).padStart(2, '0')}-${String(target.getDate()).padStart(2, '0')}`
}

const grouped = computed(() => {
  const buckets = new Map()
  for (const item of list.value) {
    const t = item.viewTime ? new Date(item.viewTime) : null
    if (!t || Number.isNaN(t.getTime())) continue
    const key = groupKey(t)
    if (!buckets.has(key)) buckets.set(key, [])
    buckets.get(key).push(item)
  }
  return Array.from(buckets.entries()).map(([label, items]) => ({ label, items }))
})

const loadCategories = async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
}

const load = async ({ append = false } = {}) => {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    list.value = []
    page.value = 1
  }
  try {
    const data = await fetchHistoryList({ page: page.value, pageSize })
    const next = data?.list || []
    list.value = append ? [...list.value, ...next] : next
    total.value = data?.total ?? list.value.length
  } catch (err) {
    message.error(err?.message || '加载失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = async () => {
  page.value += 1
  await load({ append: true })
}

const onRemove = async (historyId) => {
  try {
    await removeHistoryEntry(historyId)
    list.value = list.value.filter((it) => it.historyId !== historyId)
    total.value = Math.max(0, total.value - 1)
    message.success('已删除')
  } catch (err) {
    message.error(err?.message || '删除失败')
  }
}

const onClearAll = async () => {
  try {
    await clearHistoryEntries()
    list.value = []
    total.value = 0
    message.success('已清空')
  } catch (err) {
    message.error(err?.message || '清空失败')
  }
}

onMounted(async () => {
  await loadCategories()
  await load()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-4);
  margin-bottom: var(--sp-8);
  padding-bottom: var(--sp-4);
  border-bottom: 2px solid var(--text-primary);
}

.page-header__title {
  font-family: var(--font-serif);
  font-size: var(--fs-36);
}

.page-header__subtitle {
  margin-top: var(--sp-2);
  color: var(--text-secondary);
  font-size: var(--fs-14);
}

.history__group {
  margin-bottom: var(--sp-8);
}

.history__group-label {
  font-family: var(--font-sans);
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding-bottom: var(--sp-2);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--sp-2);
}

.history__remove {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  font-size: var(--fs-12);
}

.history__remove:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-on-accent);
}

.history__more {
  margin-top: var(--sp-8);
  display: flex;
  justify-content: center;
}
</style>
