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

const render = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    radar: {
      indicator: props.items.map((item) => ({ name: item.name, max: 100 })),
      splitArea: { areaStyle: { color: ['rgba(79,70,229,0.03)', 'rgba(79,70,229,0.06)'] } },
      splitLine: { lineStyle: { color: '#dfe7ff' } },
      axisName: { color: '#475569' },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: props.items.map((item) => item.value),
            areaStyle: { color: 'rgba(79, 70, 229, 0.16)' },
            lineStyle: { color: '#2563eb', width: 2 },
            itemStyle: { color: '#2563eb' },
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
