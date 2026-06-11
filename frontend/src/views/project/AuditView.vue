<template>
  <div class="teamflow-card audit-page" v-if="dashboard">
    <div class="header-row">
      <div>
        <h1 class="page-title">过程审计</h1>
        <div class="page-desc">查看任务、文档、代码与消息行为留下的审计链路</div>
      </div>
    </div>
    <div class="audit-list">
      <div v-for="item in dashboard.recent_task_activities" :key="item.id" class="audit-item">
        <img :src="item.actor?.avatar" alt="avatar" />
        <div>
          <div class="timeline-title">{{ item.content }}</div>
          <div class="tiny-muted">{{ item.actor?.name }} · {{ item.created_at }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { projectApi } from '@/api'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const dashboard = ref<any>(null)

const load = async () => {
  const { data } = await projectApi.dashboard(projectId.value)
  dashboard.value = data
}

onMounted(load)
</script>

<style scoped>
.audit-page {
  padding: 20px;
}

.audit-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.audit-item,
.header-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.audit-item img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

@media (max-width: 768px) {
  .header-row,
  .audit-item {
    align-items: flex-start;
  }
}
</style>
