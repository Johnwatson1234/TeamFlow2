import { defineStore } from 'pinia'

export const useAiStore = defineStore('ai', {
  state: () => ({
    pageContext: {} as Record<string, unknown>,
    latestActionResults: [] as any[],
  }),
  actions: {
    setPageContext(context: Record<string, unknown>) {
      this.pageContext = { ...context }
    },
    mergePageContext(context: Record<string, unknown>) {
      this.pageContext = { ...this.pageContext, ...context }
    },
    resetPageContext() {
      this.pageContext = {}
    },
    setLatestActionResults(results: any[]) {
      this.latestActionResults = results
    },
  },
})
