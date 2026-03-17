<template>
  <div class="page auth-page">
    <section class="hero-card hero-card--editorial">
      <p class="eyebrow">Create Account</p>
      <h1 class="hero-title">创建新闻阅读账户</h1>
      <p class="hero-subtitle">注册后立即获得登录态，可直接进入首页继续浏览。</p>
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
          <van-button block type="primary" native-type="submit" :loading="submitting">注册并登录</van-button>
        </div>
      </van-form>
      <p class="form-switch">
        已有账号？
        <button class="text-button" type="button" @click="router.push('/login')">去登录</button>
      </p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { register } from '../services/auth.js'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  submitting.value = true

  try {
    const payload = await register(form)
    authStore.setAuth(payload)
    showToast('注册成功')
    router.replace('/')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '注册失败')
  } finally {
    submitting.value = false
  }
}
</script>
