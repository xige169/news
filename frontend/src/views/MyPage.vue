<template>
  <div class="page page-my">
    <section class="hero-card compact">
      <p class="eyebrow">Profile</p>
      <h1 class="hero-title">{{ $t('my.title') }}</h1>
      <p class="hero-subtitle">{{ $t('my.subtitle') }}</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>{{ $t('my.theme') }}</h2>
      </div>
      <div class="theme-grid">
        <button
          v-for="item in themeOptions"
          :key="item.id"
          class="theme-item click-effect"
          :class="{ active: item.id === themeStore.getCurrentTheme }"
          type="button"
          @click="themeStore.setTheme(item.id)"
        >
          <span class="theme-swatch" :style="{ background: item.primaryColor }"></span>
          <span>{{ item.name }}</span>
        </button>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>{{ $t('my.language') }}</h2>
      </div>
      <van-cell-group inset>
        <van-cell
          title="简体中文"
          clickable
          :value="currentLocale === 'zh-CN' ? '当前' : ''"
          @click="changeLanguage('zh-CN')"
        />
        <van-cell
          title="English"
          clickable
          :value="currentLocale === 'en-US' ? 'Current' : ''"
          @click="changeLanguage('en-US')"
        />
      </van-cell-group>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>{{ $t('my.reading') }}</h2>
      </div>
      <p class="preference-copy">{{ $t('my.readingDesc') }}</p>
    </section>

    <TabBar />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'

import TabBar from '../components/TabBar.vue'
import { useThemeStore } from '../store/theme'
import { setI18nLanguage } from '../i18n'

const themeStore = useThemeStore()
const composer = useI18n()

const themeOptions = computed(() => themeStore.getAllThemes)
const currentLocale = computed(() => composer.locale.value)

const changeLanguage = (targetLocale) => {
  localStorage.setItem('language', targetLocale)
  setI18nLanguage(composer, targetLocale)
  showToast(targetLocale === 'zh-CN' ? '已切换为中文' : 'Switched to English')
}
</script>
