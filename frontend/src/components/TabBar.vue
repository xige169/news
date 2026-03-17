<template>
  <van-tabbar v-model="active" route>
    <van-tabbar-item to="/" icon="home-o">首页</van-tabbar-item>
    <van-tabbar-item to="/favorites" icon="star-o">收藏</van-tabbar-item>
    <van-tabbar-item to="/history" icon="clock-o">历史</van-tabbar-item>
    <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

// 根据当前路由路径设置激活的标签
const setActiveTab = () => {
  const path = route.path
  if (path === '/') {
    active.value = 0
  } else if (path.startsWith('/favorites')) {
    active.value = 1
  } else if (path.startsWith('/history')) {
    active.value = 2
  } else if (path.startsWith('/profile')) {
    active.value = 3
  }
}

// 初始化时设置激活标签
setActiveTab()

watch(
  () => route.path,
  () => {
    setActiveTab()
  }
)
</script>

<style scoped>
.van-tabbar {
  max-width: 750px;
  left: 50%;
  transform: translateX(-50%);
  border-top: 1px solid rgba(25, 137, 250, 0.08);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
}
</style>
