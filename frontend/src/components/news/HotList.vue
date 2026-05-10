<template>
  <aside class="hot-list">
    <div class="hot-list__header">
      <h3>热门</h3>
      <slot name="extra" />
    </div>
    <ol class="hot-list__items">
      <li v-for="(item, index) in items" :key="item.id" class="hot-list__item">
        <span class="hot-list__rank" :class="{ 'hot-list__rank--top': index < 3 }">
          {{ index + 1 }}
        </span>
        <router-link :to="`/news/${item.id}`" class="hot-list__title">
          {{ item.title }}
        </router-link>
      </li>
    </ol>
    <div v-if="!items.length && !loading" class="hot-list__empty">暂无数据</div>
    <div v-if="loading" class="hot-list__empty">加载中...</div>
  </aside>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})
</script>

<style scoped>
.hot-list {
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: var(--sp-5);
}

.hot-list__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--sp-4);
}

.hot-list__header h3 {
  font-family: var(--font-serif);
  font-size: var(--fs-18);
  font-weight: 700;
  position: relative;
  padding-left: var(--sp-3);
}

.hot-list__header h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: var(--accent);
  border-radius: 2px;
}

.hot-list__items {
  display: flex;
  flex-direction: column;
}

.hot-list__item {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-3);
  padding: var(--sp-3) 0;
  border-bottom: 1px dashed var(--border);
}

.hot-list__item:last-child {
  border-bottom: 0;
}

.hot-list__rank {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--text-muted);
  background: var(--bg-page);
  border-radius: var(--radius-sm);
}

.hot-list__rank--top {
  background: var(--accent);
  color: var(--text-on-accent);
}

.hot-list__title {
  font-size: var(--fs-14);
  color: var(--text-primary);
  line-height: var(--lh-snug);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.hot-list__title:hover {
  color: var(--accent);
}

.hot-list__empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--fs-14);
  padding: var(--sp-6) 0;
}
</style>
