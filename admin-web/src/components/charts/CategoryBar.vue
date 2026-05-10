<template>
  <BaseChart :option="option" :height="height" />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  valueKey: { type: String, default: 'newsCount' },
  labelKey: { type: String, default: 'name' },
  height: { type: Number, default: 240 }
})

const option = computed(() => {
  const sorted = [...props.items]
    .filter((item) => item)
    .sort((a, b) => (b[props.valueKey] || 0) - (a[props.valueKey] || 0))
    .slice(0, 8)

  const labels = sorted.map((item) => item[props.labelKey] || '未命名')
  const values = sorted.map((item) => item[props.valueKey] || 0)

  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 80, right: 12, top: 8, bottom: 8 },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#ececea' } },
      axisLabel: { color: '#9a9a9a', fontSize: 11 }
    },
    yAxis: {
      type: 'category',
      data: labels,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#1a1a1a', fontSize: 12 },
      inverse: true
    },
    series: [
      {
        type: 'bar',
        data: values,
        barWidth: 14,
        itemStyle: { color: '#b3261e', borderRadius: [0, 4, 4, 0] }
      }
    ]
  }
})
</script>
