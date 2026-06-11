<template>
  <div class="reminder-page" v-if="payload">
    <div class="header-row">
      <div>
        <h1 class="page-title">协作提醒中心</h1>
        <div class="page-desc">管理你的邀请、未读提醒和个人待办，高效跟进每一项协作</div>
      </div>
      <el-button @click="markAllRead">全部已读</el-button>
    </div>
    <section class="grid-4">
      <StatCard title="待处理邀请" :value="payload.stats.pending_invitations" footer="需要你确认加入项目" :icon="UserFilled" tint="rgba(245,158,11,.14)" icon-color="#f59e0b" />
      <StatCard title="未读提醒" :value="payload.stats.unread_notifications" footer="较上周 ↑ 4" :icon="Bell" tint="rgba(139,92,246,.12)" icon-color="#8b5cf6" />
      <StatCard title="我的待办" :value="payload.stats.my_todos" footer="进行中及待处理事项" :icon="DocumentChecked" tint="rgba(34,197,94,.12)" icon-color="#22c55e" />
      <StatCard title="即将到期任务" :value="payload.stats.upcoming_tasks" footer="3 天内截止" :icon="Clock" tint="rgba(59,130,246,.12)" icon-color="#3b82f6" />
    </section>

    <div class="reminder-grid">
      <div class="teamflow-card panel">
        <div class="section-title">项目邀请列表</div>
        <div v-for="item in payload.invitations" :key="item.id" class="invite-card">
          <div>
            <div>{{ item.project_name }}</div>
            <div class="tiny-muted">{{ item.inviter?.name }} 邀请你加入 · {{ item.created_at }}</div>
          </div>
          <div class="invite-actions">
            <el-button @click="reject(item.id)">拒绝</el-button>
            <el-button type="primary" @click="accept(item.id)">接受</el-button>
          </div>
        </div>
      </div>
      <div class="teamflow-card panel">
        <div class="section-title">我的待办任务</div>
        <div v-for="item in payload.todo_tasks" :key="item.id" class="todo-row">
          <div>
            <div>{{ item.title }}</div>
            <div class="tiny-muted">{{ item.assignee?.name }} · {{ item.due_date }}</div>
          </div>
          <span class="status-tag blue">{{ item.response_status }}</span>
        </div>
      </div>
      <div class="teamflow-card panel">
        <div class="section-title">最新提醒</div>
        <div v-for="item in payload.latest_notifications" :key="item.id" class="notice-row">
          <div>{{ item.title }}</div>
          <div class="tiny-muted">{{ item.content }}</div>
        </div>
      </div>
    </div>

    <div class="teamflow-card panel">
      <div class="section-title">今日协作动态</div>
      <div class="timeline-track">
        <div v-for="item in payload.today_timeline" :key="item.time" class="timeline-node">
          <div class="tiny-muted">{{ item.time }}</div>
          <div class="timeline-title">{{ item.title }}</div>
          <div class="tiny-muted">{{ item.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bell, Clock, DocumentChecked, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { notificationApi, projectApi } from '@/api'
import StatCard from '@/components/common/StatCard.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const payload = ref<any>(null)

const load = async () => {
  const { data } = await projectApi.workspace(projectId.value)
  payload.value = data
}

const accept = async (id: number) => {
  await projectApi.acceptInvitation(id)
  ElMessage.success('已接受邀请')
  await load()
}

const reject = async (id: number) => {
  await projectApi.rejectInvitation(id)
  ElMessage.warning('已拒绝邀请')
  await load()
}

const markAllRead = async () => {
  await notificationApi.readAll()
  ElMessage.success('提醒已全部标记已读')
  await load()
}

onMounted(load)
</script>

<style scoped>
.reminder-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row,
.invite-card,
.invite-actions,
.todo-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.reminder-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: 1fr 1fr 1fr;
}

.panel {
  padding: 18px;
}

.invite-card,
.todo-row,
.notice-row {
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}

.timeline-track {
  display: grid;
  gap: 18px;
  margin-top: 18px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.timeline-node {
  padding: 12px;
  border-radius: 16px;
  background: #f8fbff;
}

@media (max-width: 1200px) {
  .reminder-grid {
    grid-template-columns: 1fr 1fr;
  }

  .timeline-track {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .header-row,
  .invite-card,
  .invite-actions,
  .todo-row {
    align-items: flex-start;
    gap: 10px;
    flex-direction: column;
  }

  .reminder-grid,
  .timeline-track {
    grid-template-columns: 1fr;
  }
}
</style>
