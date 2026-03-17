<template>
  <div class="page">
    <section class="hero-card hero-card--editorial">
      <p class="eyebrow">Profile</p>
      <van-image
        class="profile-avatar"
        round
        fit="cover"
        width="88"
        height="88"
        :src="avatarUrl"
      />
      <h1 class="hero-title">{{ profile.nickname || profile.username || '个人中心' }}</h1>
      <p class="hero-subtitle">{{ profile.bio || '维护个人资料、密码，以及你的阅读资产。' }}</p>
      <div class="detail-meta">
        <span>用户名：{{ profile.username || '-' }}</span>
        <span>性别：{{ toGenderLabel(profile.gender) }}</span>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>账号设置</h2>
      </div>
      <van-cell-group inset>
        <van-cell title="编辑资料" is-link @click="router.push('/profile/edit')" />
        <van-cell title="修改密码" is-link @click="router.push('/profile/password')" />
        <van-cell title="我的收藏" is-link @click="router.push('/favorites')" />
        <van-cell title="浏览历史" is-link @click="router.push('/history')" />
      </van-cell-group>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>资料概览</h2>
      </div>
      <div class="profile-grid">
        <div class="profile-item">
          <span class="profile-label">头像地址</span>
          <span class="profile-value ellipsis">{{ avatarUrl }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">简介</span>
          <span class="profile-value">{{ profile.bio || '未填写' }}</span>
        </div>
      </div>
      <button class="hero-button hero-button--ghost" type="button" @click="handleLogout">退出登录</button>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import { fetchCurrentUser } from '../services/auth.js'
import { useAuthStore } from '../store/auth'
import { getAvatarUrl } from '../utils/media.js'
import { toGenderLabel } from '../utils/profile.js'

const router = useRouter()
const authStore = useAuthStore()
const profile = ref(authStore.userInfo || {})
const avatarUrl = computed(() => getAvatarUrl(profile.value.avatar))

const loadProfile = async () => {
  try {
    const payload = await fetchCurrentUser()
    profile.value = payload
    authStore.setUserInfo(payload)
  } catch (error) {
    showToast(error instanceof Error ? error.message : '用户信息加载失败')
  }
}

const handleLogout = () => {
  authStore.clearAuth()
  router.replace('/login')
}

onMounted(async () => {
  await loadProfile()
})
</script>
