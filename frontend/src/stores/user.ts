import { defineStore } from 'pinia'

import { authApi } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('teamflow-token') || '',
    user: null as null | Record<string, any>,
    loading: false,
  }),
  actions: {
    async login(payload: { username: string; password: string }) {
      const { data } = await authApi.login(payload)
      this.token = data.token
      this.user = data.user
      localStorage.setItem('teamflow-token', data.token)
    },
    async register(payload: { username: string; password: string; display_name: string; email: string }) {
      const { data } = await authApi.register(payload)
      this.token = data.token
      this.user = data.user
      localStorage.setItem('teamflow-token', data.token)
    },
    async fetchMe() {
      if (!this.token) return
      const { data } = await authApi.me()
      this.user = data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('teamflow-token')
    },
  },
})
