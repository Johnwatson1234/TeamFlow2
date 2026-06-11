<template>
  <div class="teamflow-card milestone-page">
    <div class="panel-header">
      <div>
        <h1 class="page-title">里程碑管理</h1>
        <div class="page-desc">把项目阶段、任务推进和交付节点放在一条时间轴上管理</div>
      </div>
      <el-button type="primary" @click="dialogVisible = true">新建里程碑</el-button>
    </div>
    <div class="timeline-grid">
      <div v-for="item in milestones" :key="item.id" class="timeline-card">
        <div class="milestone-badge">{{ item.order_index + 1 }}</div>
        <div class="timeline-title">{{ item.name }}</div>
        <div class="status-tag blue">{{ item.status }}</div>
        <div class="tiny-muted">{{ item.due_date }}</div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="新增里程碑" width="min(520px, 92vw)">
      <el-form :model="form" label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="截止日期"><el-input v-model="form.due_date" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createMilestone">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { taskApi } from '@/api'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const milestones = ref<any[]>([])
const dialogVisible = ref(false)
const form = reactive({ name: '', due_date: '' })

const load = async () => {
  const { data } = await taskApi.milestones(projectId.value)
  milestones.value = data
}

const createMilestone = async () => {
  await taskApi.createMilestone(projectId.value, { ...form, status: '待开始' })
  ElMessage.success('里程碑已创建')
  dialogVisible.value = false
  form.name = ''
  form.due_date = ''
  await load()
}

onMounted(load)
</script>

<style scoped>
.milestone-page {
  padding: 22px;
}

.timeline-grid {
  display: grid;
  gap: 16px;
  margin-top: 24px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.timeline-card {
  padding: 18px;
  border: 1px solid #edf1ff;
  border-radius: 18px;
}

.milestone-badge {
  display: grid;
  width: 34px;
  height: 34px;
  margin-bottom: 16px;
  border-radius: 50%;
  place-items: center;
  background: rgba(79, 70, 229, 0.12);
  color: var(--primary);
  font-weight: 700;
}

.timeline-title {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 700;
}

@media (max-width: 1200px) {
  .timeline-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .panel-header {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .timeline-grid {
    grid-template-columns: 1fr;
  }
}
</style>
