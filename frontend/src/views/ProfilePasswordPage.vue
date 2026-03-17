<template>
  <div class="page">
    <section class="hero-card compact">
      <p class="eyebrow">Security</p>
      <h1 class="hero-title">修改密码</h1>
      <p class="hero-subtitle">密码修改成功后仍保持当前登录态，由后端负责校验旧密码。</p>
    </section>

    <section class="section-card">
      <van-form @submit="handleSubmit">
        <van-field
          v-model="form.oldPassword"
          type="password"
          label="旧密码"
          placeholder="请输入旧密码"
          required
        />
        <van-field
          v-model="form.newPassword"
          type="password"
          label="新密码"
          placeholder="请输入新密码"
          required
        />
        <div class="form-actions">
          <van-button block type="primary" native-type="submit" :loading="submitting">更新密码</van-button>
        </div>
      </van-form>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { updatePassword } from '../services/auth.js'

const router = useRouter()
const submitting = ref(false)
const form = reactive({
  oldPassword: '',
  newPassword: ''
})

const handleSubmit = async () => {
  submitting.value = true

  try {
    await updatePassword(form)
    showToast('密码修改成功')
    router.replace('/profile')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '密码修改失败')
  } finally {
    submitting.value = false
  }
}
</script>
