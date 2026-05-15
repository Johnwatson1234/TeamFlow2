<template>
  <div class="tasks-page" v-loading="loading">
    <div class="header-row">
      <div>
        <h1 class="page-title">任务管理</h1>
        <div class="page-desc">管理和跟踪项目任务，推进任务协同与交付</div>
      </div>
      <div class="header-actions">
        <el-button @click="detailOpen = !detailOpen">批量操作</el-button>
        <el-button type="primary" @click="openCreate">新建任务</el-button>
      </div>
    </div>

    <div class="filters teamflow-card">
      <el-select v-model="filters.assignee" placeholder="全部成员"><el-option label="全部成员" value="" /></el-select>
      <el-select v-model="filters.milestone" placeholder="全部里程碑"><el-option label="全部里程碑" value="" /></el-select>
      <el-select v-model="filters.priority" placeholder="全部优先级"><el-option label="全部优先级" value="" /></el-select>
      <el-select v-model="filters.status" placeholder="全部状态"><el-option label="全部状态" value="" /></el-select>
      <el-input v-model="filters.keyword" placeholder="搜索任务标题或关键词" />
    </div>

    <div class="kanban-layout">
      <div class="kanban-board">
        <div v-for="column in columns" :key="column.key" class="kanban-column teamflow-card">
          <div class="column-head">
            <span>{{ column.label }}</span>
            <b>{{ grouped[column.key]?.length || 0 }}</b>
          </div>
          <div class="column-list">
            <div v-for="task in grouped[column.key]" :key="task.id" class="task-card" @click="selectTask(task)">
              <div class="task-title">{{ task.title }}</div>
              <div class="task-owner">
                <img v-if="task.assignee" :src="task.assignee.avatar" alt="avatar" />
                <span>{{ task.assignee?.name || '待分配' }}</span>
                <span class="priority" :class="task.priority">{{ task.priority }}</span>
              </div>
              <el-progress :percentage="task.progress" :show-text="false" />
              <div class="task-foot">
                <span>{{ task.due_date }}</span>
                <span>{{ task.progress }}%</span>
              </div>
              <div v-if="task.blocker_reason" class="blocker">阻塞原因：{{ task.blocker_reason }}</div>
            </div>
          </div>
          <div class="action-link add-task" @click="openCreate(column.key)">+ 添加任务</div>
        </div>
      </div>

      <aside class="task-detail teamflow-card" v-if="selectedTask && detailOpen">
        <div class="detail-head">
          <h3>任务详情</h3>
          <el-button text @click="detailOpen = false">关闭</el-button>
        </div>
        <el-tabs v-model="detailTab">
          <el-tab-pane label="基本信息" name="info">
            <div class="detail-title">{{ selectedTask.title }}</div>
            <p class="page-desc">{{ selectedTask.description }}</p>
            <div class="detail-grid">
              <div><label>负责人</label><span>{{ selectedTask.assignee?.name || '待分配' }}</span></div>
              <div><label>优先级</label><span>{{ selectedTask.priority }}</span></div>
              <div><label>状态</label><span>{{ selectedTask.response_status }}</span></div>
              <div><label>进度</label><span>{{ selectedTask.progress }}%</span></div>
              <div><label>开始日期</label><span>{{ selectedTask.start_date }}</span></div>
              <div><label>截止日期</label><span>{{ selectedTask.due_date }}</span></div>
            </div>
            <div class="related-box">
              <div><label>关联需求</label><a class="action-link" @click="openRelated('requirement')">{{ selectedTask.related_requirement }}</a></div>
              <div><label>关联文档</label><a class="action-link" @click="openRelated('document')">{{ selectedTask.related_document }}</a></div>
              <div><label>关联提交</label><a class="action-link" @click="openRelated('commit')">{{ selectedTask.related_commit }}</a></div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="活动记录" name="activities">
            <div class="activity-list">
              <div v-for="activity in activities" :key="activity.id" class="activity-item">
                <img :src="activity.actor?.avatar" alt="avatar" />
                <div>
                  <div>{{ activity.content }}</div>
                  <div class="tiny-muted">{{ activity.created_at }}</div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        <div class="detail-actions">
          <el-button @click="showEdit = true">编辑任务</el-button>
          <el-button type="warning" @click="markBlocked">标记阻塞</el-button>
          <el-button type="primary" @click="acceptTask">更新进度</el-button>
        </div>
      </aside>
    </div>

    <div class="teamflow-card milestones-panel">
      <div class="panel-header">
        <div class="section-title">里程碑进度</div>
        <router-link class="action-link" :to="`/projects/${projectId}/milestones`">查看全部里程碑</router-link>
      </div>
      <div class="milestone-track">
        <div v-for="item in milestones" :key="item.id" class="milestone-item">
          <div class="milestone-name">{{ item.name }}</div>
          <div class="milestone-status">{{ item.status }}</div>
          <div class="milestone-date">{{ item.due_date }}</div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showEdit" :title="editingTask.id ? '编辑任务' : '新建任务'" width="680px">
      <el-form :model="editingTask" label-position="top">
        <el-form-item label="任务标题"><el-input v-model="editingTask.title" /></el-form-item>
        <el-form-item label="任务描述"><el-input v-model="editingTask.description" rows="4" type="textarea" /></el-form-item>
        <div class="grid-2">
          <el-form-item label="优先级">
            <el-select v-model="editingTask.priority">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </el-form-item>
          <el-form-item label="截止日期"><el-input v-model="editingTask.due_date" /></el-form-item>
        </div>
        <div class="grid-2">
          <el-form-item label="负责人">
            <el-select v-model="editingTask.assignee_id" clearable>
              <el-option v-for="member in members" :key="member.user_id" :label="member.name" :value="member.user_id" />
            </el-select>
          </el-form-item>
          <el-form-item label="里程碑">
            <el-select v-model="editingTask.milestone_id">
              <el-option v-for="item in milestones" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { projectApi, taskApi } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const loading = ref(false)
const tasks = ref<any[]>([])
const milestones = ref<any[]>([])
const activities = ref<any[]>([])
const members = ref<any[]>([])
const selectedTask = ref<any>(null)
const detailOpen = ref(true)
const detailTab = ref('info')
const showEdit = ref(false)
const filters = reactive({ assignee: '', milestone: '', priority: '', status: '', keyword: '' })
const editingTask = reactive<any>({
  id: null,
  title: '',
  description: '',
  priority: '中',
  due_date: '',
  assignee_id: null,
  milestone_id: null,
  status: 'TODO',
  progress: 0,
  start_date: '2024-05-15',
  blocker_reason: '',
  related_requirement: '',
  related_document: '',
  related_commit: '',
})

const columns = [
  { key: 'TODO', label: '待处理' },
  { key: 'IN_PROGRESS', label: '进行中' },
  { key: 'BLOCKED', label: '阻塞中' },
  { key: 'REVIEW', label: '待评审' },
  { key: 'DONE', label: '已完成' },
]

const grouped = computed(() =>
  columns.reduce<Record<string, any[]>>((acc, column) => {
    acc[column.key] = tasks.value.filter((task) => task.status === column.key)
    return acc
  }, {}),
)

const load = async () => {
  loading.value = true
  try {
    const [taskRes, milestoneRes, memberRes] = await Promise.all([
      taskApi.list(projectId.value),
      taskApi.milestones(projectId.value),
      projectApi.members(projectId.value),
    ])
    tasks.value = taskRes.data
    milestones.value = milestoneRes.data
    members.value = memberRes.data
    selectedTask.value = tasks.value[3] || tasks.value[0]
    if (selectedTask.value) await loadActivities(selectedTask.value.id)
  } finally {
    loading.value = false
  }
}

const loadActivities = async (taskId: number) => {
  const { data } = await taskApi.activities(taskId)
  activities.value = data
}

const selectTask = async (task: any) => {
  selectedTask.value = task
  detailOpen.value = true
  await loadActivities(task.id)
}

const openCreate = (status = 'TODO') => {
  Object.assign(editingTask, {
    id: null,
    title: '',
    description: '',
    priority: '中',
    due_date: '',
    assignee_id: null,
    milestone_id: milestones.value[0]?.id ?? null,
    status,
    progress: 0,
    start_date: '2024-05-15',
    blocker_reason: '',
    related_requirement: '',
    related_document: '',
    related_commit: '',
  })
  showEdit.value = true
}

const saveTask = async () => {
  if (editingTask.id) {
    await taskApi.update(editingTask.id, editingTask)
    ElMessage.success('任务已更新')
  } else {
    await taskApi.create(projectId.value, editingTask)
    ElMessage.success('任务已创建')
  }
  showEdit.value = false
  await load()
}

const acceptTask = async () => {
  if (!selectedTask.value) return
  await taskApi.accept(selectedTask.value.id)
  ElMessage.success('已开始处理任务')
  await load()
}

const markBlocked = async () => {
  if (!selectedTask.value) return
  await taskApi.block(selectedTask.value.id, { blocker_reason: '等待接口定义完成后继续推进' })
  ElMessage.warning('任务已标记阻塞')
  await load()
}

const openRelated = async (type: 'requirement' | 'document' | 'commit') => {
  if (!selectedTask.value) return
  if (type === 'document') {
    await router.push(`/projects/${projectId.value}/documents`)
    return
  }
  if (type === 'commit') {
    await router.push(`/projects/${projectId.value}/git`)
    return
  }
  ElMessage.info(`关联需求：${selectedTask.value.related_requirement}`)
}

onMounted(load)
</script>

<style scoped>
.tasks-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row,
.header-actions,
.column-head,
.panel-header,
.task-owner,
.task-foot,
.detail-head,
.detail-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filters {
  display: grid;
  gap: 14px;
  padding: 18px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.kanban-layout {
  display: grid;
  gap: 18px;
  grid-template-columns: 1fr 320px;
}

.kanban-board {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.kanban-column {
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.column-head {
  margin-bottom: 12px;
  font-weight: 700;
}

.column-head b {
  display: grid;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  place-items: center;
  background: #eef2ff;
  color: var(--text-muted);
}

.column-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  padding: 14px;
  border: 1px solid #edf1ff;
  border-radius: 16px;
  cursor: pointer;
  transition: 0.2s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.08);
}

.task-title {
  min-height: 44px;
  font-weight: 700;
}

.task-owner {
  margin: 10px 0;
  gap: 6px;
  justify-content: flex-start;
}

.task-owner img,
.activity-item img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.priority {
  margin-left: auto;
  font-size: 12px;
}

.priority.高 {
  color: var(--danger);
}

.priority.中 {
  color: var(--warning);
}

.priority.低 {
  color: var(--success);
}

.task-foot {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 12px;
}

.blocker {
  margin-top: 10px;
  padding: 6px 8px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  font-size: 12px;
}

.add-task {
  margin-top: 10px;
  text-align: center;
}

.task-detail,
.milestones-panel {
  padding: 18px;
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
}

.detail-grid,
.related-box {
  display: grid;
  gap: 14px;
  margin-top: 20px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-grid label,
.related-box label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-muted);
  font-size: 13px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.activity-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.milestone-track {
  display: grid;
  gap: 12px;
  margin-top: 18px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.milestone-item {
  padding: 14px;
  border-radius: 14px;
  background: #f8faff;
}

.milestone-name {
  font-weight: 700;
}

.milestone-status {
  margin: 8px 0 6px;
  color: var(--primary);
}
</style>
