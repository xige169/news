<template>
  <aside class="category-nav">
    <div class="category-nav__header">
      <h3>分类</h3>
    </div>
    <div class="category-nav__chips">
      <button
        type="button"
        class="category-nav__chip"
        :class="{ 'category-nav__chip--active': !modelValue }"
        @click="onSelect(null)"
      >
        全部
      </button>
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="category-nav__chip"
        :class="{ 'category-nav__chip--active': modelValue === item.id }"
        @click="onSelect(item.id)"
      >
        {{ item.name }}
      </button>
    </div>
  </aside>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, default: () => [] },
  modelValue: { type: Number, default: null }
})

const emit = defineEmits(['update:modelValue', 'change'])

const onSelect = (id) => {
  emit('update:modelValue', id)
  emit('change', id)
}
</script>

<style scoped>
.category-nav {
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: var(--sp-5);
}

.category-nav__header {
  margin-bottom: var(--sp-4);
}

.category-nav__header h3 {
  font-family: var(--font-serif);
  font-size: var(--fs-18);
  font-weight: 700;
  position: relative;
  padding-left: var(--sp-3);
}

.category-nav__header h3::before {
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

.category-nav__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
}

.category-nav__chip {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: var(--sp-2) var(--sp-4);
  font-size: var(--fs-14);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-nav__chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.category-nav__chip--active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-on-accent);
}

.category-nav__chip--active:hover {
  color: var(--text-on-accent);
}
</style>
