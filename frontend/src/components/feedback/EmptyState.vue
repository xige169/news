<template>
  <div class="empty-state">
    <div class="empty-state__icon">{{ icon }}</div>
    <h3 v-if="title" class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__description">{{ description }}</p>
    <div v-if="$slots.default" class="empty-state__action">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, default: '' },
  description: { type: String, default: '' }
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: var(--sp-12) var(--sp-6);
  color: var(--text-muted);
}

.empty-state__icon {
  font-size: 56px;
  margin-bottom: var(--sp-4);
  filter: grayscale(0.4);
}

.empty-state__title {
  font-family: var(--font-serif);
  font-size: var(--fs-20);
  color: var(--text-primary);
  margin-bottom: var(--sp-2);
}

.empty-state__description {
  font-size: var(--fs-14);
  color: var(--text-secondary);
  max-width: 360px;
  margin: 0 auto;
  line-height: var(--lh-normal);
}

.empty-state__action {
  margin-top: var(--sp-5);
}
</style>
