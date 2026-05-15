<template>
  <div class="graph-page" v-if="graph">
    <div class="teamflow-card graph-filter">
      <div class="section-title">筛选条件</div>
      <el-input value="2024-04-19 ~ 2024-05-18" />
      <el-select model-value="课程设计-小组协作管理系统">
        <el-option label="课程设计-小组协作管理系统" value="课程设计-小组协作管理系统" />
      </el-select>
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

.graph-filter,
.graph-panel,
.side-card {
  padding: 18px;
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
</style>
