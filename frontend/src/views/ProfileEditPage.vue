<template>
  <div class="page">
    <section class="hero-card compact">
      <p class="eyebrow">Edit Profile</p>
      <h1 class="hero-title">编辑资料</h1>
      <p class="hero-subtitle">维护昵称、头像、性别和简介，直接同步到后端。</p>
      <van-image
        class="profile-avatar"
        round
        fit="cover"
        width="88"
        height="88"
        :src="avatarPreview"
      />
    </section>

    <section class="section-card">
      <van-form @submit="handleSubmit">
        <van-field v-model="form.nickname" label="昵称" placeholder="请输入昵称" />
        <van-field v-model="form.avatar" label="头像地址" placeholder="请输入头像 URL" />
        <div class="field-block">
          <div class="field-label">性别</div>
          <div class="category-grid">
            <button
              v-for="item in GENDER_OPTIONS"
              :key="item.value"
              class="category-chip click-effect"
              :class="{ active: form.gender === item.value }"
              type="button"
              @click="form.gender = item.value"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
        <van-field v-model="form.phone" label="手机号" placeholder="请输入手机号" />
        <van-field
          v-model="form.bio"
          type="textarea"
          rows="4"
          autosize
          label="简介"
          placeholder="介绍一下自己"
        />
        <div class="form-actions">
          <van-button block type="primary" native-type="submit" :loading="submitting">保存资料</van-button>
        </div>
      </van-form>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { fetchCurrentUser, updateProfile } from '../services/auth.js'
import { useAuthStore } from '../store/auth'
import { getAvatarUrl } from '../utils/media.js'
import { GENDER_OPTIONS, normalizeGender } from '../utils/profile.js'

const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const form = reactive({
  nickname: '',
  avatar: '',
  gender: 'unknown',
  bio: '',
  phone: ''
})
const avatarPreview = computed(() => getAvatarUrl(form.avatar))

const loadProfile = async () => {
  try {
    const payload = await fetchCurrentUser()
    Object.assign(form, {
      nickname: payload.nickname || '',
      avatar: payload.avatar || '',
      gender: normalizeGender(payload.gender),
      bio: payload.bio || '',
      phone: payload.phone || ''
    })
  } catch (error) {
    showToast(error instanceof Error ? error.message : '资料加载失败')
  }
}

const handleSubmit = async () => {
  submitting.value = true

  try {
    const payload = await updateProfile({
      ...form,
      gender: normalizeGender(form.gender)
    })
    authStore.setUserInfo(payload)
    showToast('资料已更新')
    router.replace('/profile')
  } catch (error) {
    showToast(error instanceof Error ? error.message : '资料更新失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadProfile()
})
</script>
