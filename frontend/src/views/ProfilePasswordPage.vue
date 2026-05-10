<template>
  <div class="profile-password">
    <header class="profile-password__header">
      <router-link to="/profile" class="profile-password__back">← 返回个人中心</router-link>
      <h1>修改密码</h1>
      <p class="profile-password__hint">建议使用包含字母和数字的强密码，长度不少于 6 位</p>
    </header>

    <div class="profile-password__card">
      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="top"
        size="large"
      >
        <n-form-item label="当前密码" path="current">
          <n-input
            v-model:value="formValue.current"
            type="password"
            show-password-on="click"
            placeholder="输入当前密码"
          />
        </n-form-item>

        <n-form-item label="新密码" path="next">
          <n-input
            v-model:value="formValue.next"
            type="password"
            show-password-on="click"
            placeholder="至少 6 位"
          />
        </n-form-item>

        <n-form-item label="确认新密码" path="confirm">
          <n-input
            v-model:value="formValue.confirm"
            type="password"
            show-password-on="click"
            placeholder="再次输入新密码"
            @keydown.enter="onSubmit"
          />
        </n-form-item>

        <div class="profile-password__actions">
          <n-button @click="$router.push('/profile')">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="onSubmit">保存</n-button>
        </div>
      </n-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { updatePassword, logoutSession } from '../services/auth'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const formRef = ref(null)
const submitting = ref(false)
const formValue = ref({ current: '', next: '', confirm: '' })

const rules = {
  current: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  next: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, value) =>
        value === formValue.value.next || new Error('两次密码不一致'),
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
        await updatePassword({
          oldPassword: formValue.value.current,
          newPassword: formValue.value.next
        })
        message.success('密码已更新，请重新登录')
        try {
          await logoutSession()
        } catch {
          // ignore
        }
        auth.clearAuth()
        router.push('/login')
      } catch (err) {
        message.error(err?.message || '修改失败')
      } finally {
        submitting.value = false
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.profile-password {
  max-width: 520px;
  margin: 0 auto;
}

.profile-password__header {
  margin-bottom: var(--sp-6);
}

.profile-password__back {
  display: inline-block;
  margin-bottom: var(--sp-3);
  color: var(--text-secondary);
  font-size: var(--fs-14);
}

.profile-password__back:hover {
  color: var(--accent);
}

.profile-password__header h1 {
  font-family: var(--font-serif);
  font-size: var(--fs-36);
  margin-bottom: var(--sp-2);
}

.profile-password__hint {
  font-size: var(--fs-14);
  color: var(--text-muted);
}

.profile-password__card {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
}

.profile-password__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-3);
  margin-top: var(--sp-4);
}
</style>
