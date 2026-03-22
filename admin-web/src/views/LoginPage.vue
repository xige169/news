<template>
  <div class="login-shell">
    <section class="login-hero">
      <p class="login-hero__eyebrow">HEADLINE CMS</p>
      <h1>标准新闻内容后台</h1>
      <p class="login-hero__copy">
        统一管理稿件、栏目与运营权限，后台交互按标准桌面管理台重构，不再复用移动端阅读页样式。
      </p>

      <div class="login-hero__panel">
        <strong>本期覆盖</strong>
        <span>仪表盘、新闻管理、分类管理、用户角色管理</span>
      </div>
    </section>

    <section class="login-card page-card">
      <div class="section-heading">
        <div>
          <h2 class="section-title">管理员登录</h2>
          <p class="section-copy">只允许具备后台权限的账号进入。</p>
        </div>
      </div>

      <el-form label-position="top" :model="form" @submit.prevent="handleSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入管理员用户名" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入登录密码" size="large" />
        </el-form-item>
        <el-button type="primary" size="large" class="login-submit" :loading="submitting" @click="handleSubmit">
          进入管理后台
        </el-button>
      </el-form>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { fetchAdminProfile, loginAdmin } from '../services/auth.js'
import { useAuthStore } from '../store/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const handleSubmit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写完整账号和密码')
    return
  }

  submitting.value = true
  try {
    const payload = await loginAdmin(form)
    authStore.setSession(payload)
    const profile = await fetchAdminProfile()

    if (profile.role !== 'admin') {
      authStore.clearSession()
      ElMessage.error('当前账号没有后台权限')
      return
    }

    authStore.setUserInfo(profile)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/dashboard')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '登录失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) 480px;
  gap: 28px;
  min-height: 100vh;
  padding: 36px;
}

.login-hero,
.login-card {
  min-height: calc(100vh - 72px);
}

.login-hero {
  position: relative;
  overflow: hidden;
  padding: 56px;
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.12), transparent 30%),
    linear-gradient(135deg, #7f1d1d 0%, #991b1b 36%, #111827 100%);
  color: #fff;
  box-shadow: var(--shadow-lg);
}

.login-hero::after {
  content: '';
  position: absolute;
  inset: auto -80px -110px auto;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.login-hero__eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  letter-spacing: 0.3em;
  color: rgba(255, 255, 255, 0.68);
}

.login-hero h1 {
  max-width: 420px;
  margin: 0;
  font-size: 58px;
  line-height: 1.02;
}

.login-hero__copy {
  max-width: 500px;
  margin: 24px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 18px;
  line-height: 1.8;
}

.login-hero__panel {
  display: grid;
  gap: 8px;
  width: 360px;
  margin-top: 56px;
  padding: 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.09);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
}

.login-card {
  align-self: stretch;
  padding: 34px;
}

.login-submit {
  width: 100%;
  margin-top: 8px;
}
</style>
