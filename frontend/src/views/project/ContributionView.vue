<template>
  <div class="contribution-page" v-if="payload">
    <div class="header-row">
      <div>
        <h1 class="page-title">AI 贡献画像</h1>
        <div class="page-desc">{{ payload.summary?.description }}</div>
      </div>
      <div class="header-actions">
        <el-button @click="goCareer">岗位推荐页</el-button>
        <el-button type="primary" @click="recalculate">AI 重算画像</el-button>
      </div>
    </div>

    <div class="summary-grid">
      <div class="teamflow-card summary-card">
        <div class="tiny-muted">分析方式</div>
        <div class="metric-value">{{ analysisModeLabel }}</div>
        <div class="tiny-muted">生成时间：{{ payload.summary?.generated_at }}</div>
      </div>
      <div class="teamflow-card summary-card">
        <div class="tiny-muted">讨论消息</div>
        <div class="metric-value">{{ payload.summary?.message_count || 0 }}</div>
        <div class="tiny-muted">当前项目群与任务讨论累计消息</div>
      </div>
      <div class="teamflow-card summary-card">
        <div class="tiny-muted">有效想法</div>
        <div class="metric-value">{{ payload.summary?.idea_message_count || 0 }}</div>
        <div class="tiny-muted">识别为建议、方案、风险提示的讨论发言</div>
      </div>
      <div class="teamflow-card summary-card">
        <div class="tiny-muted">完成任务</div>
        <div class="metric-value">{{ payload.summary?.completed_task_count || 0 }}</div>
        <div class="tiny-muted">系统内有闭环记录的任务完成数</div>
      </div>
    </div>

    <div class="teamflow-card ranking-panel">
      <div class="panel-head">
        <div>
          <div class="section-title">成员贡献排名</div>
          <div class="section-subtitle">综合任务落地、讨论贡献、技术输出与协作稳定性生成</div>
        </div>
      </div>
      <el-table :data="payload.ranking">
        <el-table-column label="成员" min-width="200">
          <template #default="{ row }">
            <div class="member-cell">
              <img :src="row.user.avatar" alt="avatar" />
              <div>
                <div>{{ row.user.name }}</div>
                <div class="tiny-muted">{{ row.profile_label }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="总分" prop="total_score" width="90" />
        <el-table-column label="任务落地" prop="task_score" width="100" />
        <el-table-column label="讨论贡献" prop="response_score" width="100" />
        <el-table-column label="技术输出" prop="code_score" width="100" />
        <el-table-column label="文档沉淀" prop="document_score" width="100" />
        <el-table-column label="稳定性" prop="stability_score" width="90" />
        <el-table-column label="消息数" prop="message_count" width="90" />
        <el-table-column label="想法数" prop="idea_count" width="90" />
      </el-table>
    </div>

    <div class="insight-grid" v-if="payload.member_profiles?.length">
      <div class="teamflow-card profile-list">
        <div class="section-title">成员画像列表</div>
        <div class="section-subtitle">点击成员查看个性化协作风格与就业方向建议</div>
        <div class="profile-cards app-scroll">
          <button
            v-for="item in payload.member_profiles"
            :key="item.user.id"
            :class="['profile-card', { active: item.user.id === selectedProfile?.user.id }]"
            type="button"
            @click="selectedProfileId = item.user.id"
          >
            <div class="profile-top">
              <img :src="item.user.avatar" alt="avatar" />
              <div>
                <strong>{{ item.user.name }}</strong>
                <div class="tiny-muted">{{ item.profile_label }}</div>
              </div>
            </div>
            <div class="tiny-muted profile-copy">{{ item.contribution_summary }}</div>
            <div class="profile-bottom">
              <span class="status-tag blue">总分 {{ item.total_score }}</span>
              <span class="status-tag purple">{{ item.recommended_roles?.[0] }}</span>
            </div>
          </button>
        </div>
      </div>

      <div class="teamflow-card profile-detail" v-if="selectedProfile">
        <div class="detail-header">
          <div>
            <div class="tiny-muted">个性化展示</div>
            <div class="thread-title">{{ selectedProfile.user.name }}</div>
            <div class="page-desc">{{ selectedProfile.personality_summary }}</div>
          </div>
          <span class="status-tag purple">{{ selectedProfile.profile_label }}</span>
        </div>

        <div class="detail-grid">
          <div class="detail-card">
            <div class="section-title">协作风格</div>
            <p class="detail-copy">{{ selectedProfile.communication_style }}</p>
            <div class="section-title small-gap">项目内贡献总结</div>
            <p class="detail-copy">{{ selectedProfile.contribution_summary }}</p>
          </div>

          <div class="detail-card chart-card">
            <RadarChart :items="selectedProfile.radar" />
          </div>
        </div>

        <div class="chip-block">
          <div class="section-title">个人特征</div>
          <div class="chip-row">
            <span v-for="item in selectedProfile.traits" :key="item" class="status-tag blue">{{ item }}</span>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-card">
            <div class="section-title">优势判断</div>
            <div class="bullet-list">
              <div v-for="item in selectedProfile.strengths" :key="item" class="bullet-item">{{ item }}</div>
            </div>
          </div>
          <div class="detail-card">
            <div class="section-title">待提升点</div>
            <div class="bullet-list">
              <div v-for="item in selectedProfile.risks" :key="item" class="bullet-item">{{ item }}</div>
            </div>
          </div>
        </div>

        <div class="detail-card">
          <div class="section-title">适合的岗位方向</div>
          <div class="chip-row">
            <span v-for="item in selectedProfile.recommended_roles" :key="item" class="status-tag green">{{ item }}</span>
          </div>
          <p class="detail-copy career-copy">{{ selectedProfile.career_recommendation }}</p>
        </div>

        <div class="metrics-grid">
          <div class="metric-box">
            <label>消息</label>
            <span>{{ selectedProfile.metrics.message_count }}</span>
          </div>
          <div class="metric-box">
            <label>想法</label>
            <span>{{ selectedProfile.metrics.idea_count }}</span>
          </div>
          <div class="metric-box">
            <label>完成任务</label>
            <span>{{ selectedProfile.metrics.completed_tasks }}</span>
          </div>
          <div class="metric-box">
            <label>文档</label>
            <span>{{ selectedProfile.metrics.document_count }}</span>
          </div>
          <div class="metric-box">
            <label>代码消息</label>
            <span>{{ selectedProfile.metrics.code_message_count }}</span>
          </div>
          <div class="metric-box">
            <label>任务进度</label>
            <span>{{ selectedProfile.metrics.avg_task_progress }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="teamflow-card evidence-panel">
      <div class="section-title">关键证据链</div>
      <div class="section-subtitle">每条证据都来自消息、任务、文档或技术产出记录</div>
      <div class="evidence-list">
        <div v-for="item in payload.evidence" :key="item.id" class="evidence-item">
          <div class="evidence-head">
            <strong>{{ item.summary }}</strong>
            <span class="status-tag blue">+{{ item.score }} 分</span>
          </div>
          <div class="tiny-muted">{{ item.user.name }} · {{ item.evidence_type }} · {{ item.created_at }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import RadarChart from '@/components/common/RadarChart.vue'
import { projectApi } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const payload = ref<any>(null)
const selectedProfileId = ref<number | null>(null)

const analysisModeLabel = computed(() => {
  return payload.value?.summary?.analysis_mode === 'llm' ? '大模型 API' : '本地兜底分析'
})

const selectedProfile = computed(() => {
  const profiles = payload.value?.member_profiles || []
  return profiles.find((item: any) => item.user.id === selectedProfileId.value) || profiles[0] || null
})

const applyPayload = (data: any) => {
  payload.value = data
  const profiles = data?.member_profiles || []
  if (!profiles.length) {
    selectedProfileId.value = null
    return
  }
  const exists = profiles.some((item: any) => item.user.id === selectedProfileId.value)
  if (!exists) {
    selectedProfileId.value = profiles[0].user.id
  }
}

const load = async () => {
  const { data } = await projectApi.contribution(projectId.value)
  applyPayload(data)
}

const recalculate = async () => {
  const { data } = await projectApi.recalculateContribution(projectId.value)
  applyPayload(data)
  ElMessage.success('成员贡献画像已刷新')
}

const goCareer = async () => {
  await router.push(`/projects/${projectId.value}/career`)
}

watch(
  () => payload.value?.member_profiles,
  (profiles) => {
    if (profiles?.length && !selectedProfileId.value) {
      selectedProfileId.value = profiles[0].user.id
    }
  },
)

onMounted(load)
</script>

<style scoped>
.contribution-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row,
.panel-head,
.detail-header,
.evidence-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.thread-title {
  font-size: 22px;
  font-weight: 700;
}

.summary-card,
.ranking-panel,
.profile-list,
.profile-detail,
.evidence-panel {
  padding: 18px;
}

.summary-card {
  background:
    radial-gradient(circle at top right, rgba(79, 70, 229, 0.12), transparent 35%),
    #fff;
}

.panel-head {
  margin-bottom: 14px;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-cell img,
.profile-top img {
  width: 38px;
  height: 38px;
  border-radius: 50%;
}

.insight-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: 340px 1fr;
  align-items: start;
}

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-cards {
  display: flex;
  max-height: 760px;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
  overflow: auto;
}

.profile-card {
  padding: 16px;
  border: 1px solid #e6edff;
  border-radius: 18px;
  background: linear-gradient(180deg, #fff 0%, #f8fbff 100%);
  cursor: pointer;
  text-align: left;
}

.profile-card.active {
  border-color: rgba(79, 70, 229, 0.32);
  box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.16);
}

.profile-top,
.profile-bottom,
.chip-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.profile-bottom {
  justify-content: space-between;
  margin-top: 14px;
}

.profile-copy {
  margin-top: 12px;
  line-height: 1.6;
}

.profile-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-card {
  padding: 18px;
  border: 1px solid #eef2ff;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.chart-card {
  min-height: 280px;
}

.detail-copy {
  margin: 12px 0 0;
  color: var(--text-muted);
  line-height: 1.75;
}

.career-copy {
  margin-top: 14px;
}

.small-gap {
  margin-top: 18px;
}

.bullet-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.bullet-item {
  padding-left: 14px;
  color: var(--text-muted);
  line-height: 1.65;
  position: relative;
}

.bullet-item::before {
  position: absolute;
  top: 10px;
  left: 0;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  content: '';
}

.chip-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metrics-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.metric-box {
  padding: 14px 16px;
  border: 1px solid #eef2ff;
  border-radius: 16px;
  background: #fff;
}

.metric-box label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-muted);
  font-size: 12px;
}

.metric-box span {
  font-size: 20px;
  font-weight: 700;
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
  background: #fff;
}

@media (max-width: 1280px) {
  .summary-grid,
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .insight-grid,
  .detail-grid,
  .evidence-list {
    grid-template-columns: 1fr;
  }
}
</style>
