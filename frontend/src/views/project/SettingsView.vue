<template>
  <div class="settings-page">
    <div class="header-row">
      <div>
        <h1 class="page-title">项目设置</h1>
        <div class="page-desc">配置项目基础信息与成员协作，管理项目空间的各项参数与权限</div>
      </div>
      <el-button type="primary" @click="save">保存设置</el-button>
    </div>

    <div class="settings-grid">
      <div class="teamflow-card panel">
        <div class="section-title">项目信息</div>
        <el-form :model="form" label-position="top">
          <el-form-item label="项目名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="课程名称"><el-input v-model="form.course_name" /></el-form-item>
          <el-form-item label="项目简介"><el-input v-model="form.description" rows="4" type="textarea" /></el-form-item>
          <div class="grid-2">
            <el-form-item label="开始日期"><el-input v-model="form.start_date" /></el-form-item>
            <el-form-item label="截止日期"><el-input v-model="form.due_date" /></el-form-item>
          </div>
          <el-form-item label="代码仓库绑定"><el-input v-model="form.repo_url" /></el-form-item>
        </el-form>
      </div>

      <div class="teamflow-card panel">
        <div class="section-title">成员管理</div>
        <div class="member-row" v-for="member in members" :key="member.user_id">
          <div class="member-info">
            <img :src="member.avatar" alt="avatar" />
            <div>
              <div>{{ member.name }}</div>
              <div class="tiny-muted">{{ member.email }}</div>
            </div>
          </div>
          <span class="status-tag blue">{{ member.role }}</span>
          <span>{{ member.workload }}%</span>
          <span class="status-tag green">{{ member.online_status }}</span>
        </div>
      </div>

      <div class="teamflow-card panel">
        <div class="section-title">邀请成员</div>
        <el-form :model="inviteForm" label-position="top">
          <el-form-item label="搜索用户">
            <el-select v-model="inviteForm.invitee_id" filterable remote :remote-method="searchUsers" style="width: 100%">
              <el-option v-for="user in searchResults" :key="user.id" :label="`${user.display_name} (${user.email})`" :value="user.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="inviteForm.role"><el-option label="成员" value="成员" /><el-option label="前端开发" value="前端开发" /><el-option label="后端开发" value="后端开发" /></el-select>
          </el-form-item>
          <el-form-item label="邀请说明">
            <el-input v-model="inviteForm.message" rows="4" type="textarea" />
          </el-form-item>
          <el-button type="primary" @click="sendInvitation">发送邀请</el-button>
        </el-form>
      </div>

      <div class="teamflow-card panel">
        <div class="section-title">邀请记录</div>
        <div class="invite-row" v-for="item in invitations" :key="item.id">
          <div>
            <div>{{ item.invitee?.name }}</div>
            <div class="tiny-muted">{{ item.created_at }}</div>
          </div>
          <span :class="['status-tag', item.status === 'pending' ? 'orange' : item.status === 'accepted' ? 'green' : 'red']">{{ item.status }}</span>
        </div>
      </div>
    </div>

    <div class="teamflow-card panel">
      <div class="section-title">成员协作权限矩阵</div>
      <el-table :data="permissionRows">
        <el-table-column label="角色" prop="role" />
        <el-table-column label="邀请成员" prop="invite" />
        <el-table-column label="分配任务" prop="assign" />
        <el-table-column label="查看审计" prop="audit" />
        <el-table-column label="导出报告" prop="report" />
        <el-table-column label="删除内容" prop="delete" />
        <el-table-column label="项目设置" prop="settings" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { authApi, projectApi } from '@/api'
import { useProjectStore } from '@/stores/project'

const route = useRoute()
const projectStore = useProjectStore()
const projectId = computed(() => route.params.id as string)
const members = ref<any[]>([])
const invitations = ref<any[]>([])
const searchResults = ref<any[]>([])
const form = reactive<any>({
  name: '',
  course_name: '',
  description: '',
  start_date: '',
  due_date: '',
  repo_url: '',
  advisor_name: '',
  advisor_email: '',
  category: '课程设计',
  tags: ['课程设计'],
})
const inviteForm = reactive({
  invitee_id: null as number | null,
  role: '成员',
  message: '',
})

const permissionRows = [
  { role: '组长（Leader）', invite: '√', assign: '√', audit: '√', report: '√', delete: '√', settings: '√' },
  { role: '成员（Member）', invite: '—', assign: '√', audit: '√', report: '√', delete: '—', settings: '—' },
  { role: '教师（Teacher）', invite: '—', assign: '—', audit: '√', report: '√', delete: '—', settings: '√' },
]

const load = async () => {
  const [detailRes, memberRes, inviteRes] = await Promise.all([
    projectApi.detail(projectId.value),
    projectApi.members(projectId.value),
    projectApi.invitations(projectId.value),
  ])
  Object.assign(form, detailRes.data)
  members.value = memberRes.data
  invitations.value = inviteRes.data
}

const searchUsers = async (keyword: string) => {
  const { data } = await authApi.searchUsers(keyword)
  searchResults.value = data
}

const sendInvitation = async () => {
  if (!inviteForm.invitee_id) return
  await projectApi.sendInvitation(projectId.value, inviteForm)
  ElMessage.success('邀请已发送')
  inviteForm.invitee_id = null
  inviteForm.message = ''
  await load()
}

const save = async () => {
  await projectApi.update(projectId.value, form)
  await projectStore.fetchProject(projectId.value)
  ElMessage.success('设置已保存')
}

onMounted(load)
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-row,
.member-row,
.member-info,
.invite-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.settings-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: 1.05fr 1fr;
}

.panel {
  padding: 18px;
}

.member-row,
.invite-row {
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}

.member-info {
  gap: 12px;
}

.member-info img {
  width: 42px;
  height: 42px;
  border-radius: 50%;
}

@media (max-width: 1200px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-row,
  .member-row,
  .invite-row {
    align-items: flex-start;
    gap: 10px;
    flex-direction: column;
  }
}
</style>
