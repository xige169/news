<template>
  <div class="profile-edit">
    <header class="profile-edit__header">
      <router-link to="/profile" class="profile-edit__back">← 返回个人中心</router-link>
      <h1>编辑资料</h1>
    </header>

    <div class="profile-edit__card">
      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="top"
        size="large"
      >
        <div class="profile-edit__avatar">
          <img :src="avatarPreview" :alt="formValue.username || 'avatar'" />
        </div>

        <n-form-item label="头像 URL" path="avatar">
          <n-input
            v-model:value="formValue.avatar"
            placeholder="粘贴头像图片地址"
            clearable
          />
        </n-form-item>

        <n-form-item label="昵称" path="nickname">
          <n-input v-model:value="formValue.nickname" placeholder="昵称" clearable />
        </n-form-item>

        <n-form-item label="性别" path="gender">
          <n-radio-group v-model:value="formValue.gender">
            <n-radio v-for="opt in genderOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </n-radio>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="formValue.email" placeholder="可选" clearable />
        </n-form-item>

        <n-form-item label="个性签名" path="signature">
          <n-input
            v-model:value="formValue.signature"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 6 }"
            placeholder="一句话介绍自己"
          />
        </n-form-item>

        <div class="profile-edit__actions">
          <n-button @click="$router.push('/profile')">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="onSubmit">保存</n-button>
        </div>
      </n-form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NRadio,
  NRadioGroup,
  useMessage
} from 'naive-ui'

import { useAuthStore } from '../store/auth'
import { fetchCurrentUser, updateProfile } from '../services/auth'
import { GENDER_OPTIONS, normalizeGender } from '../utils/profile'
import { getAvatarUrl } from '../utils/media'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const formRef = ref(null)
const submitting = ref(false)
const formValue = ref({
  avatar: '',
  nickname: '',
  gender: 'unknown',
  email: '',
  signature: '',
  username: ''
})

const genderOptions = GENDER_OPTIONS

const rules = {
  email: [
    {
      validator: (_, value) =>
        !value ||
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ||
        new Error('邮箱格式不正确'),
      trigger: 'blur'
    }
  ]
}

const avatarPreview = computed(() => getAvatarUrl(formValue.value.avatar))

const populate = (info) => {
  formValue.value.avatar = info?.avatar || ''
  formValue.value.nickname = info?.nickname || info?.username || ''
  formValue.value.gender = normalizeGender(info?.gender)
  formValue.value.email = info?.email || ''
  formValue.value.signature = info?.signature || info?.bio || ''
  formValue.value.username = info?.username || ''
}

const onSubmit = () => {
  formRef.value
    ?.validate(async (errors) => {
      if (errors) return
      submitting.value = true
      try {
        const payload = {
          nickname: formValue.value.nickname.trim(),
          gender: formValue.value.gender,
          email: formValue.value.email.trim(),
          signature: formValue.value.signature.trim(),
          avatar: formValue.value.avatar.trim()
        }
        await updateProfile(payload)
        try {
          const next = await fetchCurrentUser()
          auth.setUserInfo(next)
        } catch {
          auth.setUserInfo({ ...(auth.userInfo || {}), ...payload })
        }
        message.success('资料已更新')
        router.push('/profile')
      } catch (err) {
        message.error(err?.message || '保存失败')
      } finally {
        submitting.value = false
      }
    })
    .catch(() => {})
}

onMounted(async () => {
  populate(auth.userInfo)
  try {
    const data = await fetchCurrentUser()
    auth.setUserInfo(data)
    populate(data)
  } catch {
    // ignore
  }
})
</script>

<style scoped>
.profile-edit {
  max-width: 640px;
  margin: 0 auto;
}

.profile-edit__header {
  margin-bottom: var(--sp-6);
}

.profile-edit__back {
  display: inline-block;
  margin-bottom: var(--sp-3);
  color: var(--text-secondary);
  font-size: var(--fs-14);
}

.profile-edit__back:hover {
  color: var(--accent);
}

.profile-edit__header h1 {
  font-family: var(--font-serif);
  font-size: var(--fs-36);
}

.profile-edit__card {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
}

.profile-edit__avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto var(--sp-6);
  background: var(--bg-elevated);
}

.profile-edit__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-edit__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-3);
  margin-top: var(--sp-4);
}
</style>
