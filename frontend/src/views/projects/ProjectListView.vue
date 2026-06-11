<template>
  <AppViewport background="var(--bg)">
    <div class="page-shell project-list-page">
      <header class="list-topbar">
        <div class="top-left">
          <div class="logo-mark">⬡</div>
          <div class="brand-title">TeamFlow</div>
          <div class="product-name">小组协作过程管理软件</div>
        </div>
        <div class="top-nav">
          <button
            v-for="item in navItems"
            :key="item.key"
            :class="['nav-link', { active: item.key === 'projects' }]"
            type="button"
            @click="openWorkspaceSection(item.key)"
          >
            {{ item.label }}
          </button>
        </div>
        <div class="top-right">
          <el-button class="top-icon-btn bell" circle text @click="drawerVisible = true">
            <el-icon><Bell /></el-icon>
            <span>{{ notificationStore.unreadCount }}</span>
          </el-button>
          <el-dropdown @command="handleUserCommand">
            <div class="list-user-trigger">
              <img class="user-avatar" :src="userStore.user?.avatar" alt="avatar" />
              <div>
                <div>{{ userStore.user?.display_name }}</div>
                <div class="tiny-muted">{{ userStore.user?.title || '成员' }}</div>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="refresh">刷新项目</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div class="list-layout">
        <aside class="list-sidebar teamflow-card">
          <button
            v-for="item in scopeItems"
            :key="item.key"
            :class="['menu-item', { active: scopeFilter === item.key }]"
            type="button"
            @click="scopeFilter = item.key"
          >
            {{ item.label }}
          </button>
          <div class="side-section-title">项目分类</div>
          <button
            v-for="item in categoryItems"
            :key="item.value"
            :class="['tag-item', { active: categoryFilter === item.value }]"
            type="button"
            @click="categoryFilter = item.value"
          >
            {{ item.label }}
          </button>
          <div class="sidebar-note">
            <div class="section-title">项目空间说明</div>
            <div class="tiny-muted">在项目空间中，团队成员可以协同管理任务、文档、代码与进度，记录过程，沉淀成果。</div>
          </div>
        </aside>

        <main class="list-main">
          <div class="page-header-row">
            <div>
              <h1 class="page-title">{{ currentScopeMeta.title }}</h1>
              <div class="page-desc">{{ currentScopeMeta.description }}</div>
            </div>
            <el-button type="primary" @click="showCreate = true">创建项目</el-button>
          </div>

          <section class="grid-4">
            <StatCard title="待处理邀请" :value="notificationStore.myInvitations.length" footer="需要你确认加入项目" :icon="UserFilled" tint="rgba(245,158,11,.14)" icon-color="#f59e0b" />
            <StatCard title="我的待办" :value="myTodoCount" footer="进行中及待处理事项" :icon="DocumentChecked" tint="rgba(34,197,94,.12)" icon-color="#22c55e" />
            <StatCard title="未读提醒" :value="notificationStore.unreadCount" footer="最新协作动态与提醒" :icon="Bell" tint="rgba(139,92,246,.12)" icon-color="#8b5cf6" />
            <StatCard title="项目总数" :value="projects.length" footer="当前参与项目空间" :icon="FolderOpened" tint="rgba(79,70,229,.12)" icon-color="#4f46e5" />
          </section>

          <section class="filters teamflow-card">
            <el-input v-model="keyword" placeholder="搜索项目名称或关键词" />
            <el-select v-model="statusFilter" placeholder="全部状态">
              <el-option label="全部状态" value="" />
              <el-option label="进行中" value="进行中" />
              <el-option label="已结束" value="已结束" />
            </el-select>
            <el-select v-model="categoryFilter" placeholder="全部课程">
              <el-option label="全部课程" value="" />
              <el-option label="课程设计" value="课程设计" />
              <el-option label="竞赛项目" value="竞赛项目" />
              <el-option label="科研项目" value="科研项目" />
              <el-option label="其他项目" value="其他项目" />
            </el-select>
          </section>

          <section class="project-table-wrapper teamflow-card">
            <el-table :data="pagedProjects" style="width: 100%" @sort-change="handleSortChange">
              <template #empty>
                <el-empty description="当前筛选条件下暂无项目，试试切换分类或状态吧">
                  <el-button type="primary" plain @click="showCreate = true">创建项目</el-button>
                </el-empty>
              </template>
              <el-table-column label="项目名称 / 简介" min-width="320">
                <template #default="{ row }">
                  <div class="project-cell title">
                    <div class="project-icon">&lt;/&gt;</div>
                    <div>
                      <div class="project-name">{{ row.name }}</div>
                      <div class="status-tag blue">{{ row.category }}</div>
                      <div class="tiny-muted">{{ row.description }}</div>
                      <div class="project-meta">
                        <span>{{ row.course_name }}</span>
                        <span>{{ row.owner_name }} 负责</span>
                        <span>{{ row.is_owner ? '我创建的项目' : '我参与的项目' }}</span>
                      </div>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="成员" width="160">
                <template #default="{ row }">
                  <div class="avatar-group">
                    <img v-for="member in row.members?.slice(0, 4)" :key="member.id" :src="member.avatar" alt="avatar" />
                    <span style="margin-left: 8px; font-size: 13px; font-weight: 500;">{{ row.member_count }} 人</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="进度" width="180" sortable="custom" prop="progress">
                <template #default="{ row }">
                  <div class="progress-cell">
                    <el-progress :percentage="row.progress" :show-text="false" style="flex: 1;" />
                    <span style="font-size: 13px; min-width: 34px; font-weight: 500;">{{ row.progress }}%</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态与截止日期" width="180">
                <template #default="{ row }">
                  <div style="font-size: 13px; font-weight: 600; color: var(--text);">{{ row.due_date }}</div>
                  <div class="status-tag" :class="row.is_archived ? 'purple' : 'green'" style="margin-top: 6px;">{{ row.status }}</div>
                </template>
              </el-table-column>
              <el-table-column label="最近更新" width="180" sortable="custom" prop="updated_at">
                <template #default="{ row }">
                  <div style="font-size: 13px; font-weight: 500; color: var(--text);">{{ row.updated_at }}</div>
                  <div class="tiny-muted" style="margin-top: 2px;">{{ row.updated_by }} 更新</div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right" align="right">
                <template #default="{ row }">
                  <el-button plain type="primary" @click="router.push(`/projects/${row.id}`)">进入</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-container" v-if="filteredProjects.length > 0">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="filteredProjects.length"
              />
            </div>
          </section>
        </main>
      </div>

      <el-dialog v-model="showCreate" title="创建项目" width="min(640px, 92vw)">
        <el-form :model="createForm" label-position="top">
          <el-form-item label="项目名称">
            <el-input v-model="createForm.name" />
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="createForm.course_name" />
          </el-form-item>
          <el-form-item label="项目简介">
            <el-input v-model="createForm.description" rows="4" type="textarea" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCreate = false">取消</el-button>
          <el-button type="primary" @click="createProject">创建并进入</el-button>
        </template>
      </el-dialog>

      <el-drawer v-model="drawerVisible" title="协作提醒与通知" size="min(420px, 100vw)">
        <div class="drawer-block">
          <div class="section-title">待处理邀请</div>
          <div v-for="item in notificationStore.myInvitations" :key="item.id" class="drawer-item">
            <div>
              <div>{{ item.project_name }}</div>
              <div class="tiny-muted">{{ item.inviter?.name }} · {{ item.created_at }}</div>
            </div>
            <div class="drawer-actions">
              <el-button size="small" @click="rejectInvitation(item.id)">拒绝</el-button>
              <el-button size="small" type="primary" @click="acceptInvitation(item.id)">接受</el-button>
            </div>
          </div>
        </div>
        <div class="drawer-block">
          <div class="section-title">最新通知</div>
          <div v-for="item in notifications" :key="item.id" class="drawer-item clickable" @click="openNotification(item)">
            <div>
              <div>{{ item.title }}</div>
              <div class="tiny-muted">{{ item.content }}</div>
            </div>
            <span class="tiny-muted">{{ item.created_at?.slice(5, 16) }}</span>
          </div>
        </div>
      </el-drawer>
    </div>
  </AppViewport>
</template>

<script setup lang="ts">
import { Bell, DocumentChecked, FolderOpened, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { notificationApi, projectApi, taskApi } from '@/api'
import AppViewport from '@/components/common/AppViewport.vue'
import StatCard from '@/components/common/StatCard.vue'
import { useNotificationStore } from '@/stores/notification'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'

type ScopeFilter = 'all' | 'joined' | 'created' | 'archived'
type WorkspaceSection = 'projects' | 'tasks' | 'messages' | 'documents' | 'contribution'

const navItems: Array<{ key: WorkspaceSection; label: string }> = [
  { key: 'projects', label: '项目空间' },
  { key: 'tasks', label: '任务管理' },
  { key: 'messages', label: '消息' },
  { key: 'documents', label: '文档' },
  { key: 'contribution', label: '数据分析' },
]

const scopeItems: Array<{ key: ScopeFilter; label: string }> = [
  { key: 'all', label: '我的项目' },
  { key: 'joined', label: '我参与的项目' },
  { key: 'created', label: '我创建的项目' },
  { key: 'archived', label: '归档项目' },
]

const categoryItems = [
  { value: '', label: '全部项目' },
  { value: '课程设计', label: '课程设计' },
  { value: '竞赛项目', label: '竞赛项目' },
  { value: '科研项目', label: '科研项目' },
  { value: '其他项目', label: '其他项目' },
]

const router = useRouter()
const userStore = useUserStore()
const projectStore = useProjectStore()
const notificationStore = useNotificationStore()
const keyword = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const scopeFilter = ref<ScopeFilter>('all')
const showCreate = ref(false)
const drawerVisible = ref(false)
const myTasks = ref<any[]>([])
const notifications = ref<any[]>([])
const createForm = reactive({
  name: '',
  course_name: '',
  description: '',
  category: '课程设计',
  start_date: '2024-05-15',
  due_date: '2024-06-15 23:59',
  repo_url: '',
  advisor_name: '',
  advisor_email: '',
  tags: ['课程设计'],
})

const projects = computed(() => projectStore.projects)
const myTodoCount = computed(() => myTasks.value.filter((item) => item.status !== 'DONE').length)
const normalizedProjects = computed(() =>
  projects.value.map((item) => ({
    ...item,
    is_owner: item.owner_id === userStore.user?.id,
    is_archived: item.status === '已结束',
  })),
)

const currentScopeMeta = computed(() => {
  if (scopeFilter.value === 'joined') {
    return {
      title: '我参与的项目',
      description: '查看你作为成员参与协作的项目，快速进入任务、消息与文档工作区。',
    }
  }
  if (scopeFilter.value === 'created') {
    return {
      title: '我创建的项目',
      description: '集中管理你发起的项目，方便统一查看进度、风险与成员协作情况。',
    }
  }
  if (scopeFilter.value === 'archived') {
    return {
      title: '归档项目',
      description: '查看已结束或归档的历史项目，保留过程资料用于答辩、复盘与成果展示。',
    }
  }
  return {
    title: '我的项目',
    description: '管理和查看你创建或参与的所有项目空间。',
  }
})

const filteredProjects = computed(() =>
  normalizedProjects.value.filter((item) => {
    const matchScope =
      scopeFilter.value === 'all'
        ? true
        : scopeFilter.value === 'joined'
          ? !item.is_owner && !item.is_archived
          : scopeFilter.value === 'created'
            ? item.is_owner
            : item.is_archived
    const matchKeyword = !keyword.value || `${item.name}${item.description}${item.course_name}`.includes(keyword.value)
    const matchStatus = !statusFilter.value || item.status === statusFilter.value
    const matchCategory = !categoryFilter.value || item.category === categoryFilter.value
    return matchScope && matchKeyword && matchStatus && matchCategory
  }),
)

const currentPage = ref(1)
const pageSize = ref(10)
const sortProp = ref('')
const sortOrder = ref('')

const sortedProjects = computed(() => {
  let list = [...filteredProjects.value]
  if (sortProp.value && sortOrder.value) {
    list.sort((a, b) => {
      let valA = a[sortProp.value]
      let valB = b[sortProp.value]
      if (sortProp.value === 'progress') {
        valA = Number(valA)
        valB = Number(valB)
      }
      if (sortOrder.value === 'ascending') {
        return valA > valB ? 1 : -1
      } else {
        return valA < valB ? 1 : -1
      }
    })
  }
  return list
})

const pagedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return sortedProjects.value.slice(start, start + pageSize.value)
})

const handleSortChange = ({ prop, order }: { prop: string, order: string }) => {
  sortProp.value = prop
  sortOrder.value = order
}

watch([scopeFilter, keyword, statusFilter, categoryFilter], () => {
  currentPage.value = 1
})

const primaryProject = computed(() => filteredProjects.value[0] || normalizedProjects.value[0] || null)

const load = async () => {
  await Promise.all([
    projectStore.fetchProjects(),
    notificationStore.fetchUnreadCount(),
    notificationStore.fetchInvitations(),
  ])
  const noticeRes = await notificationApi.list()
  notifications.value = noticeRes.data
  const { data } = await taskApi.myTasks()
  myTasks.value = data
}

const openWorkspaceSection = async (section: WorkspaceSection) => {
  if (section === 'projects') {
    await router.push('/projects')
    return
  }
  if (!primaryProject.value) {
    ElMessage.warning('当前没有可进入的项目')
    return
  }
  await router.push(`/projects/${primaryProject.value.id}/${section}`)
}

const createProject = async () => {
  const { data } = await projectApi.create(createForm)
  ElMessage.success('项目创建成功')
  showCreate.value = false
  await projectStore.fetchProjects()
  router.push(`/projects/${data.id}`)
}

const acceptInvitation = async (id: number) => {
  await projectApi.acceptInvitation(id)
  ElMessage.success('已接受邀请')
  await load()
}

const rejectInvitation = async (id: number) => {
  await projectApi.rejectInvitation(id)
  ElMessage.warning('已拒绝邀请')
  await load()
}

const openNotification = async (item: any) => {
  if (!item.is_read) {
    await notificationApi.markRead(item.id)
  }
  if (item.project_id) {
    await router.push(`/projects/${item.project_id}`)
  }
}

const handleUserCommand = async (command: string) => {
  if (command === 'refresh') {
    await load()
    ElMessage.success('项目列表已刷新')
    return
  }
  if (command === 'logout') {
    userStore.logout()
    await router.push('/login')
  }
}

onMounted(load)
</script>

<style scoped>
.project-list-page {
  min-height: 100dvh;
}

.list-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 68px;
  padding: 0 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.86);
  background: rgba(255, 255, 255, 0.96);
}

.top-left,
.top-right,
.top-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-mark {
  display: grid;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  place-items: center;
  background: linear-gradient(135deg, #79a8ff 0%, #4f46e5 100%);
  color: white;
}

.brand-title {
  font-size: 22px;
  font-weight: 700;
}

.product-name {
  margin-left: 18px;
  padding-left: 18px;
  border-left: 1px solid #e2e8f0;
  font-size: 15px;
  font-weight: 600;
}

.top-nav {
  gap: 8px;
}

.nav-link {
  padding: 8px 12px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font: inherit;
}

.nav-link.active,
.nav-link:hover {
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
  font-weight: 700;
}

.top-icon-btn {
  position: relative;
  color: var(--text);
}

.list-layout {
  display: grid;
  gap: 18px;
  min-height: calc(100dvh - 68px);
  padding: 18px;
  grid-template-columns: 230px 1fr;
}

.list-sidebar {
  padding: 18px 14px;
}

.menu-item,
.tag-item {
  display: block;
  width: 100%;
  padding: 12px 14px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.menu-item.active,
.menu-item:hover,
.tag-item.active,
.tag-item:hover {
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
  font-weight: 700;
}

.side-section-title {
  margin: 18px 0 10px;
  padding: 14px 10px 0;
  border-top: 1px solid #e8edf7;
  color: var(--text);
  font-weight: 700;
}

.sidebar-note {
  margin-top: 26px;
  padding: 18px 16px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.list-main {
  min-width: 0;
  min-height: 0;
  overflow: visible;
}

.page-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.filters {
  display: grid;
  gap: 16px;
  margin: 14px 0;
  padding: 14px;
  grid-template-columns: 1.2fr 180px 180px;
}

.project-table-wrapper {
  padding: 16px;
  overflow: hidden;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.project-cell.title {
  display: flex;
  gap: 16px;
  align-items: center;
}

.project-icon {
  display: grid;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  place-items: center;
  background: linear-gradient(135deg, #4f6cf3 0%, #2563eb 100%);
  color: white;
  font-weight: 700;
}

.project-name {
  margin-bottom: 6px;
  font-size: 18px;
  font-weight: 700;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
  color: var(--text-light);
  font-size: 12px;
}

.avatar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-group img,
.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}

.list-user-trigger {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.progress-cell {
  display: flex;
  gap: 12px;
  align-items: center;
}

.bell {
  position: relative;
}

.bell span {
  position: absolute;
  top: -9px;
  right: -9px;
  display: grid;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  place-items: center;
  background: var(--danger);
  color: white;
  font-size: 11px;
}

.drawer-block + .drawer-block {
  margin-top: 24px;
}

.drawer-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #eef2ff;
}

.drawer-item.clickable {
  cursor: pointer;
}

.drawer-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 1200px) {
  .list-layout {
    grid-template-columns: 1fr;
  }

  .list-sidebar {
    order: 2;
  }

  .filters {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .list-topbar {
    height: auto;
    padding: 14px 16px;
    align-items: flex-start;
    gap: 14px;
    flex-direction: column;
  }

  .top-left,
  .top-right {
    width: 100%;
    justify-content: space-between;
  }

  .top-left {
    flex-wrap: wrap;
    gap: 10px;
  }

  .product-name {
    margin-left: 0;
    padding-left: 0;
    border-left: 0;
    width: 100%;
  }

  .top-nav {
    width: 100%;
    overflow: auto;
  }

  .list-user-trigger > div {
    display: none;
  }

  .list-layout {
    min-height: auto;
    padding: 12px;
  }

  .page-header-row {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .filters {
    grid-template-columns: 1fr;
  }

  .project-table-wrapper {
    padding: 14px 0;
  }
  
  .project-cell.title {
    align-items: flex-start;
  }

  .project-icon {
    width: 48px;
    height: 48px;
  }

  .project-name {
    font-size: 16px;
  }

  .avatar-group,
  .progress-cell {
    flex-wrap: wrap;
  }

  .drawer-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
