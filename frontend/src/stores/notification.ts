import { defineStore } from 'pinia'

import { notificationApi, projectApi } from '@/api'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as any[],
    unreadCount: 0,
    myInvitations: [] as any[],
    myTasks: [] as any[],
  }),
  actions: {
    async fetchNotifications() {
      const { data } = await notificationApi.list()
      this.notifications = data
      return data
    },
    async fetchUnreadCount() {
      const { data } = await notificationApi.unreadCount()
      this.unreadCount = data.count
      return data.count
    },
    async markAllRead() {
      await notificationApi.readAll()
      await this.fetchUnreadCount()
      await this.fetchNotifications()
    },
    async fetchInvitations() {
      const { data } = await projectApi.myInvitations()
      this.myInvitations = data
      return data
    },
  },
})
