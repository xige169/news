<template>
  <header class="admin-topbar">
    <div class="admin-topbar__left">
      <h1 class="admin-topbar__title">{{ pageTitle }}</h1>
      <nav v-if="breadcrumbs.length" class="admin-topbar__breadcrumb">
        <template v-for="(crumb, idx) in breadcrumbs" :key="idx">
          <span v-if="idx > 0" class="admin-topbar__breadcrumb-sep">/</span>
          <router-link v-if="crumb.path" :to="crumb.path">{{ crumb.label }}</router-link>
          <span v-else>{{ crumb.label }}</span>
        </template>
      </nav>
    </div>

    <div class="admin-topbar__right">
      <el-dropdown trigger="click" @command="onCommand">
        <button type="button" class="admin-topbar__user">
          <span class="admin-topbar__avatar">{{ avatarChar }}</span>
          <span class="admin-topbar__username">{{ auth.nickname }}</span>
          <el-icon size="14"><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <span class="admin-topbar__menu-meta">{{ auth.username }}</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElDropdown, ElDropdownItem, ElDropdownMenu, ElIcon, ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

import { useAuthStore } from '../../store/auth.js'
import { logoutAdmin } from '../../services/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const pageTitle = computed(() => route.meta.title || '管理后台')

const breadcrumbs = computed(() => {
  const segments = []
  if (route.path.startsWith('/news')) {
    segments.push({ label: '内容管理', path: null })
    if (route.path === '/news') {
      segments.push({ label: '新闻列表' })
    } else if (route.path === '/news/create') {
      segments.push({ label: '新闻列表', path: '/news' })
      segments.push({ label: '新建稿件' })
    } else {
      segments.push({ label: '新闻列表', path: '/news' })
      segments.push({ label: '编辑稿件' })
    }
  } else if (route.path.startsWith('/categories')) {
    segments.push({ label: '内容管理', path: null })
    segments.push({ label: '栏目管理' })
  } else if (route.path.startsWith('/users')) {
    segments.push({ label: '用户管理' })
  } else if (route.path.startsWith('/dashboard') || route.path === '/') {
    segments.push({ label: '仪表盘' })
  }
  return segments
})

const avatarChar = computed(() => (auth.nickname || '管').slice(0, 1).toUpperCase())

const onCommand = async (command) => {
  if (command !== 'logout') return
  try {
    if (auth.accessToken) await logoutAdmin()
  } catch {
    // ignore
  }
  auth.clearSession()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.admin-topbar {
  height: var(--top-bar-height);
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--sp-6);
  position: sticky;
  top: 0;
  z-index: 50;
}

.admin-topbar__left {
  display: flex;
  align-items: baseline;
  gap: var(--sp-4);
  min-width: 0;
}

.admin-topbar__title {
  font-size: var(--fs-18);
  font-weight: 600;
  color: var(--text-primary);
}

.admin-topbar__breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: var(--fs-13);
  color: var(--text-muted);
}

.admin-topbar__breadcrumb a {
  color: var(--text-secondary);
}

.admin-topbar__breadcrumb a:hover {
  color: var(--accent);
}

.admin-topbar__breadcrumb-sep {
  color: var(--text-muted);
}

.admin-topbar__right {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.admin-topbar__user {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: none;
  border: 0;
  padding: var(--sp-1) var(--sp-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-primary);
  transition: background var(--transition-fast);
}

.admin-topbar__user:hover {
  background: var(--bg-elevated);
}

.admin-topbar__avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--text-on-accent);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--fs-13);
  font-weight: 600;
}

.admin-topbar__username {
  font-size: var(--fs-14);
}

.admin-topbar__menu-meta {
  font-size: var(--fs-12);
  color: var(--text-muted);
}
</style>
