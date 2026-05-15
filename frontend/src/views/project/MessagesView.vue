<template>
  <div class="messages-page" v-loading="loading">
    <aside class="teamflow-card conversation-pane">
      <div class="pane-header">
        <h2 class="section-title">会话列表</h2>
        <el-button type="primary" plain @click="createDialog = true">新建会话</el-button>
      </div>
      <div class="conversation-tabs">
        <button
          v-for="item in conversationTabItems"
          :key="item.key"
          :class="['tab-button', { active: conversationFilter === item.key }]"
          type="button"
          @click="conversationFilter = item.key"
        >
          {{ item.label }}
        </button>
      </div>
      <div class="conversation-list app-scroll">
        <div
          v-for="item in filteredConversations"
          :key="item.id"
          class="conversation-item"
          :class="{ active: item.id === currentConversation?.id }"
          @click="selectConversation(item)"
        >
          <div class="conversation-icon">{{ item.conversation_type === 'project_group' ? '👥' : item.conversation_type === 'system' ? '🔔' : '✅' }}</div>
          <div class="conversation-body">
            <div class="conversation-top">
              <div>{{ item.name }}</div>
              <span class="tiny-muted">{{ item.latest_message?.created_at?.slice(11, 16) }}</span>
            </div>
            <div class="tiny-muted">{{ item.latest_message?.content || '暂无消息' }}</div>
          </div>
          <div class="conversation-badge" v-if="item.unread_count">{{ item.unread_count }}</div>
        </div>
        <div v-if="!filteredConversations.length" class="list-empty tiny-muted">
          当前筛选下暂无会话
        </div>
      </div>
    </aside>

    <section class="teamflow-card thread-pane" v-if="currentConversation">
      <div class="thread-header">
        <div>
          <div class="thread-title">{{ currentConversation.name }}</div>
          <div class="page-desc">
            <span v-if="thread.task_context">任务负责人：{{ thread.task_context.assignee?.name || '待分配' }}</span>
            <span v-if="thread.task_context">截止日期：{{ thread.task_context.due_date }}</span>
          </div>
        </div>
        <div class="thread-header-actions">
          <el-button text @click="toggleLaterConversation">
            {{ isCurrentMarkedLater ? '取消稍后处理' : '稍后处理' }}
          </el-button>
          <el-button v-if="thread.task_context" type="primary" plain @click="openTask(thread.task_context.id)">
            查看任务
          </el-button>
        </div>
      </div>
      <div class="thread-messages app-scroll">
        <div v-for="message in thread.messages" :key="message.id" class="message-row" :class="{ mine: message.sender?.id === userStore.user?.id }">
          <img :src="message.sender?.avatar" alt="avatar" />
          <div class="message-content">
            <div class="message-meta">
              <strong>{{ message.sender?.name }}</strong>
              <span class="tiny-muted">{{ message.created_at?.slice(11, 16) }}</span>
            </div>
            <div v-if="message.message_type === 'code'" class="code-block">{{ message.content }}</div>
            <div v-else-if="message.message_type === 'file'" class="file-block">{{ message.content }}</div>
            <div
              v-else-if="message.message_type === 'task'"
              class="task-block"
              @click="openReferencedTask(message)"
            >
              {{ message.content }}
            </div>
            <div v-else class="text-bubble">{{ message.content }}</div>
          </div>
        </div>
      </div>
      <div class="message-editor">
        <div class="editor-tabs">
          <button
            v-for="item in editorModeItems"
            :key="item.key"
            :class="['tab-button', { active: editorMode === item.key }]"
            type="button"
            @click="editorMode = item.key"
          >
            {{ item.label }}
          </button>
        </div>
        <div v-if="editorMode === 'task'" class="task-reference-bar">
          <el-select v-model="taskReferenceId" filterable placeholder="选择要引用的任务">
            <el-option v-for="task in taskOptions" :key="task.id" :label="`#${task.id} ${task.title}`" :value="task.id" />
          </el-select>
          <el-button plain @click="fillTaskReference">插入任务引用</el-button>
        </div>
        <div v-if="editorMode === 'code'" class="task-reference-bar">
          <el-select v-model="codeLanguage" placeholder="代码语言">
            <el-option label="Java" value="Java" />
            <el-option label="TypeScript" value="TypeScript" />
            <el-option label="Python" value="Python" />
            <el-option label="SQL" value="SQL" />
          </el-select>
          <el-button plain @click="insertCodeTemplate">插入代码模板</el-button>
        </div>
        <el-input
          v-model="messageForm.content"
          :placeholder="composerPlaceholder"
          :rows="4"
          type="textarea"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="editor-actions">
          <div class="tiny-muted">{{ editorHelperText }}</div>
          <el-button type="primary" @click="sendMessage">发送</el-button>
        </div>
      </div>
    </section>

    <aside class="teamflow-card context-pane" v-if="thread.task_context">
      <div class="detail-head">
        <h3>任务详情</h3>
      </div>
      <div class="context-card">
        <div class="thread-title">#{{ thread.task_context.id }} {{ thread.task_context.title }}</div>
        <div class="status-tag purple">{{ thread.task_context.response_status }}</div>
        <div class="context-grid">
          <div><label>负责人</label><span>{{ thread.task_context.assignee?.name }}</span></div>
          <div><label>截止日期</label><span>{{ thread.task_context.due_date }}</span></div>
          <div><label>优先级</label><span>{{ thread.task_context.priority }}</span></div>
          <div><label>进度</label><span>{{ thread.task_context.progress }}%</span></div>
        </div>
        <el-progress :percentage="thread.task_context.progress" :show-text="false" />
        <div class="context-actions">
          <el-button type="primary" @click="updateProgress">更新进度</el-button>
          <el-button type="warning" @click="markBlocked">标记阻塞</el-button>
        </div>
      </div>
      <div class="activity-list compact">
        <div v-for="item in activities" :key="item.id" class="activity-item">
          <img :src="item.actor?.avatar" alt="avatar" />
          <div>
            <div>{{ item.content }}</div>
            <div class="tiny-muted">{{ item.created_at }}</div>
          </div>
        </div>
      </div>
    </aside>

    <el-dialog v-model="createDialog" title="新建会话" width="520px">
      <el-form :model="conversationForm" label-position="top">
        <el-form-item label="会话名称"><el-input v-model="conversationForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" @click="createConversation">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { conversationApi, taskApi } from '@/api'
import { useUserStore } from '@/stores/user'

type ConversationFilter = 'all' | 'unread' | 'mention' | 'later'
type EditorMode = 'text' | 'code' | 'task'

const conversationTabItems: Array<{ key: ConversationFilter; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'unread', label: '未读' },
  { key: 'mention', label: '@ 我' },
  { key: 'later', label: '稍后处理' },
]

const editorModeItems: Array<{ key: EditorMode; label: string }> = [
  { key: 'text', label: '文字' },
  { key: 'code', label: '代码' },
  { key: 'task', label: '任务引用' },
]

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const projectId = computed(() => route.params.id as string)
const conversations = ref<any[]>([])
const currentConversation = ref<any>(null)
const thread = reactive<any>({ messages: [], task_context: null })
const messageForm = reactive({ content: '' })
const activities = ref<any[]>([])
const taskOptions = ref<any[]>([])
const loading = ref(false)
const createDialog = ref(false)
const conversationForm = reactive({ name: '' })
const conversationFilter = ref<ConversationFilter>('all')
const editorMode = ref<EditorMode>('text')
const taskReferenceId = ref<number | null>(null)
const codeLanguage = ref('Java')
const laterConversationIds = ref<number[]>([])

const laterStorageKey = computed(() => `teamflow-later-conversations-${projectId.value}`)
const mentionKeywords = computed(() => [userStore.user?.display_name, userStore.user?.username, '@我', '@ 我'].filter(Boolean))
const filteredConversations = computed(() =>
  conversations.value.filter((item) => {
    if (conversationFilter.value === 'unread') {
      return item.unread_count > 0
    }
    if (conversationFilter.value === 'mention') {
      return mentionKeywords.value.some((keyword) => item.latest_message?.content?.includes(keyword))
    }
    if (conversationFilter.value === 'later') {
      return laterConversationIds.value.includes(item.id)
    }
    return true
  }),
)
const isCurrentMarkedLater = computed(() => !!currentConversation.value && laterConversationIds.value.includes(currentConversation.value.id))
const composerPlaceholder = computed(() => {
  if (editorMode.value === 'code') {
    return '输入代码片段，Enter 发送，Shift + Enter 换行'
  }
  if (editorMode.value === 'task') {
    return '可补充任务说明或引用备注，Enter 发送'
  }
  return '输入消息，Enter 发送，Shift + Enter 换行'
})
const editorHelperText = computed(() => {
  if (editorMode.value === 'code') {
    return `当前以 ${codeLanguage.value} 代码片段发送`
  }
  if (editorMode.value === 'task') {
    return taskReferenceId.value ? '将以任务引用消息发送，并可点击跳转到任务页' : '先选择一个任务，再发送任务引用'
  }
  return '@ / 附件 / 图片 / 代码块'
})

const loadLaterConversations = () => {
  try {
    const raw = localStorage.getItem(laterStorageKey.value)
    laterConversationIds.value = raw ? JSON.parse(raw) : []
  } catch {
    laterConversationIds.value = []
  }
}

const persistLaterConversations = () => {
  localStorage.setItem(laterStorageKey.value, JSON.stringify(laterConversationIds.value))
}

const load = async () => {
  loading.value = true
  try {
    loadLaterConversations()
    const [conversationRes, taskRes] = await Promise.all([
      conversationApi.list(projectId.value),
      taskApi.list(projectId.value),
    ])
    conversations.value = conversationRes.data
    taskOptions.value = taskRes.data
    const preferred = currentConversation.value
      ? conversationRes.data.find((item: any) => item.id === currentConversation.value.id)
      : conversationRes.data[1] || conversationRes.data[0]
    if (preferred) {
      await selectConversation(preferred)
    }
  } finally {
    loading.value = false
  }
}

const selectConversation = async (item: any) => {
  currentConversation.value = item
  await conversationApi.read(item.id).catch(() => null)
  const row = conversations.value.find((conversation) => conversation.id === item.id)
  if (row) {
    row.unread_count = 0
  }
  const { data } = await conversationApi.messages(item.id)
  Object.assign(thread, data)
  if (data.task_context) {
    const activityRes = await taskApi.activities(data.task_context.id)
    activities.value = activityRes.data
  } else {
    activities.value = []
  }
}

const fillTaskReference = () => {
  const task = taskOptions.value.find((item) => item.id === taskReferenceId.value)
  if (!task) {
    ElMessage.warning('请先选择一个任务')
    return
  }
  messageForm.content = `关联任务 #${task.id} ${task.title}`
  ElMessage.success('已插入任务引用')
}

const insertCodeTemplate = () => {
  messageForm.content = codeLanguage.value === 'Java'
    ? '@GetMapping("/task/detail")\npublic Result<TaskDetail> detail(){\n    return Result.success(taskService.detail());\n}'
    : codeLanguage.value === 'TypeScript'
      ? 'const payload = await api.getTaskDetail(taskId)\nconsole.log(payload)'
      : codeLanguage.value === 'Python'
        ? 'def build_task_context(task_id: int):\n    return task_service.detail(task_id)\n'
        : 'SELECT id, title, status\nFROM tasks\nWHERE project_id = ?;'
  ElMessage.success('代码模板已插入')
}

const sendMessage = async () => {
  if (!currentConversation.value) return
  let payload: Record<string, unknown> | null = null
  if (editorMode.value === 'task') {
    const task = taskOptions.value.find((item) => item.id === taskReferenceId.value)
    if (!task) {
      ElMessage.warning('请先选择要引用的任务')
      return
    }
    const extra = messageForm.content.trim() && !messageForm.content.includes(`关联任务 #${task.id}`) ? `\n备注：${messageForm.content.trim()}` : ''
    payload = {
      content: `关联任务 #${task.id} ${task.title}${extra}`,
      message_type: 'task',
      metadata: { task_id: task.id, task_title: task.title },
    }
  } else if (editorMode.value === 'code') {
    if (!messageForm.content.trim()) {
      ElMessage.warning('请输入代码内容')
      return
    }
    payload = {
      content: messageForm.content,
      message_type: 'code',
      code_language: codeLanguage.value,
    }
  } else {
    if (!messageForm.content.trim()) {
      ElMessage.warning('请输入消息内容')
      return
    }
    payload = {
      content: messageForm.content,
      message_type: 'text',
    }
  }
  await conversationApi.sendMessage(currentConversation.value.id, payload)
  messageForm.content = ''
  if (editorMode.value === 'task') {
    taskReferenceId.value = null
  }
  await selectConversation(currentConversation.value)
}

const createConversation = async () => {
  if (!conversationForm.name.trim()) {
    ElMessage.warning('请输入会话名称')
    return
  }
  await conversationApi.create(projectId.value, {
    name: conversationForm.name,
    conversation_type: 'project_group',
  })
  conversationForm.name = ''
  createDialog.value = false
  ElMessage.success('会话已创建')
  await load()
}

const updateProgress = async () => {
  if (!thread.task_context || !currentConversation.value) return
  await taskApi.accept(thread.task_context.id)
  ElMessage.success('任务状态已更新')
  await selectConversation(currentConversation.value)
}

const markBlocked = async () => {
  if (!thread.task_context || !currentConversation.value) return
  await taskApi.block(thread.task_context.id, { blocker_reason: '需要补充接口定义与依赖说明' })
  ElMessage.warning('任务已标记阻塞')
  await selectConversation(currentConversation.value)
}

const toggleLaterConversation = () => {
  if (!currentConversation.value) return
  if (laterConversationIds.value.includes(currentConversation.value.id)) {
    laterConversationIds.value = laterConversationIds.value.filter((id) => id !== currentConversation.value.id)
    ElMessage.success('已取消稍后处理')
  } else {
    laterConversationIds.value = [...laterConversationIds.value, currentConversation.value.id]
    ElMessage.success('已加入稍后处理')
  }
  persistLaterConversations()
}

const openTask = async (taskId: number) => {
  await router.push(`/projects/${projectId.value}/tasks?taskId=${taskId}`)
}

const openReferencedTask = async (message: any) => {
  const taskId = message.metadata?.task_id || thread.task_context?.id
  if (!taskId) {
    ElMessage.info('当前消息没有绑定具体任务')
    return
  }
  await openTask(taskId)
}

onMounted(load)
</script>

<style scoped>
.messages-page {
  display: grid;
  gap: 18px;
  height: 100%;
  min-height: 0;
  grid-template-columns: 340px 1fr 320px;
}

.conversation-pane,
.thread-pane,
.context-pane {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 18px;
}

.pane-header,
.conversation-top,
.thread-header,
.editor-actions,
.context-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.thread-header-actions,
.task-reference-bar {
  display: flex;
  gap: 10px;
  align-items: center;
}

.conversation-tabs {
  display: flex;
  gap: 12px;
  margin: 14px 0 18px;
}

.tab-button {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font: inherit;
}

.tab-button.active {
  color: var(--primary);
  font-weight: 700;
}

.conversation-list,
.thread-messages {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12px;
  overflow: auto;
}

.list-empty {
  padding: 18px 0;
  text-align: center;
}

.conversation-item {
  display: grid;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  cursor: pointer;
  grid-template-columns: 44px 1fr 24px;
}

.conversation-item.active {
  background: linear-gradient(180deg, #f5f8ff 0%, #eef4ff 100%);
}

.conversation-icon {
  display: grid;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  place-items: center;
  background: rgba(79, 70, 229, 0.1);
}

.conversation-badge {
  display: grid;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  place-items: center;
  background: var(--danger);
  color: white;
  font-size: 12px;
}

.thread-title {
  font-size: 22px;
  font-weight: 700;
}

.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-row.mine {
  flex-direction: row-reverse;
}

.message-row img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.message-content {
  max-width: 76%;
}

.message-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.text-bubble,
.file-block,
.code-block,
.task-block {
  padding: 14px 16px;
  border: 1px solid #edf1ff;
  border-radius: 16px;
  background: #fff;
  white-space: pre-wrap;
}

.file-block {
  background: linear-gradient(180deg, #eef4ff 0%, #f8fbff 100%);
}

.code-block {
  background: #161b35;
  color: #e2e8f0;
  font-family: 'SFMono-Regular', Consolas, monospace;
}

.task-block {
  background: linear-gradient(180deg, #eef4ff 0%, #f8fbff 100%);
  cursor: pointer;
}

.message-editor {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eef2ff;
}

.editor-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 14px;
}

.task-reference-bar {
  margin-bottom: 12px;
}

.task-reference-bar :deep(.el-select) {
  flex: 1;
}

.context-card {
  padding: 18px;
  border: 1px solid #edf1ff;
  border-radius: 18px;
}

.context-grid {
  display: grid;
  gap: 14px;
  margin: 14px 0;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.context-grid label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-muted);
  font-size: 12px;
}

.activity-list.compact {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.activity-item {
  display: flex;
  gap: 10px;
}

.activity-item img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}
</style>
