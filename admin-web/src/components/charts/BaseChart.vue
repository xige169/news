<template>
  <div ref="chartEl" class="base-chart" :style="{ height: `${height}px` }" />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: Number, default: 240 }
})

const chartEl = ref(null)
const chart = shallowRef(null)

const renderChart = () => {
  if (!chart.value) return
  chart.value.setOption(props.option, true)
}

const handleResize = () => {
  chart.value?.resize()
}

onMounted(() => {
  if (!chartEl.value) return
  chart.value = echarts.init(chartEl.value)
  renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart.value?.dispose()
  chart.value = null
})

watch(
  () => props.option,
  () => renderChart(),
  { deep: true }
)
</script>

<style scoped>
.base-chart {
  width: 100%;
  min-height: 200px;
}
</style>
