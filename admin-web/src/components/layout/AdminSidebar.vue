<template>
  <aside class="admin-sidebar">
    <div class="admin-sidebar__brand">
      <span class="admin-sidebar__brand-mark">N</span>
      <div class="admin-sidebar__brand-text">
        <strong>新闻管理</strong>
        <span>NEWSROOM ADMIN</span>
      </div>
    </div>

    <nav class="admin-sidebar__nav">
      <template v-for="item in items" :key="item.label">
        <router-link
          v-if="!item.children"
          :to="item.path"
          class="admin-sidebar__link"
          :class="{ 'admin-sidebar__link--active': isActive(item.path) }"
        >
          <component :is="item.icon" class="admin-sidebar__icon" />
          <span>{{ item.label }}</span>
        </router-link>
        <div v-else class="admin-sidebar__group">
          <div class="admin-sidebar__group-label">{{ item.label }}</div>
          <router-link
            v-for="child in item.children"
            :key="child.path"
            :to="child.path"
            class="admin-sidebar__link admin-sidebar__link--child"
            :class="{ 'admin-sidebar__link--active': isActive(child.path, child.exact) }"
          >
            <component :is="child.icon" class="admin-sidebar__icon" />
            <span>{{ child.label }}</span>
          </router-link>
        </div>
      </template>
    </nav>
  </aside>
</template>

<script setup>
import { markRaw } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  Document,
  EditPen,
  Folder,
  User
} from '@element-plus/icons-vue'

const route = useRoute()

const items = [
  { label: '仪表盘', path: '/dashboard', icon: markRaw(DataAnalysis) },
  {
    label: '内容管理',
    children: [
      { label: '新闻列表', path: '/news', icon: markRaw(Document) },
      { label: '栏目管理', path: '/categories', icon: markRaw(Folder) },
      { label: '新建稿件', path: '/news/create', icon: markRaw(EditPen), exact: true }
    ]
  },
  { label: '用户管理', path: '/users', icon: markRaw(User) }
]

const isActive = (path, exact = false) => {
  if (exact) return route.path === path
  if (path === '/dashboard') return route.path === '/dashboard' || route.path === '/'
  if (path === '/news') return route.path === '/news' || route.path.startsWith('/news/') && route.path !== '/news/create'
  return route.path === path || route.path.startsWith(`${path}/`)
}
</script>

<style scoped>
.admin-sidebar {
  width: var(--sidebar-width);
  background: var(--admin-sidebar-bg);
  color: var(--admin-sidebar-text);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
}

.admin-sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-5) var(--sp-5);
  border-bottom: 1px solid var(--admin-sidebar-border);
  height: var(--top-bar-height);
}

.admin-sidebar__brand-mark {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--accent);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--fs-16);
}

.admin-sidebar__brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.admin-sidebar__brand-text strong {
  color: var(--admin-sidebar-text-active);
  font-size: var(--fs-14);
  font-weight: 600;
}

.admin-sidebar__brand-text span {
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--admin-sidebar-text-muted);
}

.admin-sidebar__nav {
  flex: 1;
  padding: var(--sp-3) var(--sp-2);
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
}

.admin-sidebar__group {
  margin-top: var(--sp-3);
}

.admin-sidebar__group-label {
  padding: var(--sp-2) var(--sp-3);
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--admin-sidebar-text-muted);
}

.admin-sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  color: var(--admin-sidebar-text);
  border-radius: var(--radius-md);
  font-size: var(--fs-14);
  position: relative;
  transition: all var(--transition-fast);
}

.admin-sidebar__link:hover {
  background: var(--admin-sidebar-bg-hover);
  color: var(--admin-sidebar-text-active);
}

.admin-sidebar__link--active {
  background: var(--admin-sidebar-bg-active);
  color: var(--admin-sidebar-text-active);
}

.admin-sidebar__link--active::before {
  content: '';
  position: absolute;
  left: -2px;
  top: 8px;
  bottom: 8px;
  width: 3px;
  background: var(--accent);
  border-radius: 2px;
}

.admin-sidebar__icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}
</style>
