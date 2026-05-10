<template>
  <div class="page-toolbar">
    <div class="page-toolbar__row">
      <div class="page-toolbar__filters">
        <slot name="filters" />
      </div>
      <div v-if="$slots.actions" class="page-toolbar__actions">
        <slot name="actions" />
      </div>
    </div>
    <div v-if="$slots.bulk" class="page-toolbar__bulk">
      <slot name="bulk" />
    </div>
  </div>
</template>

<style scoped>
.page-toolbar {
  position: sticky;
  top: var(--top-bar-height);
  z-index: 10;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-3) var(--sp-4);
  margin-bottom: var(--sp-4);
  box-shadow: var(--shadow-sm);
}

.page-toolbar__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-4);
}

.page-toolbar__filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--sp-2);
  flex: 1;
  min-width: 0;
}

.page-toolbar__actions {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  flex-shrink: 0;
}

.page-toolbar__bulk {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  margin-top: var(--sp-3);
  padding-top: var(--sp-3);
  border-top: 1px dashed var(--border);
  font-size: var(--fs-13);
  color: var(--text-secondary);
}
</style>
