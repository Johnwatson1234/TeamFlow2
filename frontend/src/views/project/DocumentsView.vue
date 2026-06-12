<template>
  <div class="documents-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">文档协作</h1>
        <div class="page-desc">沉淀需求、设计、接口和会议纪要，持续留下版本证据</div>
      </div>
      <el-button type="primary" @click="createDocument">新建文档</el-button>
    </div>

    <div class="doc-grid">
      <div v-for="(item, index) in documents" :key="item.id" class="teamflow-card doc-card" @click="router.push(`/projects/${projectId}/documents/${item.id}`)">
        <div class="doc-cover" :style="{ background: getDocCover(index) }">
          <el-icon :size="36"><Document /></el-icon>
        </div>
        <div class="doc-content">
          <div class="doc-title">{{ item.title }}</div>
          <div class="doc-meta">
            <img class="author-avatar" :src="item.author?.avatar || 'https://api.dicebear.com/7.x/notionists/svg?seed=Doc' + index" alt="avatar" />
            <span>{{ item.author?.name || '成员' }}</span>
            <span class="dot">·</span>
            <span>{{ item.updated_at?.slice(0, 10) || '今日更新' }}</span>
          </div>
          <div class="doc-tags">
            <span v-for="tag in item.tags" :key="tag" class="status-tag blue">{{ tag }}</span>
            <span class="status-tag purple">{{ item.version_count || 1 }} 版本</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { documentApi } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const documents = ref<any[]>([])

const getDocCover = (index: number) => {
  const gradients = [
    'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
    'linear-gradient(135deg, #34D399 0%, #059669 100%)',
    'linear-gradient(135deg, #F472B6 0%, #DB2777 100%)',
    'linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)',
    'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)'
  ]
  return gradients[index % gradients.length]
}

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
  gap: 24px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.doc-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.doc-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(15, 23, 42, 0.06);
}

.doc-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(79, 70, 229, 0.3);
}

.doc-cover {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0.95;
}

.doc-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.doc-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 13px;
}

.dot {
  color: var(--border);
}

.doc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

@media (max-width: 768px) {
  .header-row {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }
}
</style>
