<template>
  <div ref="chartRef" class="chart-shell"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  series: { date: string; value: number }[]
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const render = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 24, right: 20, top: 36, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: props.series.map((item) => item.date),
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d9e0f0' } },
      axisLabel: { color: '#64748b' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef2ff' } },
      axisLabel: { color: '#94a3b8' },
    },
    series: [
      {
        data: props.series.map((item) => item.value),
        type: 'line',
        smooth: true,
        symbolSize: 8,
        itemStyle: { color: '#2563eb' },
        lineStyle: { width: 3, color: '#2563eb' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.16)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.02)' },
          ]),
        },
      },
    ],
  })
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

watch(() => props.series, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  chart?.dispose()
})
</script>
