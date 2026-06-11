<template>
  <div class="git-page" v-if="payload">
    <div class="header-row">
      <div>
        <h1 class="page-title">代码提交与冲突风险</h1>
        <div class="page-desc">追踪代码提交证据、分支关系、修改热点与合并风险预警</div>
      </div>
    </div>
    <section class="grid-4">
      <StatCard title="今日提交数" :value="payload.overview.today_commits" footer="较昨日 ↑ 5" :icon="Connection" tint="rgba(139,92,246,.12)" icon-color="#8b5cf6" />
      <StatCard title="活跃分支" :value="payload.overview.active_branches" footer="较上周 ↑ 2" :icon="Share" tint="rgba(59,130,246,.12)" icon-color="#3b82f6" />
      <StatCard title="冲突风险文件" :value="payload.overview.conflict_files" footer="较昨日 ↑ 3" :icon="Warning" tint="rgba(245,158,11,.12)" icon-color="#f59e0b" />
      <StatCard title="待处理合并请求" :value="payload.overview.pending_prs" footer="较昨日 ↓ 1" :icon="Tickets" tint="rgba(34,197,94,.12)" icon-color="#22c55e" />
    </section>
    <div class="git-grid">
      <div class="teamflow-card panel">
        <div class="section-title">最近提交</div>
        <div class="commit-list">
          <div v-for="item in payload.recent_commits" :key="item.id" class="commit-item">
            <img :src="item.author.avatar" alt="avatar" />
            <div>
              <div>{{ item.author.name }} · {{ item.commit_hash }}</div>
              <div class="tiny-muted">{{ item.message }} · {{ item.branch_name }}</div>
            </div>
            <span class="status-tag green">质量分 {{ item.quality_score }}</span>
          </div>
        </div>
      </div>
      <div class="teamflow-card panel">
        <div class="section-title">分支图谱</div>
        <div class="branch-list">
          <div v-for="item in payload.branch_graph" :key="item.commit" class="branch-row">
            <span class="status-tag blue">{{ item.branch }}</span>
            <span>{{ item.author }}</span>
            <span class="tiny-muted">{{ item.commit }}</span>
          </div>
        </div>
      </div>
      <div class="teamflow-card panel">
        <div class="section-title">冲突风险预警</div>
        <div class="conflict-list">
          <div v-for="item in payload.conflict_files" :key="item.path" class="conflict-item">
            <div>
              <div>{{ item.path }}</div>
              <div class="tiny-muted">{{ item.suggestion }}</div>
            </div>
            <span :class="['status-tag', item.level === '高' ? 'red' : item.level === '中' ? 'orange' : 'green']">{{ item.level }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="git-bottom">
      <div class="teamflow-card panel">
        <div class="section-title">修改热点热力表（近 7 天）</div>
        <el-table :data="payload.hotspots">
          <el-table-column label="文件路径" prop="path" min-width="220" />
          <el-table-column label="修改次数" prop="changes" width="100" />
          <el-table-column label="增删行数" prop="lines" width="140" />
          <el-table-column label="参与人数" prop="participants" width="100" />
          <el-table-column label="热点指数" width="180">
            <template #default="{ row }">
              <div class="heat-cell">
                <div class="heat-bar">
                  <div class="heat-fill" :style="{ width: `${row.heat}%`, background: heatGradient(row.heat) }"></div>
                </div>
                <strong :style="{ color: heatTextColor(row.heat) }">{{ row.heat }}</strong>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="teamflow-card panel">
        <div class="section-title">仓库绑定信息</div>
        <div class="repo-item"><label>仓库</label><span>{{ payload.repository.name }}</span></div>
        <div class="repo-item"><label>远程地址</label><span>{{ payload.repository.url }}</span></div>
        <div class="repo-item"><label>默认分支</label><span>{{ payload.repository.default_branch }}</span></div>
        <div class="repo-item"><label>同步状态</label><span>{{ payload.repository.sync_status }}</span></div>
        <div class="repo-item"><label>最近同步</label><span>{{ payload.repository.last_synced_at }}</span></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Connection, Share, Tickets, Warning } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { projectApi } from '@/api'
import StatCard from '@/components/common/StatCard.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const payload = ref<any>(null)

const load = async () => {
  const { data } = await projectApi.git(projectId.value)
  payload.value = data
}

const heatGradient = (heat: number) => {
  if (heat >= 80) return 'linear-gradient(90deg, #f97316 0%, #ef4444 100%)'
  if (heat >= 60) return 'linear-gradient(90deg, #f59e0b 0%, #f97316 100%)'
  if (heat >= 40) return 'linear-gradient(90deg, #14b8a6 0%, #0ea5e9 100%)'
  return 'linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%)'
}

const heatTextColor = (heat: number) => {
  if (heat >= 80) return '#dc2626'
  if (heat >= 60) return '#ea580c'
  if (heat >= 40) return '#0f766e'
  return '#4f46e5'
}

onMounted(load)
</script>

<style scoped>
.git-page,
.git-bottom {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.git-grid,
.git-bottom {
  display: grid;
  gap: 18px;
  grid-template-columns: 1fr 1fr 1fr;
}

.panel {
  padding: 18px;
}

.commit-list,
.branch-list,
.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 16px;
}

.commit-item,
.branch-row,
.conflict-item,
.repo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.commit-item img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}

.repo-item {
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.repo-item label {
  color: var(--text-muted);
}

.heat-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.heat-bar {
  position: relative;
  width: 100px;
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: linear-gradient(180deg, #edf4fa 0%, #e2ebf5 100%);
}

.heat-fill {
  height: 100%;
  border-radius: inherit;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.14);
}

@media (max-width: 1200px) {
  .git-grid,
  .git-bottom {
    grid-template-columns: 1fr 1fr;
  }

  .git-grid > :first-child,
  .git-bottom > :first-child {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .git-grid,
  .git-bottom {
    grid-template-columns: 1fr;
  }

  .commit-item,
  .branch-row,
  .conflict-item,
  .repo-item {
    align-items: flex-start;
    gap: 10px;
    flex-direction: column;
  }
}
</style>
