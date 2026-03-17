<template>
  <div class="page page-chat">
    <section class="hero-card compact">
      <p class="eyebrow">AI</p>
      <h1 class="hero-title">{{ $t('aichat.title') }}</h1>
      <p class="hero-subtitle">{{ $t('aichat.subtitle') }}</p>
    </section>

    <section class="section-card">
      <van-field
        v-model="question"
        rows="5"
        autosize
        type="textarea"
        maxlength="200"
        show-word-limit
        :placeholder="$t('aichat.placeholder')"
      />

      <van-button block type="primary" class="action-button" @click="generateAnswer">
        {{ $t('aichat.action') }}
      </van-button>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>{{ $t('aichat.tipsTitle') }}</h2>
      </div>
      <div class="prompt-list">
        <button
          v-for="tip in promptTips"
          :key="tip"
          class="prompt-chip click-effect"
          type="button"
          @click="question = tip"
        >
          {{ tip }}
        </button>
      </div>
    </section>

    <section class="section-card answer-card">
      <div class="section-header">
        <h2>AI 回答</h2>
      </div>
      <p class="answer-text">{{ answer }}</p>
    </section>

    <TabBar />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'

import TabBar from '../components/TabBar.vue'

const { t, tm } = useI18n()
const question = ref('')
const answer = ref('AI 回答会显示在这里，适合放摘要、背景信息或阅读建议。')

const promptTips = tm('aichat.tips')

const generateAnswer = () => {
  if (!question.value.trim()) {
    showToast('请先输入问题')
    return
  }

  answer.value = `围绕“${question.value}”，当前界面建议优先输出三部分：一句摘要、两条背景信息、一个延伸阅读方向。这样更符合新闻阅读助手的使用场景。`
}
</script>
