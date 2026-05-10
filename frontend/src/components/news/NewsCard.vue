<template>
  <router-link :to="`/news/${news.id}`" class="news-card" :class="{ 'news-card--feature': feature }">
    <div v-if="news.image" class="news-card__cover">
      <img :src="news.image" :alt="news.title" loading="lazy" />
    </div>
    <div class="news-card__body">
      <div v-if="news.tags?.length || categoryName" class="news-card__eyebrow">
        <span v-if="categoryName" class="news-card__category">{{ categoryName }}</span>
        <span v-for="tag in (news.tags || []).slice(0, 2)" :key="tag" class="news-card__tag">
          {{ tag }}
        </span>
      </div>

      <h3 class="news-card__title">{{ news.title }}</h3>

      <p v-if="news.summary || news.description" class="news-card__summary line-clamp-2">
        {{ news.summary || news.description }}
      </p>

      <div class="news-card__meta">
        <span v-if="news.author">{{ news.author }}</span>
        <span v-if="news.publishTime">{{ formatTime(news.publishTime) }}</span>
        <span v-if="typeof news.views === 'number'">{{ news.views }} 阅读</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  news: { type: Object, required: true },
  categories: { type: Array, default: () => [] },
  feature: { type: Boolean, default: false }
})

const categoryName = computed(() => {
  if (!props.news.categoryId) return ''
  const match = props.categories.find((c) => c.id === props.news.categoryId)
  return match ? match.name : ''
})

const formatTime = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const now = new Date()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 60) return `${Math.max(diffMin, 1)} 分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay} 天前`
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.news-card {
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
  text-decoration: none;
  color: var(--text-primary);
  transition: transform var(--transition-normal);
}

.news-card:hover {
  transform: translateY(-2px);
}

.news-card:hover .news-card__title {
  color: var(--accent);
}

.news-card__cover {
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.news-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.news-card:hover .news-card__cover img {
  transform: scale(1.03);
}

.news-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.news-card__eyebrow {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
  align-items: center;
}

.news-card__category {
  font-size: var(--fs-12);
  color: var(--accent);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.news-card__tag {
  font-size: var(--fs-12);
  color: var(--text-muted);
}

.news-card__title {
  font-family: var(--font-serif);
  font-size: var(--fs-20);
  font-weight: 700;
  line-height: var(--lh-tight);
  color: var(--text-primary);
  transition: color var(--transition-fast);
}

.news-card__summary {
  font-size: var(--fs-14);
  color: var(--text-secondary);
  line-height: var(--lh-normal);
}

.news-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-3);
  font-size: var(--fs-12);
  color: var(--text-muted);
}

.news-card--feature .news-card__title {
  font-size: var(--fs-36);
  line-height: var(--lh-tight);
}

.news-card--feature .news-card__summary {
  font-size: var(--fs-18);
  line-height: var(--lh-normal);
}

.news-card--feature .news-card__cover {
  aspect-ratio: 16 / 9;
}

@media (max-width: 899px) {
  .news-card--feature .news-card__title {
    font-size: var(--fs-24);
  }
}
</style>
