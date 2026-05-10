<template>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <span class="site-footer__logo">新闻</span>
        <p class="site-footer__tagline">读懂世界的入口</p>
      </div>

      <div class="site-footer__col">
        <h4>内容</h4>
        <router-link to="/">首页</router-link>
        <router-link to="/search">搜索</router-link>
      </div>

      <div class="site-footer__col">
        <h4>账户</h4>
        <template v-if="auth.isLoggedIn">
          <router-link to="/profile">个人中心</router-link>
          <router-link to="/favorites">我的收藏</router-link>
          <router-link to="/history">浏览历史</router-link>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
          <router-link to="/register">注册</router-link>
        </template>
      </div>

      <div class="site-footer__col">
        <h4>关于</h4>
        <span class="site-footer__muted">新闻客户端 · 学习项目</span>
        <span class="site-footer__muted">FastAPI + Vue 3</span>
      </div>
    </div>

    <div class="site-footer__bottom">
      <span>© {{ year }} 新闻客户端</span>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

import { useAuthStore } from '../../store/auth'

const auth = useAuthStore()
const year = computed(() => new Date().getFullYear())
</script>

<style scoped>
.site-footer {
  margin-top: var(--sp-16);
  background: var(--bg-elevated);
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
}

.site-footer__inner {
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--sp-12) var(--sp-6) var(--sp-8);
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--sp-8);
}

.site-footer__brand {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.site-footer__logo {
  font-family: var(--font-serif);
  font-size: var(--fs-24);
  font-weight: 800;
  color: var(--text-primary);
  border-bottom: 3px solid var(--accent);
  padding-bottom: 2px;
  display: inline-block;
  align-self: flex-start;
}

.site-footer__tagline {
  margin-top: var(--sp-2);
  color: var(--text-secondary);
  font-size: var(--fs-14);
}

.site-footer__col {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.site-footer__col h4 {
  font-family: var(--font-sans);
  font-size: var(--fs-14);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--sp-2);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.site-footer__col a {
  color: var(--text-secondary);
  font-size: var(--fs-14);
  transition: color var(--transition-fast);
}

.site-footer__col a:hover {
  color: var(--accent);
}

.site-footer__muted {
  color: var(--text-muted);
  font-size: var(--fs-14);
}

.site-footer__bottom {
  border-top: 1px solid var(--border);
  padding: var(--sp-5) var(--sp-6);
  text-align: center;
  color: var(--text-muted);
  font-size: var(--fs-12);
}

@media (max-width: 899px) {
  .site-footer__inner {
    grid-template-columns: 1fr 1fr;
    padding: var(--sp-8) var(--sp-4);
    gap: var(--sp-6);
  }
}
</style>
