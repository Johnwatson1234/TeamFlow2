<template>
  <AppViewport background="var(--bg)">
    <div class="project-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">⬡</div>
        <div class="brand-name">TeamFlow</div>
      </div>

      <div class="project-switch">
        <div class="switch-icon">&lt;/&gt;</div>
        <div>
          <div class="switch-name">{{ currentProject?.name || '加载中...' }}</div>
          <div class="switch-status">
            <span class="status-dot"></span>
            进行中
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.name" :to="item.to" class="nav-item" :class="{ active: route.name === item.name }">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <router-link :to="`/projects/${projectId}/reminders`" class="reminder-shortcut" :class="{ active: route.name === 'reminders' }">
        <span>协作提醒</span>
        <b>{{ notificationStore.unreadCount }}</b>
      </router-link>

      <div class="sidebar-user">
        <img :src="userStore.user?.avatar" alt="avatar" />
        <div>
          <div class="user-name">{{ userStore.user?.display_name }}</div>
          <div class="tiny-muted">{{ userStore.user?.title || '成员' }}</div>
        </div>
      </div>
    </aside>

    <div class="project-main">
      <header class="project-topbar">
        <div class="topbar-left">
          <el-icon :size="20"><Operation /></el-icon>
          <div class="breadcrumb">
            <span>项目空间</span>
            <span>/</span>
            <span>{{ currentProject?.name }}</span>
            <span>/</span>
            <strong>{{ pageLabel }}</strong>
          </div>
        </div>
        <div class="topbar-right">
          <el-button class="top-icon-btn" circle text @click="searchVisible = true">
            <el-icon :size="18"><Search /></el-icon>
          </el-button>
          <el-button class="top-icon-btn bell" circle text @click="goReminders">
            <el-icon :size="18"><Bell /></el-icon>
            <span>{{ notificationStore.unreadCount }}</span>
          </el-button>
          <el-dropdown @command="handleUserCommand">
            <div class="user-trigger">
              <img class="topbar-avatar" :src="userStore.user?.avatar" alt="avatar" />
              <div class="topbar-user">
                <div>{{ userStore.user?.display_name }}</div>
                <div class="tiny-muted">{{ userStore.user?.title || '成员' }}</div>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="reminders">我的工作台</el-dropdown-item>
                <el-dropdown-item command="settings">项目设置</el-dropdown-item>
                <el-dropdown-item command="projects">项目列表</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="project-content">
        <router-view v-slot="{ Component }">
          <component :is="Component" class="project-page-view" />
        </router-view>
      </main>
    </div>
    </div>
    <el-dialog v-model="searchVisible" title="快速搜索与跳转" width="560px">
      <el-input v-model="searchKeyword" clearable placeholder="搜索页面、功能、任务关键词" />
      <div class="search-shortcuts">
        <button
          v-for="item in filteredActions"
          :key="item.name"
          class="search-action"
          @click="jumpTo(item.to)"
        >
          <strong>{{ item.label }}</strong>
          <span class="tiny-muted">{{ item.to }}</span>
        </button>
      </div>
    </el-dialog>
  </AppViewport>
</template>

<script setup lang="ts">
import {
  Avatar,
  Bell,
  ChatDotRound,
  Connection,
  DataAnalysis,
  Document,
  Files,
  HomeFilled,
  Monitor,
  Operation,
  Search,
  SetUp,
  Share,
  Warning,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppViewport from '@/components/common/AppViewport.vue'
import { useNotificationStore } from '@/stores/notification'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const notificationStore = useNotificationStore()
const userStore = useUserStore()
const searchVisible = ref(false)
const searchKeyword = ref('')

const projectId = computed(() => route.params.id as string)
const currentProject = computed(() => projectStore.currentProject)

const navItems = computed(() => [
  { name: 'dashboard', label: '项目仪表盘', icon: HomeFilled, to: `/projects/${projectId.value}` },
  { name: 'tasks', label: '任务管理', icon: Document, to: `/projects/${projectId.value}/tasks` },
  { name: 'milestones', label: '里程碑管理', icon: Monitor, to: `/projects/${projectId.value}/milestones` },
  { name: 'messages', label: '消息与讨论', icon: ChatDotRound, to: `/projects/${projectId.value}/messages` },
  { name: 'documents', label: '文档协作', icon: Files, to: `/projects/${projectId.value}/documents` },
  { name: 'files', label: '文件管理', icon: Share, to: `/projects/${projectId.value}/files` },
  { name: 'git', label: 'Git 协作', icon: Connection, to: `/projects/${projectId.value}/git` },
  { name: 'graph', label: '协作图谱', icon: Share, to: `/projects/${projectId.value}/graph` },
  { name: 'contribution', label: '贡献分析', icon: DataAnalysis, to: `/projects/${projectId.value}/contribution` },
  { name: 'career', label: '成员画像', icon: Avatar, to: `/projects/${projectId.value}/career` },
  { name: 'risk', label: '风险预警', icon: Warning, to: `/projects/${projectId.value}/risk` },
  { name: 'audit', label: '过程审计', icon: Monitor, to: `/projects/${projectId.value}/audit` },
  { name: 'ai', label: 'AI 助手', icon: SetUp, to: `/projects/${projectId.value}/ai` },
  { name: 'settings', label: '项目设置', icon: SetUp, to: `/projects/${projectId.value}/settings` },
])

const pageLabel = computed(() => navItems.value.find((item) => item.name === route.name)?.label || '项目空间')
const filteredActions = computed(() => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return navItems.value
  return navItems.value.filter((item) => item.label.includes(keyword) || item.to.includes(keyword))
})

const bootstrap = async () => {
  await Promise.all([
    projectStore.fetchProject(projectId.value),
    notificationStore.fetchUnreadCount(),
  ])
}

const jumpTo = async (target: string) => {
  searchVisible.value = false
  await router.push(target)
}

const goReminders = async () => {
  await router.push(`/projects/${projectId.value}/reminders`)
}

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    userStore.logout()
    await router.push('/login')
    return
  }
  if (command === 'projects') {
    await router.push('/projects')
    return
  }
  if (command === 'settings') {
    await router.push(`/projects/${projectId.value}/settings`)
    return
  }
  if (command === 'reminders') {
    await goReminders()
    return
  }
  ElMessage.info('功能即将开放')
}

watch(projectId, bootstrap, { immediate: true })
onMounted(bootstrap)
</script>

<style scoped>
.project-layout {
  display: grid;
  height: 100%;
  grid-template-columns: 248px 1fr;
}

.sidebar {
  display: flex;
  flex-direction: column;
  padding: 14px 12px;
  gap: 12px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  place-items: center;
  background: linear-gradient(135deg, #5b7cfe 0%, #7158ff 100%);
}

.project-switch {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
}

.switch-icon {
  display: grid;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  place-items: center;
  color: white;
  background: linear-gradient(135deg, #4f6cf3 0%, #5440da 100%);
}

.switch-name {
  font-size: 14px;
  color: white;
}

.switch-status {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 6px;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
}

.sidebar-nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  gap: 4px;
}

.nav-item,
.reminder-shortcut {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 14px;
  color: rgba(226, 232, 240, 0.88);
  transition: 0.2s ease;
}

.nav-item {
  justify-content: flex-start;
}

.nav-item.active,
.nav-item:hover,
.reminder-shortcut.active,
.reminder-shortcut:hover {
  color: white;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(79, 70, 229, 0.9) 100%);
}

.reminder-shortcut b {
  display: grid;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  place-items: center;
  background: rgba(239, 68, 68, 0.92);
  font-size: 12px;
}

.sidebar-user {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
}

.sidebar-user img,
.topbar-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
}

.project-main {
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
}

.project-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 68px;
  padding: 0 22px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  background: rgba(255, 255, 255, 0.96);
}

.topbar-left,
.topbar-right,
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 14px;
}

.breadcrumb {
  color: var(--text-muted);
  font-size: 14px;
}

.topbar-right {
  gap: 18px;
}

.top-icon-btn {
  position: relative;
  color: var(--text);
}

.bell {
  position: relative;
}

.bell span {
  position: absolute;
  top: -7px;
  right: -10px;
  display: grid;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  place-items: center;
  background: var(--danger);
  color: white;
  font-size: 11px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.project-content {
  flex: 1;
  min-height: 0;
  padding: 18px;
  overflow: hidden;
}

.project-page-view {
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.search-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.search-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid #e6ecfb;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  text-align: left;
}
</style>
