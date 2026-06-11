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

const cssVar = (name: string, fallback: string) => {
  if (typeof window === 'undefined') return fallback
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

const render = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  const axis = cssVar('--chart-axis', '#6b7c93')
  const axisLight = cssVar('--chart-axis-light', '#93a4b8')
  const grid = cssVar('--chart-grid', '#dbe7f3')
  const lineStart = cssVar('--chart-line-1', '#0f9d8a')
  const lineEnd = cssVar('--chart-line-2', '#2563eb')
  const fillStart = cssVar('--chart-fill-1', 'rgba(15, 157, 138, 0.24)')
  const fillEnd = cssVar('--chart-fill-2', 'rgba(37, 99, 235, 0.04)')
  chart.setOption({
    grid: { left: 22, right: 18, top: 34, bottom: 20 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      axisPointer: {
        type: 'line',
        lineStyle: { color: 'rgba(37, 99, 235, 0.26)', width: 1.5 },
      },
    },
    xAxis: {
      type: 'category',
      data: props.series.map((item) => item.date),
      boundaryGap: false,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: grid } },
      axisLabel: { color: axis, margin: 12 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: grid, type: 'dashed' } },
      axisLabel: { color: axisLight },
    },
    series: [
      {
        data: props.series.map((item) => item.value),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 9,
        showSymbol: false,
        emphasis: { focus: 'series', scale: true },
        itemStyle: {
          color: lineEnd,
          borderColor: '#ffffff',
          borderWidth: 2,
        },
        lineStyle: {
          width: 4,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: lineStart },
            { offset: 1, color: lineEnd },
          ]),
          shadowBlur: 12,
          shadowColor: 'rgba(37, 99, 235, 0.18)',
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: fillStart },
            { offset: 1, color: fillEnd },
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
