<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-card__header">
        <h1>登录</h1>
        <p>登录以使用收藏、历史和个人中心</p>
      </header>

      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="top"
        size="large"
        @submit.prevent
      >
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formValue.username" placeholder="请输入用户名" clearable />
        </n-form-item>

        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
            @keydown.enter="onSubmit"
          />
        </n-form-item>

        <n-button
          type="primary"
          size="large"
          block
          :loading="submitting"
          @click="onSubmit"
        >
          登录
        </n-button>
      </n-form>

      <div class="auth-card__footer">
        还没有账号？
        <router-link :to="{ path: '/register', query: route.query }">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { login, fetchCurrentUser } from '../services/auth'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const formRef = ref(null)
const submitting = ref(false)
const formValue = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const onSubmit = () => {
  formRef.value
    ?.validate(async (errors) => {
      if (errors) return
      submitting.value = true
      try {
        const payload = await login({
          username: formValue.value.username.trim(),
          password: formValue.value.password
        })
        auth.setAuth(payload)
        try {
          const userInfo = await fetchCurrentUser()
          auth.setUserInfo(userInfo)
        } catch {
          // tolerate /info failure — login already succeeded
        }
        message.success('登录成功')
        const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
        router.replace(redirect)
      } catch (err) {
        message.error(err?.message || '登录失败')
      } finally {
        submitting.value = false
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - var(--top-bar-height) - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  margin: calc(var(--sp-8) * -1) calc(var(--sp-6) * -1);
  padding: var(--sp-12) var(--sp-6);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
  box-shadow: var(--shadow-md);
}

.auth-card__header {
  text-align: center;
  margin-bottom: var(--sp-8);
}

.auth-card__header h1 {
  font-family: var(--font-serif);
  font-size: var(--fs-30);
  margin-bottom: var(--sp-2);
}

.auth-card__header p {
  font-size: var(--fs-14);
  color: var(--text-secondary);
}

.auth-card__footer {
  margin-top: var(--sp-6);
  text-align: center;
  font-size: var(--fs-14);
  color: var(--text-secondary);
}

.auth-card__footer a {
  margin-left: var(--sp-1);
}

@media (max-width: 899px) {
  .auth-page {
    margin: calc(var(--sp-5) * -1) calc(var(--sp-4) * -1);
    padding: var(--sp-8) var(--sp-4);
  }
  .auth-card {
    padding: var(--sp-6);
  }
}
</style>
