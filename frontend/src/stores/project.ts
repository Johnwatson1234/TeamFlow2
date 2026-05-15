import { defineStore } from 'pinia'

import { projectApi } from '@/api'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [] as any[],
    currentProject: null as any,
    dashboard: null as any,
  }),
  actions: {
    async fetchProjects() {
      const { data } = await projectApi.list()
      this.projects = data
      return data
    },
    async fetchProject(id: string | number) {
      const { data } = await projectApi.detail(id)
      this.currentProject = data
      return data
    },
    async fetchDashboard(id: string | number) {
      const { data } = await projectApi.dashboard(id)
      this.dashboard = data
      return data
    },
  },
})
