<template>
  <div class="teamflow-card stat-card">
    <div class="stat-icon" :style="{ background: tint }">
      <el-icon :size="22" :color="iconColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-body">
      <div class="stat-title">{{ title }}</div>
      <div class="metric-value">{{ value }}</div>
      <div class="stat-foot">
        <span>{{ footer }}</span>
        <span v-if="trend" :class="['trend', trend.type]">{{ trend.text }}</span>
      </div>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  footer?: string
  icon: any
  tint?: string
  iconColor?: string
  trend?: {
    text: string
    type: 'up' | 'down' | 'flat'
  }
}>()
</script>

<style scoped>
.stat-card {
  position: relative;
  display: flex;
  gap: 16px;
  align-items: center;
  min-height: 118px;
  padding: 22px 24px;
}

.stat-icon {
  display: grid;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  place-items: center;
}

.stat-title {
  color: var(--text-muted);
  font-size: 14px;
}

.stat-foot {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  color: var(--text-light);
  font-size: 12px;
}

.trend.up {
  color: var(--danger);
}

.trend.down {
  color: var(--success);
}

.trend.flat {
  color: var(--text-muted);
}
</style>
