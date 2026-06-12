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
          <el-button class="mobile-nav-trigger" circle text @click="mobileNavVisible = true">
            <el-icon :size="18"><Operation /></el-icon>
          </el-button>
          <el-icon :size="20"><Operation /></el-icon>
          <div class="breadcrumb">
            <span class="crumb-link" @click="router.push('/projects')">项目空间</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-link" @click="router.push(`/projects/${projectId}`)">{{ currentProject?.name || '加载中...' }}</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ pageLabel }}</span>
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
    <el-dialog v-model="searchVisible" title="快速搜索与跳转" width="min(560px, 92vw)">
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
    <el-drawer v-model="mobileNavVisible" class="mobile-nav-drawer" direction="ltr" size="280px">
      <template #header>
        <div class="mobile-drawer-head">
          <div class="brand-mark">⬡</div>
          <div>
            <div class="brand-name">TeamFlow</div>
            <div class="tiny-muted">{{ currentProject?.name }}</div>
          </div>
        </div>
      </template>
      <nav class="mobile-nav-list">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="mobile-nav-item"
          :class="{ active: route.name === item.name }"
          @click="mobileNavVisible = false"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </el-drawer>
  </AppViewport>
  <AIAssistantDock v-if="projectId" />
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
import AIAssistantDock from '@/components/common/AIAssistantDock.vue'
import { useNotificationStore } from '@/stores/notification'
import { useAiStore } from '@/stores/ai'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const notificationStore = useNotificationStore()
const userStore = useUserStore()
const aiStore = useAiStore()
const searchVisible = ref(false)
const searchKeyword = ref('')
const mobileNavVisible = ref(false)

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
watch(() => route.fullPath, () => {
  mobileNavVisible.value = false
  aiStore.setPageContext({
    routeName: String(route.name || ''),
    query: JSON.stringify(route.query),
  })
})
onMounted(bootstrap)
</script>

<style scoped>
.project-layout {
  display: grid;
  min-height: 100dvh;
  grid-template-columns: 248px 1fr;
  background: var(--bg);
}

.sidebar {
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  gap: 12px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  border-right: 1px solid var(--sidebar-border);
  box-shadow: 1px 0 10px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 10;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  padding: 0 8px;
  letter-spacing: -0.01em;
}

.brand-mark {
  display: grid;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  place-items: center;
  background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%);
  color: #fff;
  font-weight: 800;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.3);
}

.project-switch {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-switch:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
}

.switch-icon {
  display: grid;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  place-items: center;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.switch-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.switch-status {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
  color: var(--sidebar-text);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
}

.sidebar-nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  gap: 2px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}
.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }

.nav-item,
.reminder-shortcut {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--sidebar-text);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-item {
  justify-content: flex-start;
}

.nav-item.active,
.reminder-shortcut.active {
  color: var(--sidebar-text-active);
  background: var(--sidebar-item-active-bg);
  box-shadow: inset 2px 0 0 var(--primary-light);
}

.nav-item:hover:not(.active),
.reminder-shortcut:hover:not(.active) {
  color: #fff;
  background: var(--sidebar-item-hover);
}

.nav-item .el-icon {
  font-size: 16px;
  opacity: 0.8;
}

.nav-item.active .el-icon {
  opacity: 1;
  color: var(--primary-light);
}

.reminder-shortcut b {
  display: grid;
  width: 22px;
  height: 22px;
  border-radius: 11px;
  place-items: center;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.sidebar-user {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-user:hover {
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-user img,
.topbar-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-name {
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.project-main {
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  position: relative;
}

.project-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 9;
}

.topbar-left,
.topbar-right,
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-nav-trigger {
  display: none;
}

.breadcrumb {
  display: flex;
  align-items: center;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
}

.crumb-link {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.crumb-link:hover {
  color: var(--primary);
  background: rgba(79, 70, 229, 0.08);
}

.crumb-sep {
  margin: 0 2px;
  opacity: 0.5;
}

.crumb-current {
  color: var(--text);
  font-weight: 600;
  padding: 4px 8px;
}

.topbar-right {
  gap: 12px;
}

.top-icon-btn {
  position: relative;
  color: var(--text-muted);
  transition: all 0.2s;
}

.top-icon-btn:hover {
  color: var(--text);
  background: rgba(0, 0, 0, 0.04);
}

.bell {
  position: relative;
}

.bell span {
  position: absolute;
  top: -4px;
  right: -4px;
  display: grid;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  place-items: center;
  background: var(--danger);
  color: white;
  font-size: 10px;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 999px;
  transition: background 0.2s;
}

.user-trigger:hover {
  background: rgba(0, 0, 0, 0.04);
}

.topbar-user {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.project-content {
  flex: 1;
  min-height: 0;
  padding: 24px;
  overflow: auto;
}

.project-page-view {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100%;
  overflow: visible;
  animation: fade-in-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.search-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.search-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.search-action:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.search-action strong {
  font-size: 14px;
  color: var(--text);
}

.mobile-drawer-head,
.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-nav-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-nav-item {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-weight: 500;
}

.mobile-nav-item.active {
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
  font-weight: 600;
}

@media (max-width: 1024px) {
  .project-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }

  .mobile-nav-trigger {
    display: inline-flex;
  }

  .project-topbar {
    height: 60px;
    padding: 0 16px;
  }

  .project-content {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .project-topbar {
    height: auto;
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .topbar-left {
    width: 100%;
  }

  .topbar-right {
    width: 100%;
    justify-content: flex-end;
  }

  .topbar-user {
    display: none;
  }

  .project-content {
    padding: 12px;
  }
}
</style>
