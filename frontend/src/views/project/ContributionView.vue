<template>
  <div class="contribution-page" v-if="payload">
    <div class="header-row">
      <div>
        <h1 class="page-title">贡献审计</h1>
        <div class="page-desc">用任务、文档、代码、响应和稳定性构建多维证据链</div>
      </div>
      <el-button type="primary" @click="recalculate">重算贡献分</el-button>
    </div>
    <div class="teamflow-card ranking-panel">
      <el-table :data="payload.ranking">
        <el-table-column label="成员" min-width="180">
          <template #default="{ row }">{{ row.user.name }}</template>
        </el-table-column>
        <el-table-column label="总分" prop="total_score" />
        <el-table-column label="任务得分" prop="task_score" />
        <el-table-column label="文档得分" prop="document_score" />
        <el-table-column label="代码得分" prop="code_score" />
        <el-table-column label="响应得分" prop="response_score" />
        <el-table-column label="稳定性得分" prop="stability_score" />
      </el-table>
    </div>
    <div class="teamflow-card evidence-panel">
      <div class="section-title">近期证据列表</div>
      <div class="evidence-list">
        <div v-for="item in payload.evidence" :key="item.id" class="evidence-item">
          <strong>{{ item.summary }}</strong>
          <div class="tiny-muted">{{ item.user.name }} · {{ item.evidence_type }} · {{ item.created_at }}</div>
          <span class="status-tag blue">+{{ item.score }} 分</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { projectApi } from '@/api'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const payload = ref<any>(null)

const load = async () => {
  const { data } = await projectApi.contribution(projectId.value)
  payload.value = data
}

const recalculate = async () => {
  await projectApi.recalculateContribution(projectId.value)
  ElMessage.success('贡献分已刷新')
  await load()
}

onMounted(load)
</script>

<style scoped>
.contribution-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ranking-panel,
.evidence-panel {
  padding: 18px;
}

.evidence-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.evidence-item {
  padding: 16px;
  border: 1px solid #eef2ff;
  border-radius: 16px;
}
</style>
