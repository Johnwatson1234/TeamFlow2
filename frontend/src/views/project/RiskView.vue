<template>
  <div class="risk-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">风险雷达</h1>
        <div class="page-desc">统一查看延期、阻塞、评审积压与代码冲突等高优先级风险</div>
      </div>
      <el-button type="primary" @click="scan">重新扫描风险</el-button>
    </div>
    <div class="risk-dashboard">
      <div class="grid-3">
        <div v-for="(risk, index) in risks.slice(0, 3)" :key="risk.id" :class="['risk-summary-card', risk.level === '高' ? 'high' : risk.level === '中' ? 'medium' : 'low']">
          <div class="risk-card-head">
            <span class="risk-badge">Top {{ index + 1 }}</span>
            <span class="risk-level-tag">{{ risk.level }}风险</span>
          </div>
          <div class="risk-card-title">{{ risk.title }}</div>
          <div class="risk-card-score">风险值 <strong>{{ risk.score }}</strong></div>
        </div>
      </div>

      <div class="teamflow-card risk-distribution">
        <div class="section-title">风险分布情况</div>
        <div class="distribution-bar">
          <div class="dist-segment red" :style="{ width: highRiskRatio + '%' }"></div>
          <div class="dist-segment orange" :style="{ width: medRiskRatio + '%' }"></div>
          <div class="dist-segment green" :style="{ width: lowRiskRatio + '%' }"></div>
        </div>
        <div class="dist-legend">
          <span><i class="dot red"></i> 高风险 {{ highRiskCount }}</span>
          <span><i class="dot orange"></i> 中风险 {{ medRiskCount }}</span>
          <span><i class="dot green"></i> 低风险 {{ lowRiskCount }}</span>
        </div>
      </div>
    </div>

    <div class="teamflow-card risk-table">
      <el-table :data="risks">
        <el-table-column label="风险标题" prop="title" min-width="220" />
        <el-table-column label="风险类型" width="140">
          <template #default="{ row }">
            <span class="status-tag blue">{{ row.risk_type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', row.level === '高' ? 'red' : row.level === '中' ? 'orange' : 'green']">{{ row.level }}</span>
          </template>
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

const highRiskCount = computed(() => risks.value.filter(r => r.level === '高').length)
const medRiskCount = computed(() => risks.value.filter(r => r.level === '中').length)
const lowRiskCount = computed(() => risks.value.filter(r => r.level === '低').length)
const totalRisks = computed(() => Math.max(1, risks.value.length))
const highRiskRatio = computed(() => (highRiskCount.value / totalRisks.value) * 100)
const medRiskRatio = computed(() => (medRiskCount.value / totalRisks.value) * 100)
const lowRiskRatio = computed(() => (lowRiskCount.value / totalRisks.value) * 100)

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

.risk-dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.risk-summary-card {
  padding: 20px;
  border-radius: 16px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-summary-card.high {
  background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
}

.risk-summary-card.medium {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
}

.risk-summary-card.low {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}

.risk-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.risk-badge {
  background: rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.risk-level-tag {
  font-size: 13px;
  font-weight: 600;
}

.risk-card-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.4;
  margin-top: 4px;
}

.risk-card-score {
  margin-top: auto;
  font-size: 14px;
  opacity: 0.9;
}

.risk-card-score strong {
  font-size: 24px;
}

.risk-distribution {
  padding: 20px;
}

.distribution-bar {
  display: flex;
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  margin: 16px 0;
  background: var(--bg-dark);
}

.dist-segment {
  height: 100%;
  transition: width 0.5s ease-out;
}

.dist-segment.red { background: var(--danger); }
.dist-segment.orange { background: var(--warning); }
.dist-segment.green { background: var(--success); }

.dist-legend {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-muted);
}

.dist-legend .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}

.dist-legend .dot.red { background: var(--danger); }
.dist-legend .dot.orange { background: var(--warning); }
.dist-legend .dot.green { background: var(--success); }

.risk-table {
  padding: 18px;
}

@media (max-width: 768px) {
  .header-row {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }
}
</style>
