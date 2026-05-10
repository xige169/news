<template>
  <div class="admin-login">
    <div class="admin-login__card">
      <div class="admin-login__brand">
        <span class="admin-login__brand-mark">N</span>
        <div>
          <h1>新闻管理后台</h1>
          <p>NEWSROOM ADMIN</p>
        </div>
      </div>

      <el-form
        ref="formRef"
        label-position="top"
        :model="form"
        :rules="rules"
        size="large"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入管理员用户名" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            autocomplete="current-password"
            @keydown.enter="handleSubmit"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="admin-login__submit"
          :loading="submitting"
          @click="handleSubmit"
        >
          登录
        </el-button>
      </el-form>

      <p class="admin-login__hint">仅具备 admin 角色的账号可以进入</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElButton, ElForm, ElFormItem, ElInput, ElMessage } from 'element-plus'

import { fetchAdminProfile, loginAdmin } from '../services/auth.js'
import { useAuthStore } from '../store/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch {
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
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  padding: var(--sp-6);
}

.admin-login__card {
  width: 100%;
  max-width: 420px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
  box-shadow: var(--shadow-md);
}

.admin-login__brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  margin-bottom: var(--sp-8);
}

.admin-login__brand-mark {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--accent);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--fs-18);
  font-weight: 700;
}

.admin-login__brand h1 {
  font-size: var(--fs-18);
  font-weight: 600;
}

.admin-login__brand p {
  font-size: 11px;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  margin-top: 2px;
}

.admin-login__submit {
  width: 100%;
  margin-top: var(--sp-2);
}

.admin-login__hint {
  margin-top: var(--sp-5);
  text-align: center;
  font-size: var(--fs-12);
  color: var(--text-muted);
}
</style>
