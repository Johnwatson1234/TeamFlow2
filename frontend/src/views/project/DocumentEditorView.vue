<template>
  <div class="editor-page" v-if="document">
    <aside class="teamflow-card tree-pane">
      <div class="section-title">文档目录</div>
      <div class="search-box"><el-input placeholder="搜索文档标题" /></div>
      <div class="tree-group">
        <div class="group-title">课程设计文档</div>
        <div class="tree-item" v-for="item in allDocuments" :key="item.id" :class="{ active: item.id === document.id }" @click="router.push(`/projects/${projectId}/documents/${item.id}`)">
          {{ item.title }}
        </div>
      </div>
    </aside>

    <section class="teamflow-card editor-pane">
      <div class="editor-head">
        <div>
          <div class="thread-title">{{ document.title }}</div>
          <div class="page-desc">自动保存成功 · {{ document.updated_at }}</div>
        </div>
        <div class="editor-actions">
          <el-button @click="saveVersion">历史版本</el-button>
          <el-button @click="exportDoc">导出</el-button>
          <el-button type="primary" @click="shareDoc">分享</el-button>
        </div>
      </div>
      <div class="toolbar">
        <span>文件</span>
        <span>编辑</span>
        <span>插入</span>
        <span>格式</span>
        <span>视图</span>
        <span>表格</span>
        <span>帮助</span>
      </div>
      <div class="editor-content">
        <el-input v-model="document.title" class="title-input" />
        <el-input v-model="document.content" :rows="24" resize="none" type="textarea" />
      </div>
      <div class="editor-footer">
        <span>字数：{{ document.content?.length || 0 }}</span>
        <span>正在编辑：{{ document.updated_by?.name }}</span>
      </div>
    </section>

    <aside class="teamflow-card side-pane">
      <el-tabs v-model="tab">
        <el-tab-pane label="评论" name="comments">
          <div class="comment-list">
            <div v-for="item in comments" :key="item.author + item.time" class="comment-item">
              <div class="comment-head">
                <strong>{{ item.author }}</strong>
                <span class="tiny-muted">{{ item.time }}</span>
              </div>
              <div>{{ item.content }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="版本记录" name="versions">
          <div class="version-list">
            <div v-for="item in versions" :key="item.id" class="version-item">
              <div class="version-top">
                <span>{{ item.version_label }}</span>
                <span class="status-tag green" v-if="item.version_label === versions[0]?.version_label">当前版本</span>
              </div>
              <div class="tiny-muted">{{ item.author?.name }} · {{ item.created_at }}</div>
              <div class="page-desc">{{ item.summary }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { documentApi } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id as string)
const docId = computed(() => route.params.docId as string)
const document = ref<any>(null)
const allDocuments = ref<any[]>([])
const versions = ref<any[]>([])
const tab = ref('comments')

const comments = ref([
  { author: '李四', time: '05-18 15:20', content: '建议在此处补充系统部署架构图。' },
  { author: '王五', time: '05-18 14:10', content: '功能模块表格中，文档协作模块的功能描述是否需要细化？' },
  { author: '赵六', time: '05-17 22:05', content: '外部服务建议补充 Git 仓库与消息服务说明。' },
])

const load = async () => {
  const [docRes, listRes, versionRes] = await Promise.all([
    documentApi.detail(docId.value),
    documentApi.list(projectId.value),
    documentApi.versions(docId.value),
  ])
  document.value = docRes.data
  allDocuments.value = listRes.data
  versions.value = versionRes.data
}

const saveVersion = async () => {
  await documentApi.createVersion(docId.value, {
    summary: '手动保存版本',
    content: document.value.content,
  })
  ElMessage.success('版本已保存')
  await load()
}

const exportDoc = () => ElMessage.success('已模拟导出文档')
const shareDoc = () => ElMessage.success('已复制分享链接（模拟）')

watch(docId, load, { immediate: true })
onMounted(load)
</script>

<style scoped>
.editor-page {
  display: grid;
  gap: 18px;
  height: 100%;
  min-height: 0;
  grid-template-columns: 260px 1fr 320px;
}

.tree-pane,
.editor-pane,
.side-pane {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 18px;
}

.tree-group {
  margin-top: 18px;
}

.group-title {
  margin-bottom: 10px;
  color: var(--text-muted);
}

.tree-item {
  padding: 12px 14px;
  border-radius: 12px;
  cursor: pointer;
}

.tree-item.active {
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
  font-weight: 700;
}

.editor-head,
.editor-actions,
.editor-footer,
.comment-head,
.version-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar {
  display: flex;
  gap: 22px;
  padding: 14px 0;
  border-top: 1px solid #eef2ff;
  border-bottom: 1px solid #eef2ff;
  color: var(--text-muted);
}

.editor-content {
  flex: 1;
  min-height: 0;
  padding: 18px 0;
}

.title-input {
  margin-bottom: 18px;
}

.comment-list,
.version-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item,
.version-item {
  padding: 14px;
  border: 1px solid #eef2ff;
  border-radius: 14px;
}

@media (max-width: 1200px) {
  .editor-page {
    height: auto;
    grid-template-columns: 220px 1fr;
  }

  .side-pane {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .editor-page {
    grid-template-columns: 1fr;
  }

  .editor-head,
  .editor-actions,
  .editor-footer,
  .version-top {
    align-items: flex-start;
    gap: 10px;
    flex-direction: column;
  }

  .toolbar {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
