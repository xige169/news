<template>
  <div class="page-shell admin-layout">
    <aside class="admin-layout__sidebar">
      <div class="brand-block">
        <span class="brand-block__mark">TT</span>
        <div>
          <p class="brand-block__eyebrow">TODAY OPERATIONS</p>
          <h1>头条新闻管理台</h1>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        class="admin-menu"
        background-color="transparent"
        text-color="rgba(255,255,255,0.72)"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">仪表盘</el-menu-item>
        <el-menu-item index="/news">新闻管理</el-menu-item>
        <el-menu-item index="/categories">分类管理</el-menu-item>
        <el-menu-item index="/users">用户管理</el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <p>内容生产、栏目结构、权限角色集中管理。</p>
      </div>
    </aside>

    <main class="admin-layout__main">
      <header class="admin-layout__header page-card">
        <div>
          <p class="header-tag">NEWSROOM CONTROL CENTER</p>
          <h2>{{ route.meta.title || '管理后台' }}</h2>
        </div>

        <div class="header-actions">
          <div class="operator-card">
            <span class="operator-card__avatar">{{ authStore.nickname.slice(0, 1).toUpperCase() }}</span>
            <div>
              <strong>{{ authStore.nickname }}</strong>
              <span>{{ authStore.username }}</span>
            </div>
          </div>
          <el-button plain @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <section class="admin-layout__content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { logoutAdmin } from '../../services/auth.js'
import { useAuthStore } from '../../store/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = async () => {
  try {
    if (authStore.accessToken) {
      await logoutAdmin()
    }
  } catch {
    // 登出失败时直接走本地清理，避免阻塞退出
  } finally {
    authStore.clearSession()
    ElMessage.success('已退出后台')
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 292px minmax(0, 1fr);
}

.admin-layout__sidebar {
  position: sticky;
  top: 0;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 28px;
  min-height: 100vh;
  padding: 28px 22px;
  background: var(--bg-sidebar);
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.05);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 10px 8px;
}

.brand-block__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ef4444, #991b1b);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 18px 28px rgba(185, 28, 28, 0.25);
}

.brand-block__eyebrow {
  margin: 0 0 6px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  letter-spacing: 0.24em;
}

.brand-block h1 {
  margin: 0;
  color: #fff;
  font-size: 24px;
}

.admin-menu {
  display: grid;
  gap: 8px;
}

:deep(.admin-menu .el-menu-item) {
  height: 52px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
}

:deep(.admin-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(255, 255, 255, 0.08));
}

.sidebar-footer {
  align-self: end;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
}

.sidebar-footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  line-height: 1.7;
}

.admin-layout__main {
  min-width: 0;
  padding: 24px;
}

.admin-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 18px 24px;
}

.header-tag {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 11px;
  letter-spacing: 0.28em;
}

.admin-layout__header h2 {
  margin: 0;
  font-size: 26px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.operator-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.operator-card__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
}

.operator-card strong,
.operator-card span {
  display: block;
}

.operator-card span {
  margin-top: 3px;
  color: var(--text-secondary);
  font-size: 12px;
}

.admin-layout__content {
  padding-top: 24px;
}
</style>
