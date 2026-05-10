<template>
  <div class="favorites">
    <header class="page-header">
      <div>
        <h1 class="page-header__title">我的收藏</h1>
        <p class="page-header__subtitle">已收藏 {{ total }} 条新闻</p>
      </div>
      <div class="page-header__actions">
        <n-select
          v-model:value="sortOrder"
          :options="sortOptions"
          size="small"
          style="width: 140px"
          @update:value="onReload"
        />
        <n-popconfirm v-if="list.length" @positive-click="onClearAll">
          <template #trigger>
            <n-button>清空收藏</n-button>
          </template>
          确认清空全部收藏？此操作不可恢复
        </n-popconfirm>
      </div>
    </header>

    <div v-if="loading && !list.length" class="favorites__grid">
      <LoadingSkeleton v-for="n in 6" :key="n" variant="card" />
    </div>

    <div v-else-if="sortedList.length" class="favorites__grid">
      <div
        v-for="item in sortedList"
        :key="item.id"
        class="favorites__cell"
      >
        <NewsCard :news="item" :categories="categories" />
        <n-popconfirm @positive-click="onRemove(item.id)">
          <template #trigger>
            <button type="button" class="favorites__remove" aria-label="移除收藏">✕</button>
          </template>
          确认移除这条收藏？
        </n-popconfirm>
      </div>
    </div>

    <EmptyState
      v-else
      icon="🔖"
      title="还没有收藏任何新闻"
      description="去首页发现感兴趣的内容，点击收藏后会出现在这里"
    >
      <router-link to="/">
        <n-button type="primary">去首页看看</n-button>
      </router-link>
    </EmptyState>

    <div v-if="hasMore" class="favorites__more">
      <n-button :loading="loadingMore" size="large" @click="loadMore">加载更多</n-button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { NButton, NPopconfirm, NSelect, useMessage } from 'naive-ui'

import NewsCard from '../components/news/NewsCard.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import LoadingSkeleton from '../components/feedback/LoadingSkeleton.vue'
import { clearFavorites, fetchFavoriteList, removeFavorite } from '../services/favorite'
import { fetchCategories } from '../services/news'

const message = useMessage()

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)
const loadingMore = ref(false)
const sortOrder = ref('newest')
const categories = ref([])

const sortOptions = [
  { label: '最新优先', value: 'newest' },
  { label: '最早优先', value: 'oldest' }
]

const hasMore = computed(() => list.value.length < total.value)

const sortedList = computed(() => {
  const arr = [...list.value]
  arr.sort((a, b) => {
    const ta = new Date(a.favoriteTime || a.publishTime || 0).getTime()
    const tb = new Date(b.favoriteTime || b.publishTime || 0).getTime()
    return sortOrder.value === 'newest' ? tb - ta : ta - tb
  })
  return arr
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
    const data = await fetchFavoriteList({ page: page.value, pageSize })
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

const onReload = () => load()

const onRemove = async (id) => {
  try {
    await removeFavorite(id)
    list.value = list.value.filter((it) => it.id !== id)
    total.value = Math.max(0, total.value - 1)
    message.success('已移除')
  } catch (err) {
    message.error(err?.message || '移除失败')
  }
}

const onClearAll = async () => {
  try {
    await clearFavorites()
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

.page-header__actions {
  display: flex;
  gap: var(--sp-2);
  align-items: center;
}

.favorites__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--sp-8);
}

.favorites__cell {
  position: relative;
}

.favorites__remove {
  position: absolute;
  top: var(--sp-2);
  right: var(--sp-2);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border: 0;
  cursor: pointer;
  font-size: var(--fs-14);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.favorites__cell:hover .favorites__remove {
  opacity: 1;
}

.favorites__more {
  margin-top: var(--sp-8);
  display: flex;
  justify-content: center;
}

@media (max-width: 899px) {
  .favorites__grid {
    grid-template-columns: 1fr;
  }
  .favorites__remove {
    opacity: 1;
  }
}
</style>
