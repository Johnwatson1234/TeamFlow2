<template>
  <div class="career-page" v-if="payload">
    <div class="hero-card teamflow-card">
      <div class="hero-copy">
        <span class="status-tag purple">AI 个性化展示</span>
        <h1 class="page-title">成员画像与岗位推荐</h1>
        <div class="page-desc">
          基于消息讨论、任务闭环、文档沉淀和技术输出，对每位成员生成协作风格、性格倾向和适配岗位建议。
        </div>
        <div class="hero-metrics">
          <div class="hero-metric">
            <label>分析模式</label>
            <strong>{{ payload.summary?.analysis_mode === 'llm' ? '智谱大模型' : '本地兜底分析' }}</strong>
          </div>
          <div class="hero-metric">
            <label>覆盖成员</label>
            <strong>{{ payload.summary?.member_count || 0 }}</strong>
          </div>
          <div class="hero-metric">
            <label>讨论消息</label>
            <strong>{{ payload.summary?.message_count || 0 }}</strong>
          </div>
          <div class="hero-metric">
            <label>生成时间</label>
            <strong>{{ payload.summary?.generated_at }}</strong>
          </div>
        </div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="recalculate">重新生成画像</el-button>
        <el-button @click="goContribution">查看贡献证据</el-button>
      </div>
    </div>

    <div class="career-grid" v-if="payload.member_profiles?.length">
      <aside class="teamflow-card member-column">
        <div class="section-title">成员列表</div>
        <div class="section-subtitle">选择成员查看单独画像与岗位建议</div>
        <div class="member-list app-scroll">
          <button
            v-for="item in payload.member_profiles"
            :key="item.user.id"
            :class="['member-card', { active: item.user.id === selectedProfile?.user.id }]"
            type="button"
            @click="selectedProfileId = item.user.id"
          >
            <div class="member-head">
              <img :src="item.user.avatar" alt="avatar" />
              <div>
                <strong>{{ item.user.name }}</strong>
                <div class="tiny-muted">{{ item.profile_label }}</div>
              </div>
            </div>
            <div class="member-role">{{ item.recommended_roles?.[0] }}</div>
            <div class="tiny-muted member-summary">{{ item.career_recommendation }}</div>
          </button>
        </div>
      </aside>

      <section v-if="selectedProfile" class="detail-column">
        <div class="teamflow-card spotlight-card">
          <div class="spotlight-head">
            <div>
              <div class="tiny-muted">当前成员</div>
              <div class="spotlight-title">{{ selectedProfile.user.name }}</div>
              <div class="page-desc">{{ selectedProfile.personality_summary }}</div>
            </div>
            <div class="spotlight-tags">
              <span class="status-tag purple">{{ selectedProfile.profile_label }}</span>
              <span class="status-tag blue">总分 {{ selectedProfile.total_score }}</span>
            </div>
          </div>
          <div class="spotlight-grid">
            <div class="spotlight-block">
              <div class="section-title">岗位建议</div>
              <div class="role-tags">
                <span v-for="item in selectedProfile.recommended_roles" :key="item" class="status-tag green">{{ item }}</span>
              </div>
              <p class="spotlight-copy">{{ selectedProfile.career_recommendation }}</p>
            </div>
            <div class="spotlight-block">
              <div class="section-title">沟通风格</div>
              <p class="spotlight-copy">{{ selectedProfile.communication_style }}</p>
              <div class="section-title secondary-title">项目内总结</div>
              <p class="spotlight-copy">{{ selectedProfile.contribution_summary }}</p>
            </div>
          </div>
        </div>

        <div class="detail-grid">
          <div class="teamflow-card chart-card">
            <div class="section-title">能力雷达</div>
            <RadarChart :items="selectedProfile.radar" />
          </div>

          <div class="teamflow-card metric-panel">
            <div class="section-title">行为指标</div>
            <div class="metric-grid">
              <div class="metric-item">
                <label>消息</label>
                <strong>{{ selectedProfile.metrics.message_count }}</strong>
              </div>
              <div class="metric-item">
                <label>想法</label>
                <strong>{{ selectedProfile.metrics.idea_count }}</strong>
              </div>
              <div class="metric-item">
                <label>完成任务</label>
                <strong>{{ selectedProfile.metrics.completed_tasks }}</strong>
              </div>
              <div class="metric-item">
                <label>文档</label>
                <strong>{{ selectedProfile.metrics.document_count }}</strong>
              </div>
              <div class="metric-item">
                <label>代码消息</label>
                <strong>{{ selectedProfile.metrics.code_message_count }}</strong>
              </div>
              <div class="metric-item">
                <label>任务进度</label>
                <strong>{{ selectedProfile.metrics.avg_task_progress }}%</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-grid">
          <div class="teamflow-card list-panel">
            <div class="section-title">优势特征</div>
            <div class="bullet-list">
              <div v-for="item in selectedProfile.strengths" :key="item" class="bullet-item">{{ item }}</div>
            </div>
          </div>
          <div class="teamflow-card list-panel">
            <div class="section-title">待提升点</div>
            <div class="bullet-list">
              <div v-for="item in selectedProfile.risks" :key="item" class="bullet-item">{{ item }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { projectApi } from '@/api'
import RadarChart from '@/components/common/RadarChart.vue'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const payload = ref<any>(null)
const selectedProfileId = ref<number | null>(null)

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
  if (!profiles.some((item: any) => item.user.id === selectedProfileId.value)) {
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
  ElMessage.success('成员画像已更新')
}

const goContribution = async () => {
  await router.push(`/projects/${projectId.value}/contribution`)
}

onMounted(load)
</script>

<style scoped>
.career-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-card,
.member-column,
.spotlight-card,
.chart-card,
.metric-panel,
.list-panel {
  padding: 20px;
}

.hero-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  background:
    radial-gradient(circle at top right, rgba(79, 70, 229, 0.18), transparent 28%),
    radial-gradient(circle at bottom left, rgba(6, 182, 212, 0.14), transparent 24%),
    #fff;
}

.hero-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 14px;
}

.hero-metrics {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.hero-metric {
  padding: 14px 16px;
  border: 1px solid #e8efff;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
}

.hero-metric label,
.metric-item label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-muted);
  font-size: 12px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.career-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: 320px 1fr;
}

.member-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-list {
  display: flex;
  max-height: 860px;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
  overflow: auto;
}

.member-card {
  padding: 16px;
  border: 1px solid #e8efff;
  border-radius: 18px;
  background: linear-gradient(180deg, #fff 0%, #f8fbff 100%);
  text-align: left;
  cursor: pointer;
}

.member-card.active {
  border-color: rgba(79, 70, 229, 0.34);
  box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.16);
}

.member-head,
.spotlight-head,
.spotlight-tags,
.role-tags {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.member-head img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.member-role {
  margin-top: 12px;
  font-weight: 700;
  color: var(--primary);
}

.member-summary {
  margin-top: 8px;
  line-height: 1.6;
}

.detail-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.spotlight-title {
  font-size: 24px;
  font-weight: 700;
}

.spotlight-grid,
.detail-grid,
.metric-grid {
  display: grid;
  gap: 14px;
}

.spotlight-grid,
.detail-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.spotlight-grid {
  margin-top: 18px;
}

.spotlight-block {
  padding: 18px;
  border: 1px solid #eef2ff;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.spotlight-copy {
  margin: 12px 0 0;
  color: var(--text-muted);
  line-height: 1.75;
}

.secondary-title {
  margin-top: 18px;
}

.chart-card,
.metric-panel {
  min-height: 320px;
}

.metric-grid {
  margin-top: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric-item {
  padding: 16px;
  border: 1px solid #eef2ff;
  border-radius: 16px;
  background: #fff;
}

.metric-item strong {
  font-size: 22px;
}

.bullet-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.bullet-item {
  position: relative;
  padding-left: 14px;
  color: var(--text-muted);
  line-height: 1.7;
}

.bullet-item::before {
  position: absolute;
  top: 11px;
  left: 0;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  content: '';
}

@media (max-width: 1280px) {
  .hero-card,
  .career-grid,
  .spotlight-grid,
  .detail-grid,
  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
  }
}
</style>
