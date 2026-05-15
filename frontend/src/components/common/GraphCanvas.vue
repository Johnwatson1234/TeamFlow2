<template>
  <div ref="chartRef" class="graph-canvas"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  nodes: { id: string; label: string; type: string }[]
  edges: { source: string; target: string; label?: string }[]
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const colorMap: Record<string, string> = {
  member: '#1d4ed8',
  task: '#22c55e',
  document: '#3b82f6',
  message: '#8b5cf6',
  commit: '#f97316',
  review: '#14b8a6',
}

const render = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: {},
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 8,
        force: {
          repulsion: 300,
          edgeLength: 110,
        },
        label: {
          show: true,
          color: '#334155',
          fontSize: 13,
        },
        lineStyle: {
          color: '#c7d2fe',
          width: 2,
          curveness: 0.18,
        },
        data: props.nodes.map((item) => ({
          id: item.id,
          name: item.label,
          value: item.type,
          symbolSize: item.type === 'member' ? 56 : 44,
          itemStyle: { color: colorMap[item.type] || '#4f46e5' },
        })),
        links: props.edges.map((item) => ({
          source: item.source,
          target: item.target,
          label: { show: Boolean(item.label), formatter: item.label },
        })),
      },
    ],
  })
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

watch(() => [props.nodes, props.edges], render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  chart?.dispose()
})
</script>

<style scoped>
.graph-canvas {
  width: 100%;
  height: 640px;
}
</style>
