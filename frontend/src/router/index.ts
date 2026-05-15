import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/projects',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { public: true },
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/projects/ProjectListView.vue'),
    },
    {
      path: '/projects/:id',
      component: () => import('@/layouts/ProjectLayout.vue'),
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/project/DashboardView.vue') },
        { path: 'tasks', name: 'tasks', component: () => import('@/views/project/TasksView.vue') },
        { path: 'milestones', name: 'milestones', component: () => import('@/views/project/MilestonesView.vue') },
        { path: 'messages', name: 'messages', component: () => import('@/views/project/MessagesView.vue') },
        { path: 'documents', name: 'documents', component: () => import('@/views/project/DocumentsView.vue') },
        { path: 'documents/:docId', name: 'document-editor', component: () => import('@/views/project/DocumentEditorView.vue') },
        { path: 'files', name: 'files', component: () => import('@/views/project/FilesView.vue') },
        { path: 'graph', name: 'graph', component: () => import('@/views/project/GraphView.vue') },
        { path: 'contribution', name: 'contribution', component: () => import('@/views/project/ContributionView.vue') },
        { path: 'risk', name: 'risk', component: () => import('@/views/project/RiskView.vue') },
        { path: 'git', name: 'git', component: () => import('@/views/project/GitView.vue') },
        { path: 'ai', name: 'ai', component: () => import('@/views/project/AIView.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/project/SettingsView.vue') },
        { path: 'reminders', name: 'reminders', component: () => import('@/views/project/RemindersView.vue') },
        { path: 'audit', name: 'audit', component: () => import('@/views/project/AuditView.vue') },
      ],
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const store = useUserStore()
  if (store.token && !store.user) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
    }
  }
  if (!to.meta.public && !store.token) {
    return '/login'
  }
  if ((to.name === 'login' || to.name === 'register') && store.token) {
    return '/projects'
  }
  return true
})

export default router
