<template>
  <div class="viewport-shell" :style="shellStyle">
    <div class="viewport-frame" :style="frameStyle">
      <div class="viewport-stage" :style="stageStyle">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    baseWidth?: number
    baseHeight?: number
    padding?: number
    background?: string
  }>(),
  {
    baseWidth: 1536,
    baseHeight: 1024,
    padding: 12,
    background: 'transparent',
  },
)

const viewportWidth = ref(typeof window === 'undefined' ? props.baseWidth : window.innerWidth)
const viewportHeight = ref(typeof window === 'undefined' ? props.baseHeight : window.innerHeight)

const updateSize = () => {
  viewportWidth.value = window.innerWidth
  viewportHeight.value = window.innerHeight
}

const scale = computed(() => {
  const availableWidth = Math.max(viewportWidth.value - props.padding * 2, 320)
  const availableHeight = Math.max(viewportHeight.value - props.padding * 2, 320)
  return Math.min(1, availableWidth / props.baseWidth, availableHeight / props.baseHeight)
})

const shellStyle = computed(() => ({
  padding: `${props.padding}px`,
  background: props.background,
}))

const frameStyle = computed(() => ({
  width: `${props.baseWidth * scale.value}px`,
  height: `${props.baseHeight * scale.value}px`,
}))

const stageStyle = computed(() => ({
  width: `${props.baseWidth}px`,
  height: `${props.baseHeight}px`,
  transform: `scale(${scale.value})`,
  transformOrigin: 'top left',
  '--app-width': `${props.baseWidth}px`,
  '--app-height': `${props.baseHeight}px`,
  '--app-scale': String(scale.value),
} as Record<string, string>))

onMounted(() => {
  updateSize()
  window.addEventListener('resize', updateSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateSize)
})
</script>

<style scoped>
.viewport-shell {
  display: grid;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  place-items: center;
}

.viewport-frame {
  position: relative;
  overflow: hidden;
}

.viewport-stage {
  overflow: hidden;
}
</style>
