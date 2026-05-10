<template>
  <BaseChart :option="option" :height="240" />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ published: 0, draft: 0, offline: 0 }) }
})

const palette = {
  published: '#2e7d32',
  draft: '#b45309',
  offline: '#9a9a9a'
}

const labels = {
  published: '已发布',
  draft: '草稿',
  offline: '已下线'
}

const option = computed(() => {
  const entries = ['published', 'draft', 'offline']
  const series = entries
    .map((key) => ({
      name: labels[key],
      value: props.data?.[key] || 0,
      itemStyle: { color: palette[key] }
    }))
    .filter((item) => item.value > 0)

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      textStyle: { fontSize: 12, color: '#6b6b6b' }
    },
    series: [
      {
        name: '稿件状态',
        type: 'pie',
        radius: ['52%', '76%'],
        avoidLabelOverlap: false,
        label: { show: false },
        labelLine: { show: false },
        data: series.length
          ? series
          : [{ name: '暂无数据', value: 1, itemStyle: { color: '#ececea' } }]
      }
    ]
  }
})
</script>
