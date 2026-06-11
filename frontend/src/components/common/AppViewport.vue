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

const shellStyle = computed(() => ({
  background: props.background,
}))

const frameStyle = computed(() => ({
  width: '100%',
  minHeight: '100dvh',
}))

const stageStyle = computed(() => ({
  width: '100%',
  minHeight: '100dvh',
  '--app-width': `${viewportWidth.value}px`,
  '--app-height': `${viewportHeight.value}px`,
  '--app-scale': '1',
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
  width: 100%;
  min-height: 100dvh;
}

.viewport-frame {
  position: relative;
  width: 100%;
  min-height: 100dvh;
}

.viewport-stage {
  width: 100%;
  min-height: 100dvh;
}
</style>
