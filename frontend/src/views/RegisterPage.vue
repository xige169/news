<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-card__header">
        <h1>注册</h1>
        <p>创建账号开启你的新闻阅读旅程</p>
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
          <n-input v-model:value="formValue.username" placeholder="3-20 个字符" clearable />
        </n-form-item>

        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            show-password-on="click"
            placeholder="至少 6 位"
          />
        </n-form-item>

        <n-form-item label="确认密码" path="confirm">
          <n-input
            v-model:value="formValue.confirm"
            type="password"
            show-password-on="click"
            placeholder="再次输入密码"
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
          注册
        </n-button>
      </n-form>

      <div class="auth-card__footer">
        已有账号？
        <router-link :to="{ path: '/login', query: route.query }">直接登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { register, fetchCurrentUser } from '../services/auth'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const formRef = ref(null)
const submitting = ref(false)
const formValue = ref({ username: '', password: '', confirm: '' })

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, value) =>
        value === formValue.value.password || new Error('两次密码不一致'),
      trigger: 'blur'
    }
  ]
}

const onSubmit = () => {
  formRef.value
    ?.validate(async (errors) => {
      if (errors) return
      submitting.value = true
      try {
        const payload = await register({
          username: formValue.value.username.trim(),
          password: formValue.value.password
        })
        auth.setAuth(payload)
        try {
          const userInfo = await fetchCurrentUser()
          auth.setUserInfo(userInfo)
        } catch {
          // ignore
        }
        message.success('注册成功')
        const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
        router.replace(redirect)
      } catch (err) {
        message.error(err?.message || '注册失败')
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
