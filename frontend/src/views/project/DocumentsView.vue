<template>
  <div class="documents-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">文档协作</h1>
        <div class="page-desc">沉淀需求、设计、接口和会议纪要，持续留下版本证据</div>
      </div>
      <el-button type="primary" @click="createDocument">新建文档</el-button>
    </div>

    <div class="teamflow-card doc-list-panel">
      <div v-for="item in documents" :key="item.id" class="doc-row" @click="router.push(`/projects/${projectId}/documents/${item.id}`)">
        <div>
          <div class="doc-title">{{ item.title }}</div>
          <div class="doc-meta">{{ item.author?.name }} · {{ item.updated_at }} · {{ item.version_count }} 个版本</div>
        </div>
        <div class="doc-tags">
          <span v-for="tag in item.tags" :key="tag" class="status-tag blue">{{ tag }}</span>
          <span class="status-tag green">{{ item.permission_status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { documentApi } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const documents = ref<any[]>([])

const load = async () => {
  const { data } = await documentApi.list(projectId.value)
  documents.value = data
}

const createDocument = async () => {
  const { data } = await documentApi.create(projectId.value, {
    title: `新建文档 ${documents.value.length + 1}`,
    content: '# 新建文档\n\n请在这里开始编辑内容。',
    tags: ['协作'],
  })
  ElMessage.success('文档已创建')
  router.push(`/projects/${projectId.value}/documents/${data.id}`)
}

onMounted(load)
</script>

<style scoped>
.documents-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row,
.doc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.doc-list-panel {
  padding: 16px 18px;
}

.doc-row {
  padding: 18px 16px;
  border: 1px solid #edf1ff;
  border-radius: 16px;
  cursor: pointer;
}

.doc-row + .doc-row {
  margin-top: 14px;
}

.doc-title {
  font-size: 18px;
  font-weight: 700;
}

.doc-meta {
  margin-top: 8px;
  color: var(--text-muted);
}

.doc-tags {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .header-row,
  .doc-row {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .doc-tags {
    flex-wrap: wrap;
  }
}
</style>
