<template>
  <div class="audit-page" v-if="dashboard">
    <div class="header-row">
      <div>
        <h1 class="page-title">过程审计</h1>
        <div class="page-desc">查看任务、文档、代码与消息行为留下的审计链路</div>
      </div>
    </div>

    <div class="audit-dashboard">
      <div class="teamflow-card audit-stat dark" style="background: linear-gradient(135deg, #F472B6 0%, #DB2777 100%)">
        <div class="stat-label">总事件记录</div>
        <div class="stat-val">{{ dashboard.recent_task_activities?.length || 0 }}</div>
      </div>
      <div class="teamflow-card audit-stat dark" style="background: linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)">
        <div class="stat-label">活跃成员</div>
        <div class="stat-val">3</div>
      </div>
      <div class="teamflow-card audit-stat dark" style="background: linear-gradient(135deg, #22D3EE 0%, #0891B2 100%)">
        <div class="stat-label">任务更新</div>
        <div class="stat-val">{{ dashboard.recent_task_activities?.filter((a: any) => a.content.includes('任务')).length || 0 }}</div>
      </div>
      <div class="teamflow-card audit-stat dark" style="background: linear-gradient(135deg, #818CF8 0%, #4F46E5 100%)">
        <div class="stat-label">文档记录</div>
        <div class="stat-val">{{ dashboard.recent_task_activities?.filter((a: any) => a.content.includes('文档')).length || 0 }}</div>
      </div>
    </div>

    <div class="teamflow-card audit-timeline-panel">
      <div class="section-title" style="margin-bottom: 20px;">详细审计日志</div>
      <div class="audit-list">
        <div v-for="(item, index) in dashboard.recent_task_activities" :key="item.id" class="audit-item">
          <div class="timeline-track">
            <div class="timeline-dot"></div>
            <div class="timeline-line" v-if="index !== dashboard.recent_task_activities.length - 1"></div>
          </div>
          <img class="actor-avatar" :src="item.actor?.avatar || 'https://api.dicebear.com/7.x/notionists/svg?seed=Audit'" alt="avatar" />
          <div class="audit-content">
            <div class="audit-header">
              <span class="actor-name">{{ item.actor?.name || '系统用户' }}</span>
              <span class="audit-action">{{ item.content }}</span>
              <span class="status-tag" :class="item.content.includes('任务') ? 'blue' : (item.content.includes('文档') ? 'purple' : 'green')">
                {{ item.content.includes('任务') ? '任务更新' : (item.content.includes('文档') ? '文档操作' : '系统操作') }}
              </span>
            </div>
            <div class="tiny-muted">{{ item.created_at || '刚刚' }}</div>
          </div>
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
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.audit-dashboard {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, 1fr);
}

.audit-stat {
  padding: 24px 32px;
}

.audit-stat.dark {
  color: #fff;
  border: none;
}
.audit-stat.dark .stat-label {
  color: rgba(255, 255, 255, 0.9);
}
.audit-stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  color: var(--text-muted);
  font-size: 14px;
}

.stat-val {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
}

.audit-timeline-panel {
  padding: 24px;
}

.audit-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.audit-item {
  display: flex;
  gap: 16px;
  min-height: 60px;
}

.timeline-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  border: 2px solid #EEF2FF;
  z-index: 2;
  margin-top: 6px;
}

.timeline-line {
  flex: 1;
  width: 2px;
  background: var(--border-light);
  margin: 4px 0;
}

.actor-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-top: -4px;
}

.audit-content {
  flex: 1;
  padding-bottom: 24px;
}

.audit-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 15px;
}

.actor-name {
  font-weight: 600;
  color: var(--text);
}

.audit-action {
  color: var(--text);
}

@media (max-width: 768px) {
  .audit-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
  .header-row {
    align-items: flex-start;
  }
}
</style>
