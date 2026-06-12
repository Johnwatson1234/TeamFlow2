<template>
  <div class="graph-page" v-if="graph">
    <div class="graph-left-panel">
      <div class="teamflow-card graph-filter">
        <div class="section-title">筛选条件</div>
        <div class="filter-item">
          <label>协作时间跨度</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </div>
        <div class="filter-item">
          <label>项目数据源</label>
          <el-select v-model="selectedProject" style="width: 100%;">
            <el-option label="课程设计-小组协作管理系统" value="课程设计-小组协作管理系统" />
          </el-select>
        </div>
      </div>

      <div class="teamflow-card graph-overview">
        <div class="section-title">图谱概览</div>
        <div class="metric-card cyan">
          <div class="metric-label">总节点数 (Nodes)</div>
          <div class="metric-value">{{ graph.nodes.length }}</div>
        </div>
        <div class="metric-card indigo">
          <div class="metric-label">关系连线 (Edges)</div>
          <div class="metric-value">{{ graph.edges.length }}</div>
        </div>
        <div class="metric-card purple">
          <div class="metric-label">网络密度 (Density)</div>
          <div class="metric-value">
            {{ (graph.edges.length / Math.max(1, graph.nodes.length * (graph.nodes.length - 1)) * 100).toFixed(1) }}%
          </div>
        </div>
      </div>
    </div>

    <div class="graph-main">
      <div class="teamflow-card graph-panel">
        <div class="panel-header">
          <div>
            <h1 class="page-title">协作图谱</h1>
            <div class="page-desc">节点：{{ graph.nodes.length }}，关系：{{ graph.edges.length }}</div>
          </div>
        </div>
        <GraphCanvas :edges="graph.edges" :nodes="graph.nodes" />
      </div>

      <div class="graph-side">
        <div class="teamflow-card side-card">
          <div class="panel-header">
            <div class="section-title">成员贡献排名</div>
          </div>
          <div class="rank-list">
            <div v-for="(item, index) in graph.member_ranking" :key="item.id" class="rank-row">
              <span>{{ Number(index) + 1 }}</span>
              <img :src="item.user.avatar" alt="avatar" />
              <span>{{ item.user.name }}</span>
              <el-progress :percentage="Math.min(item.total_score, 100)" :show-text="false" />
              <span>{{ item.total_score }}</span>
            </div>
          </div>
        </div>
        <div class="teamflow-card side-card">
          <div class="section-title">证据链摘要</div>
          <div class="evidence-row" v-for="(item, key) in graph.evidence_summary" :key="key">
            <span>{{ key }}</span>
            <span>{{ item.count }} / {{ item.ratio }}%</span>
          </div>
        </div>
        <div class="teamflow-card side-card">
          <div class="section-title">事件详情</div>
          <div class="evidence-row"><span>事件类型</span><span>{{ graph.event_detail.event_type }}</span></div>
          <div class="evidence-row"><span>事件ID</span><span>{{ graph.event_detail.event_id }}</span></div>
          <div class="evidence-row"><span>作者</span><span>{{ graph.event_detail.author }}</span></div>
          <div class="evidence-row"><span>时间</span><span>{{ graph.event_detail.time }}</span></div>
          <div class="page-desc">{{ graph.event_detail.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { projectApi } from '@/api'
import GraphCanvas from '@/components/common/GraphCanvas.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const graph = ref<any>(null)
const dateRange = ref(['2024-04-19', '2024-05-18'])
const selectedProject = ref('课程设计-小组协作管理系统')

const load = async () => {
  const { data } = await projectApi.graph(projectId.value)
  graph.value = data
}

onMounted(load)
</script>

<style scoped>
.graph-page {
  display: grid;
  gap: 18px;
  grid-template-columns: 220px 1fr;
}

.graph-left-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.graph-filter,
.graph-overview,
.graph-panel,
.side-card {
  padding: 18px;
}

.graph-filter {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.filter-item :deep(.el-range-editor.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 10px;
}

.filter-item :deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

.metric-card {
  padding: 16px;
  border-radius: 12px;
  margin-top: 14px;
  color: white;
}

.metric-card.cyan {
  background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
}

.metric-card.indigo {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
}

.metric-card.purple {
  background: linear-gradient(135deg, #A855F7 0%, #7E22CE 100%);
}

.metric-label {
  font-size: 13px;
  opacity: 0.9;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
}

.graph-main {
  display: grid;
  gap: 18px;
  grid-template-columns: 1fr 330px;
}

.graph-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel-header,
.rank-row,
.evidence-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.rank-row {
  display: grid;
  align-items: center;
  gap: 10px;
  grid-template-columns: 16px 30px 72px 1fr 46px;
}

.rank-row img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.evidence-row {
  margin-top: 14px;
}

@media (max-width: 1200px) {
  .graph-page,
  .graph-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .rank-row {
    grid-template-columns: 20px 30px 1fr;
  }

  .rank-row :deep(.el-progress) {
    grid-column: 1 / -1;
  }
}
</style>
