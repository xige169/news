<template>
  <div class="skeleton" :class="`skeleton--${variant}`">
    <template v-if="variant === 'card'">
      <div class="skeleton__cover" />
      <div class="skeleton__line skeleton__line--title" />
      <div class="skeleton__line skeleton__line--full" />
      <div class="skeleton__line skeleton__line--short" />
    </template>
    <template v-else-if="variant === 'row'">
      <div class="skeleton__row">
        <div class="skeleton__row-body">
          <div class="skeleton__line skeleton__line--title" />
          <div class="skeleton__line skeleton__line--full" />
          <div class="skeleton__line skeleton__line--short" />
        </div>
        <div class="skeleton__row-cover" />
      </div>
    </template>
    <template v-else>
      <div class="skeleton__line skeleton__line--full" />
    </template>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'card' }
})
</script>

<style scoped>
.skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
}

.skeleton__cover {
  aspect-ratio: 16 / 10;
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  animation: pulse 1.4s ease-in-out infinite;
}

.skeleton__line {
  height: 12px;
  border-radius: 4px;
  background: var(--bg-elevated);
  animation: pulse 1.4s ease-in-out infinite;
}

.skeleton__line--title {
  height: 20px;
  width: 80%;
}

.skeleton__line--full {
  width: 100%;
}

.skeleton__line--short {
  width: 60%;
}

.skeleton__row {
  display: flex;
  gap: var(--sp-5);
  padding: var(--sp-5) 0;
  border-bottom: 1px solid var(--border);
}

.skeleton__row-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.skeleton__row-cover {
  flex: 0 0 180px;
  aspect-ratio: 16 / 10;
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
