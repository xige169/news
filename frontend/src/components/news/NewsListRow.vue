<template>
  <router-link :to="`/news/${news.id}`" class="news-row">
    <div class="news-row__body">
      <div v-if="categoryName" class="news-row__category">{{ categoryName }}</div>
      <h3 class="news-row__title" v-html="renderedTitle" />
      <p v-if="news.summary || news.description" class="news-row__summary line-clamp-2">
        {{ news.summary || news.description }}
      </p>
      <div class="news-row__meta">
        <span v-if="news.author">{{ news.author }}</span>
        <span v-if="news.publishTime">{{ formatTime(news.publishTime) }}</span>
        <span v-if="typeof news.views === 'number'">{{ news.views }} 阅读</span>
        <slot name="meta" />
      </div>
    </div>
    <div v-if="news.image" class="news-row__cover">
      <img :src="news.image" :alt="news.title" loading="lazy" />
    </div>
    <div v-if="$slots.actions" class="news-row__actions" @click.stop.prevent>
      <slot name="actions" />
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  news: { type: Object, required: true },
  categories: { type: Array, default: () => [] },
  highlight: { type: String, default: '' }
})

const categoryName = computed(() => {
  if (!props.news.categoryId) return ''
  const match = props.categories.find((c) => c.id === props.news.categoryId)
  return match ? match.name : ''
})

const escapeHtml = (text) =>
  String(text).replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[ch])

const renderedTitle = computed(() => {
  const title = props.news.title || ''
  if (!props.highlight) return escapeHtml(title)
  const safe = escapeHtml(title)
  const safeQuery = escapeHtml(props.highlight).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  if (!safeQuery) return safe
  const re = new RegExp(`(${safeQuery})`, 'gi')
  return safe.replace(re, '<mark>$1</mark>')
})

const formatTime = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.news-row {
  display: flex;
  align-items: stretch;
  gap: var(--sp-5);
  padding: var(--sp-5) 0;
  border-bottom: 1px solid var(--border);
  text-decoration: none;
  color: var(--text-primary);
  position: relative;
}

.news-row:hover .news-row__title {
  color: var(--accent);
}

.news-row__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  min-width: 0;
}

.news-row__category {
  font-size: var(--fs-12);
  color: var(--accent);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.news-row__title {
  font-family: var(--font-serif);
  font-size: var(--fs-20);
  font-weight: 700;
  line-height: var(--lh-tight);
  color: var(--text-primary);
  transition: color var(--transition-fast);
  margin: 0;
}

.news-row__title :deep(mark) {
  background: var(--accent-soft);
  color: var(--accent-hover);
  padding: 0 2px;
  border-radius: 2px;
}

.news-row__summary {
  font-size: var(--fs-14);
  color: var(--text-secondary);
  line-height: var(--lh-normal);
}

.news-row__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-3);
  font-size: var(--fs-12);
  color: var(--text-muted);
  margin-top: auto;
}

.news-row__cover {
  flex: 0 0 180px;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.news-row__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-row__actions {
  position: absolute;
  top: var(--sp-4);
  right: 0;
  display: flex;
  gap: var(--sp-2);
}

@media (max-width: 899px) {
  .news-row {
    gap: var(--sp-3);
  }
  .news-row__cover {
    flex: 0 0 110px;
  }
  .news-row__title {
    font-size: var(--fs-18);
  }
}
</style>
