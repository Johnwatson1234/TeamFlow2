<template>
  <div class="risk-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">风险雷达</h1>
        <div class="page-desc">统一查看延期、阻塞、评审积压与代码冲突等高优先级风险</div>
      </div>
      <el-button type="primary" @click="scan">重新扫描风险</el-button>
    </div>
    <div class="grid-3">
      <div v-for="risk in risks.slice(0, 3)" :key="risk.id" class="teamflow-card risk-summary">
        <div class="section-title">{{ risk.title }}</div>
        <div class="metric-value">{{ risk.score }}</div>
        <div :class="['status-tag', risk.level === '高' ? 'red' : risk.level === '中' ? 'orange' : 'green']">{{ risk.level }}风险</div>
      </div>
    </div>
    <div class="teamflow-card risk-table">
      <el-table :data="risks">
        <el-table-column label="风险标题" prop="title" min-width="220" />
        <el-table-column label="风险类型" prop="risk_type" width="120" />
        <el-table-column label="等级" width="100">
          <template #default="{ row }">{{ row.level }}</template>
        </el-table-column>
        <el-table-column label="风险分数" prop="score" width="100" />
        <el-table-column label="风险原因" prop="reason" min-width="240" />
        <el-table-column label="风险建议" prop="suggestion" min-width="260" />
      </el-table>
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
const risks = ref<any[]>([])

const load = async () => {
  const { data } = await projectApi.riskAlerts(projectId.value)
  risks.value = data
}

const scan = async () => {
  await projectApi.scanRisk(projectId.value)
  ElMessage.success('风险扫描已完成')
  await load()
}

onMounted(load)
</script>

<style scoped>
.risk-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.risk-summary,
.risk-table {
  padding: 18px;
}
</style>
