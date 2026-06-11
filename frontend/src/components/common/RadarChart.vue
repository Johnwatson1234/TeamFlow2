<template>
  <div ref="chartRef" class="chart-shell"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  items: { name: string; value: number }[]
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
  const radarLine = cssVar('--chart-radar-line', '#0f766e')
  const radarFill = cssVar('--chart-radar-fill', 'rgba(20, 184, 166, 0.16)')
  const grid = cssVar('--chart-grid', '#dbe7f3')
  const axis = cssVar('--chart-axis', '#6b7c93')
  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
    },
    radar: {
      indicator: props.items.map((item) => ({ name: item.name, max: 100 })),
      radius: '64%',
      splitNumber: 5,
      splitArea: {
        areaStyle: {
          color: [
            'rgba(255,255,255,0.72)',
            'rgba(235, 247, 246, 0.9)',
            'rgba(224, 241, 243, 0.92)',
            'rgba(217, 236, 240, 0.94)',
            'rgba(211, 230, 236, 0.96)',
          ],
        },
      },
      splitLine: { lineStyle: { color: grid } },
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.4)' } },
      axisName: { color: axis, fontSize: 13 },
    },
    series: [
      {
        type: 'radar',
        symbol: 'circle',
        symbolSize: 7,
        data: [
          {
            value: props.items.map((item) => item.value),
            areaStyle: { color: radarFill },
            lineStyle: { color: radarLine, width: 3 },
            itemStyle: {
              color: radarLine,
              borderColor: '#ffffff',
              borderWidth: 2,
            },
          },
        ],
      },
    ],
  })
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

watch(() => props.items, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  chart?.dispose()
})
</script>
