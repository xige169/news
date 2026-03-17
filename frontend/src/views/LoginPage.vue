<template>
  <div class="page auth-page">
    <section class="hero-card hero-card--editorial">
      <p class="eyebrow">Sign In</p>
      <h1 class="hero-title">登录你的新闻账户</h1>
      <p class="hero-subtitle">登录后可同步收藏、浏览历史和个人资料。</p>
    </section>

    <section class="section-card">
      <van-form @submit="handleSubmit">
        <van-field v-model="form.username" name="username" label="用户名" placeholder="请输入用户名" required />
        <van-field
          v-model="form.password"
          name="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
          required
        />
        <div class="form-actions">
          <van-button block type="primary" native-type="submit" :loading="submitting">登录</van-button>
        </div>
      </van-form>
      <p class="form-switch">
        还没有账号？
        <button class="text-button" type="button" @click="router.push('/register')">去注册</button>
      </p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

import { login } from '../services/auth.js'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const submitting = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  submitting.value = true

  try {
    const payload = await login(form)
    authStore.setAuth(payload)
    showToast('登录成功')
    router.replace(String(route.query.redirect || '/'))
  } catch (error) {
    showToast(error instanceof Error ? error.message : '登录失败')
  } finally {
    submitting.value = false
  }
}
</script>
