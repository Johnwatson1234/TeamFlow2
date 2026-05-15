<template>
  <div class="files-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">文件共享与资料评审</h1>
        <div class="page-desc">共享项目资料、关联任务与版本评论，让评审状态一目了然</div>
      </div>
    </div>
    <section class="grid-4">
      <StatCard title="文件总数" :value="files.length" footer="较上周 ↓ 6" :icon="FolderOpened" tint="rgba(139,92,246,.12)" icon-color="#8b5cf6" />
      <StatCard title="待评审资料" :value="pendingCount" footer="较上周 ↑ 3" :icon="Clock" tint="rgba(245,158,11,.12)" icon-color="#f59e0b" />
      <StatCard title="近 7 天上传" :value="36" footer="较上周 ↓ 4" :icon="UploadFilled" tint="rgba(34,197,94,.12)" icon-color="#22c55e" />
      <StatCard title="存储空间使用" value="2.34 GB / 10 GB" footer="23%" :icon="PieChart" tint="rgba(59,130,246,.12)" icon-color="#3b82f6" />
    </section>

    <div class="files-layout">
      <div class="teamflow-card file-table-panel">
        <el-table :data="filteredFiles" @row-click="selectFile">
          <el-table-column label="文件名称" prop="name" min-width="240" />
          <el-table-column label="类型" prop="file_type" width="120" />
          <el-table-column label="关联任务" prop="related_task" width="140" />
          <el-table-column label="上传者" width="120">
            <template #default="{ row }">{{ row.uploader?.name }}</template>
          </el-table-column>
          <el-table-column label="版本" prop="version_label" width="100" />
          <el-table-column label="最后更新" prop="updated_at" width="180" />
          <el-table-column label="评审状态" width="120">
            <template #default="{ row }">
              <span :class="['status-tag', row.review_status === '已通过' ? 'green' : row.review_status === '待评审' ? 'orange' : 'red']">{{ row.review_status }}</span>
            </template>
          </el-table-column>
          <el-table-column label="下载次数" prop="download_count" width="110" />
        </el-table>

        <div class="file-bottom-grid">
          <div class="teamflow-card mini-card">
            <div class="section-title">文件夹</div>
            <button
              v-for="name in folderNames"
              :key="name"
              :class="['folder-item', { active: activeFolder === name }]"
              type="button"
              @click="activeFolder = name"
            >
              {{ name }}
            </button>
          </div>
          <div class="teamflow-card mini-card">
            <div class="section-title">上传文件</div>
            <div class="upload-box">
              <el-upload :auto-upload="false" :before-upload="beforeUpload" :on-change="handleUpload" drag :show-file-list="false">
                <div class="tiny-muted">点击或拖拽文件到此处上传</div>
              </el-upload>
            </div>
          </div>
          <div class="teamflow-card mini-card">
            <div class="section-title">评审流程</div>
            <div class="review-track">
              <div class="review-node done">已上传</div>
              <div class="review-node waiting">待评审</div>
              <div class="review-node">已通过</div>
              <div class="review-node">退回修改</div>
            </div>
          </div>
        </div>
      </div>

      <aside class="teamflow-card file-preview" v-if="selectedFile">
        <div class="section-title">文件预览</div>
        <div class="preview-name">{{ selectedFile.name }}</div>
        <div class="status-tag green">{{ selectedFile.review_status }}</div>
        <div class="preview-grid">
          <div><label>上传者</label><span>{{ selectedFile.uploader?.name }}</span></div>
          <div><label>上传时间</label><span>{{ selectedFile.updated_at }}</span></div>
          <div><label>关联任务</label><span>{{ selectedFile.related_task }}</span></div>
          <div><label>存储位置</label><span>{{ selectedFile.storage_path }}</span></div>
        </div>
        <p class="page-desc">{{ selectedFile.description }}</p>
        <div class="comment-list">
          <div v-for="item in selectedFile.comments" :key="item.author + item.time" class="comment-item">
            <strong>{{ item.author }}</strong>
            <div class="tiny-muted">{{ item.time }}</div>
            <div>{{ item.content }}</div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock, FolderOpened, PieChart, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fileApi } from '@/api'
import StatCard from '@/components/common/StatCard.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const files = ref<any[]>([])
const selectedFile = ref<any>(null)
const activeFolder = ref('需求文档')
const folderNames = ['需求文档', '设计文档', '开发资料', '测试报告', '演示资料']
const pendingCount = computed(() => files.value.filter((item) => item.review_status === '待评审').length)
const folderCategoryMap: Record<string, string[]> = {
  需求文档: ['需求'],
  设计文档: ['设计', '数据库'],
  开发资料: ['接口', '代码', '计划'],
  测试报告: ['测试'],
  演示资料: ['演示', '视频'],
}
const filteredFiles = computed(() => {
  const categories = folderCategoryMap[activeFolder.value] || []
  const rows = files.value.filter((item) => categories.includes(item.category))
  return rows.length ? rows : files.value
})

const load = async () => {
  const { data } = await fileApi.list(projectId.value)
  files.value = data
  selectedFile.value = data[0] || null
}

const selectFile = (row: any) => {
  selectedFile.value = row
}

const beforeUpload = () => false

const handleUpload = async (uploadFile: any) => {
  if (!uploadFile.raw) {
    ElMessage.warning('没有检测到可上传的文件')
    return
  }
  const formData = new FormData()
  formData.append('upload', uploadFile.raw)
  formData.append('category', folderCategoryMap[activeFolder.value]?.[0] || '其他')
  formData.append('related_task', selectedFile.value?.related_task || '')
  await fileApi.upload(projectId.value, formData)
  ElMessage.success('文件上传成功')
  await load()
}

watch(filteredFiles, (rows) => {
  if (!rows.length) {
    selectedFile.value = null
    return
  }
  if (!selectedFile.value || !rows.some((item) => item.id === selectedFile.value.id)) {
    selectedFile.value = rows[0]
  }
})

onMounted(load)
</script>

<style scoped>
.files-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.files-layout {
  display: grid;
  gap: 18px;
  grid-template-columns: 1fr 320px;
}

.file-table-panel,
.file-preview,
.mini-card {
  padding: 18px;
}

.file-bottom-grid {
  display: grid;
  gap: 16px;
  margin-top: 18px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.folder-item {
  display: block;
  width: 100%;
  padding: 10px 0;
  border: 0;
  border-bottom: 1px solid #f1f5f9;
  background: transparent;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.folder-item.active {
  color: var(--primary);
  font-weight: 700;
}

.upload-box {
  margin-top: 14px;
}

.review-track {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.review-node {
  padding: 10px 12px;
  border-radius: 12px;
  background: #f8fafc;
}

.review-node.done {
  color: var(--success);
}

.review-node.waiting {
  color: var(--warning);
}

.preview-name {
  margin: 16px 0 10px;
  font-size: 22px;
  font-weight: 700;
}

.preview-grid {
  display: grid;
  gap: 12px;
  margin: 16px 0;
}

.preview-grid label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-muted);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  padding: 12px;
  border: 1px solid #eef2ff;
  border-radius: 14px;
}
</style>
