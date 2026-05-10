<template>
  <span class="status-chip" :class="`status-chip--${tone}`">
    <span class="status-chip__dot" />
    {{ label || statusLabels[status] || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: '' },
  label: { type: String, default: '' }
})

const statusLabels = {
  published: '已发布',
  draft: '草稿',
  offline: '已下线',
  active: '正常',
  banned: '已封禁',
  admin: '管理员',
  user: '普通用户'
}

const toneMap = {
  published: 'success',
  draft: 'warning',
  offline: 'muted',
  active: 'success',
  banned: 'danger',
  admin: 'accent',
  user: 'muted'
}

const tone = computed(() => toneMap[props.status] || 'muted')
</script>

<style scoped>
.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: var(--fs-12);
  font-weight: 500;
  line-height: 18px;
}

.status-chip__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-chip--success {
  background: var(--success-soft);
  color: var(--success);
}

.status-chip--warning {
  background: var(--warning-soft);
  color: var(--warning);
}

.status-chip--danger {
  background: var(--danger-soft);
  color: var(--danger);
}

.status-chip--accent {
  background: var(--accent-soft);
  color: var(--accent);
}

.status-chip--muted {
  background: var(--muted-soft);
  color: var(--text-secondary);
}
</style>
