<template>
  <div class="editor-page" v-if="document">
    <aside class="teamflow-card tree-pane">
      <div class="section-title">文档目录</div>
      <div class="search-box"><el-input placeholder="搜索文档标题"><template #prefix><el-icon><Search /></el-icon></template></el-input></div>
      <div class="tree-group">
        <div class="group-title">课程设计文档</div>
        <div class="tree-item" v-for="item in allDocuments" :key="item.id" :class="{ active: item.id === document.id }" @click="router.push(`/projects/${projectId}/documents/${item.id}`)">
          <el-icon><Document /></el-icon>
          <span class="text-truncate" style="flex: 1;">{{ item.title }}</span>
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
        <div class="toolbar-group">
          <el-tooltip content="撤销" placement="top"><el-icon><RefreshLeft /></el-icon></el-tooltip>
          <el-tooltip content="重做" placement="top"><el-icon><RefreshRight /></el-icon></el-tooltip>
        </div>
        <div class="toolbar-divider"></div>
        <div class="toolbar-group">
          <el-tooltip content="标题" placement="top"><div class="toolbar-btn text-icon">H1</div></el-tooltip>
          <el-tooltip content="副标题" placement="top"><div class="toolbar-btn text-icon">H2</div></el-tooltip>
          <el-tooltip content="正文" placement="top"><div class="toolbar-btn text-icon">P</div></el-tooltip>
        </div>
        <div class="toolbar-divider"></div>
        <div class="toolbar-group">
          <el-tooltip content="加粗" placement="top"><div class="toolbar-btn" style="font-weight: 800;">B</div></el-tooltip>
          <el-tooltip content="斜体" placement="top"><div class="toolbar-btn" style="font-style: italic;">I</div></el-tooltip>
          <el-tooltip content="下划线" placement="top"><div class="toolbar-btn" style="text-decoration: underline;">U</div></el-tooltip>
        </div>
        <div class="toolbar-divider"></div>
        <div class="toolbar-group">
          <el-tooltip content="插入图片" placement="top"><el-icon><Picture /></el-icon></el-tooltip>
          <el-tooltip content="插入链接" placement="top"><el-icon><Link /></el-icon></el-tooltip>
          <el-tooltip content="插入表格" placement="top"><el-icon><Grid /></el-icon></el-tooltip>
        </div>
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
import { Document, RefreshLeft, RefreshRight, Picture, Link, Grid, Search } from '@element-plus/icons-vue'
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
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
  color: #475569;
}
.tree-item:hover {
  background: #F1F5F9;
}
.tree-item.active {
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  color: var(--primary);
  font-weight: 600;
}
.tree-item .el-icon {
  font-size: 16px;
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
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: #F8FAFC;
  border-radius: 12px;
  margin: 16px 0;
  overflow-x: auto;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #64748B;
  font-size: 18px;
}
.toolbar-group .el-icon, .toolbar-btn {
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toolbar-group .el-icon:hover, .toolbar-btn:hover {
  background: #E2E8F0;
  color: var(--primary);
}
.toolbar-divider {
  width: 1px;
  height: 20px;
  background: #E2E8F0;
}
.text-icon { font-size: 14px; font-weight: 700; width: 28px; height: 28px; }

.editor-content {
  flex: 1;
  min-height: 0;
  padding: 24px 40px;
  margin: 0 auto;
  max-width: 800px;
  width: 100%;
}

.title-input {
  margin-bottom: 18px;
}

.title-input :deep(.el-input__wrapper) {
  box-shadow: none !important;
  background: transparent;
  padding: 0;
}
.title-input :deep(input) {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  border: none;
  height: auto;
  line-height: 1.2;
}

.editor-content :deep(.el-textarea__inner) {
  box-shadow: none !important;
  background: transparent;
  padding: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #334155;
  border: none;
}

.comment-list,
.version-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item {
  padding: 16px;
  background: #F8FAFC;
  border: 1px solid rgba(15,23,42,0.04);
  border-radius: 14px;
  transition: all 0.2s;
}
.comment-item:hover {
  border-color: rgba(99,102,241,0.2);
  box-shadow: 0 4px 12px rgba(99,102,241,0.05);
}

.version-item {
  padding: 16px;
  background: #FFFFFF;
  border: 1px solid rgba(15,23,42,0.06);
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.02);
  border-left: 4px solid var(--primary);
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
