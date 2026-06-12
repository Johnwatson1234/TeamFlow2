<template>
  <div class="ai-dock">
    <button class="dock-trigger" type="button" @click="visible = true">
      <span class="trigger-glow"></span>
      <span class="trigger-label">✨</span>
    </button>

    <el-drawer
      v-model="visible"
      class="ai-assistant-drawer"
      direction="rtl"
      size="min(520px, 100vw)"
      :with-header="false"
      @opened="loadConversation"
    >
      <div class="assistant-shell">
        <div class="assistant-header">
          <div>
            <div class="assistant-title">TeamFlow AI 助手</div>
            <div class="assistant-subtitle">{{ pageLabel }} · 实时上下文</div>
          </div>
          <div class="assistant-actions">
            <span class="status-tag teal">Mimo</span>
            <span class="status-tag blue">{{ projectStore.currentProject?.name || '当前项目' }}</span>
          </div>
        </div>

        <div class="assistant-quick-actions">
          <button v-for="item in quickPrompts" :key="item.label" type="button" class="quick-pill" @click="useQuickPrompt(item.prompt)">
            {{ item.label }}
          </button>
        </div>

        <div class="assistant-context teamflow-card">
          <div class="section-title">当前页面上下文</div>
          <div class="context-grid">
            <div><label>页面</label><strong>{{ pageLabel }}</strong></div>
            <div><label>路由</label><strong>{{ route.path }}</strong></div>
            <div><label>项目任务</label><strong>{{ projectStore.currentProject?.progress ?? 0 }}%</strong></div>
            <div><label>筛选/选中</label><strong>{{ contextSummary }}</strong></div>
          </div>
        </div>

        <div ref="messageScroller" class="assistant-messages app-scroll">
          <div v-for="message in messages" :key="message.localId" :class="['message-wrapper', message.role]">
            <div :class="['assistant-message', message.role]">
              <div class="message-head" v-if="message.role === 'assistant'">
                <span>TeamFlow AI</span>
                <span class="tiny-muted">{{ message.time }}</span>
              </div>
              <div class="message-body">{{ message.content }}</div>
              <div v-if="message.actions?.length" class="action-chip-list">
                <span v-for="(item, index) in message.actions" :key="`${message.localId}-${index}`" class="action-chip">
                  {{ actionLabel(item.type) }}
                </span>
              </div>
            </div>
          </div>
          <div v-if="streaming" class="message-wrapper assistant">
            <div class="assistant-message assistant pending">
              <div class="message-head">
                <span>TeamFlow AI</span>
                <span class="tiny-muted">{{ statusText || '正在生成' }}</span>
              </div>
              <div class="message-body">{{ streamingContent || '正在思考当前页面内容…' }}</div>
            </div>
          </div>
        </div>

        <div v-if="actionResults.length" class="assistant-results teamflow-card">
          <div class="section-title">最近自动操作</div>
          <div class="result-list">
            <div v-for="(item, index) in actionResults" :key="`${item.type}-${index}`" class="result-row">
              <div>
                <strong>{{ actionLabel(item.type) }}</strong>
                <div class="tiny-muted">{{ item.result?.message || '已执行' }}</div>
              </div>
              <span :class="['status-tag', item.status === 'ok' ? 'green' : 'red']">
                {{ item.status === 'ok' ? '成功' : '失败' }}
              </span>
            </div>
          </div>
        </div>

        <div class="assistant-composer">
          <el-input
            v-model="prompt"
            :rows="2"
            :autosize="{ minRows: 2, maxRows: 6 }"
            type="textarea"
            placeholder="与 AI 助手对话..."
            @keyup.enter.ctrl="sendPrompt"
          />
          <div class="composer-actions">
            <div class="tiny-muted">Ctrl+Enter 发送</div>
            <el-button type="primary" round :loading="streaming" @click="sendPrompt">发送</el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { aiApi, streamAiChat } from '@/api'
import { useAiStore } from '@/stores/ai'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const aiStore = useAiStore()
const projectStore = useProjectStore()
const userStore = useUserStore()

const visible = ref(false)
const prompt = ref('')
const streaming = ref(false)
const streamingContent = ref('')
const statusText = ref('')
const actionResults = ref<any[]>([])
const messageScroller = ref<HTMLElement | null>(null)
const messages = ref<Array<{ localId: string; role: 'user' | 'assistant'; content: string; time: string; actions?: any[] }>>([])

const pageLabel = computed(() => ({
  dashboard: '项目仪表盘',
  tasks: '任务管理',
  milestones: '里程碑',
  messages: '消息讨论',
  documents: '文档协作',
  'document-editor': '文档编辑',
  files: '文件管理',
  graph: '协作图谱',
  contribution: '贡献分析',
  career: '成员画像',
  risk: '风险预警',
  git: 'Git 协作',
  ai: 'AI 工作台',
  settings: '项目设置',
  reminders: '协作提醒',
  audit: '过程审计',
}[String(route.name || '')] || '项目页面'))

const contextSummary = computed(() => {
  const entries = Object.entries(aiStore.pageContext || {}).filter(([, value]) => value !== '' && value !== null && value !== undefined)
  if (!entries.length) return '无特殊筛选'
  return entries.slice(0, 3).map(([key, value]) => `${key}:${String(value)}`).join(' / ')
})

const quickPrompts = [
  { label: '总结当前页', prompt: '请总结当前页面的关键信息和需要关注的问题。' },
  { label: '下一步建议', prompt: '结合当前页面内容，给我三个最值得立即推进的下一步。' },
  { label: '自动整理任务', prompt: '结合当前页面数据，如果合适请直接帮我整理并更新相关任务。' },
  { label: '生成项目周报', prompt: '请根据当前项目数据直接生成本周周报，并在系统中留痕。' },
]

const scrollToBottom = async () => {
  await nextTick()
  if (messageScroller.value) {
    messageScroller.value.scrollTop = messageScroller.value.scrollHeight
  }
}

const loadConversation = async () => {
  const projectId = route.params.id as string
  if (!projectId) return
  const { data } = await aiApi.conversation(projectId)
  messages.value = (data.messages || []).map((item: any) => ({
    localId: `server-${item.id}`,
    role: item.sender?.name === 'TeamFlow AI' || item.message_type === 'ai' || item.message_type === 'ai_action' ? 'assistant' : 'user',
    content: item.content,
    time: item.created_at?.slice(11, 16) || '--:--',
    actions: item.metadata?.actions || (item.message_type === 'ai_action' ? [item.metadata] : []),
  }))
  await scrollToBottom()
}

const useQuickPrompt = (value: string) => {
  prompt.value = value
}

const actionLabel = (type: string) => ({
  navigate_page: '页面导航',
  open_task: '打开任务',
  open_document: '打开文档',
  open_file: '打开文件',
  create_task: '创建任务',
  update_task: '更新任务',
  accept_task: '开始任务',
  block_task: '阻塞任务',
  complete_task: '完成任务',
  create_milestone: '创建里程碑',
  generate_weekly_report: '生成周报',
  scan_risks: '风险扫描',
  recalculate_contribution: '重算贡献分析',
}[type] || type)

const applyUiAction = async (item: any) => {
  const params = item.params || {}
  if (item.type === 'navigate_page' && (params.path || item.result?.path)) {
    await router.push(params.path || item.result.path)
    return
  }
  if (item.type === 'open_task' && params.task_id) {
    await router.push(`/projects/${route.params.id}/tasks?taskId=${params.task_id}`)
    return
  }
  if (item.type === 'open_document' && params.document_id) {
    await router.push(`/projects/${route.params.id}/documents/${params.document_id}`)
    return
  }
  if (item.type === 'open_file' && params.file_id) {
    await router.push(`/projects/${route.params.id}/files?fileId=${params.file_id}`)
  }
}

const sendPrompt = async () => {
  const projectId = route.params.id as string
  if (!projectId || !prompt.value.trim() || streaming.value) return
  const userPrompt = prompt.value.trim()
  prompt.value = ''
  actionResults.value = []
  messages.value.push({
    localId: `local-user-${Date.now()}`,
    role: 'user',
    content: userPrompt,
    time: new Date().toLocaleTimeString().slice(0, 5),
  })
  streaming.value = true
  streamingContent.value = ''
  statusText.value = ''
  await scrollToBottom()

  try {
    await streamAiChat(
      projectId,
      {
        prompt: userPrompt,
        route_name: String(route.name || ''),
        route_path: route.path,
        route_params: route.params,
        query: route.query,
        page_context: {
          ...aiStore.pageContext,
          currentUserId: userStore.user?.id,
        },
        auto_execute: true,
      },
      {
        onStatus(payload) {
          statusText.value = payload.message
        },
        onChunk(payload) {
          streamingContent.value += payload.content || ''
          scrollToBottom()
        },
        onAction(payload) {
          actionResults.value = [...actionResults.value, payload]
        },
        async onDone(payload) {
          const finalReply = payload.reply || streamingContent.value
          messages.value.push({
            localId: `local-ai-${Date.now()}`,
            role: 'assistant',
            content: finalReply,
            time: new Date().toLocaleTimeString().slice(0, 5),
            actions: payload.actions || [],
          })
          aiStore.setLatestActionResults(payload.action_results || [])
          window.dispatchEvent(new CustomEvent('teamflow-ai-refresh', { detail: payload.action_results || [] }))
          for (const item of payload.action_results || []) {
            if (item.status === 'ok' && ['navigate_page', 'open_task', 'open_document', 'open_file'].includes(item.type)) {
              await applyUiAction(item)
            }
          }
          streaming.value = false
          streamingContent.value = ''
          statusText.value = ''
          await loadConversation()
        },
        onError(payload) {
          streaming.value = false
          streamingContent.value = ''
          statusText.value = ''
          ElMessage.error(payload.message || 'AI 处理失败')
        },
      },
    )
  } catch (error: any) {
    streaming.value = false
    streamingContent.value = ''
    statusText.value = ''
    ElMessage.error(error?.message || '无法连接 AI 助手')
  }
}

watch(() => route.fullPath, () => {
  aiStore.resetPageContext()
  actionResults.value = []
})
</script>

<style scoped>
:global(.ai-assistant-drawer) {
  background: transparent !important;
  box-shadow: -10px 0 40px rgba(0,0,0,0.15) !important;
}
:global(.ai-assistant-drawer .el-drawer__body) {
  padding: 0 !important;
  background: transparent !important;
}

.ai-dock {
  position: fixed;
  right: 22px;
  bottom: 22px;
  z-index: 40;
}

.dock-trigger {
  position: relative;
  display: grid;
  width: 56px;
  height: 56px;
  border: 0;
  border-radius: 50%;
  place-items: center;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  box-shadow: 0 12px 24px rgba(139, 92, 246, 0.35);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.dock-trigger:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 16px 32px rgba(139, 92, 246, 0.45);
}

.trigger-glow {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1px solid rgba(139, 92, 246, 0.3);
  animation: pulse-glow 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.05); }
}

.trigger-label {
  position: relative;
  color: #fff;
  font-size: 24px;
}

.assistant-shell {
  display: flex;
  height: 100%;
  min-height: 0;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  background: rgba(248, 250, 252, 0.85);
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255,255,255,0.6);
}

.assistant-header,
.assistant-actions,
.composer-actions,
.message-head,
.result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.assistant-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--ai-ink);
}

.assistant-subtitle {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 13px;
}

.assistant-actions {
  gap: 8px;
  align-items: flex-start;
  flex-direction: column;
}

.assistant-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-pill {
  padding: 10px 14px;
  border: 1px solid rgba(29, 78, 216, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--ai-ink);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
}

.assistant-context,
.assistant-results {
  padding: 14px 16px;
  border-color: rgba(29, 78, 216, 0.08);
}

.context-grid {
  display: grid;
  gap: 12px;
  margin-top: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.context-grid label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-muted);
  font-size: 12px;
}

.context-grid strong {
  color: var(--ai-ink);
  font-size: 14px;
}

.assistant-messages {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
  gap: 16px;
  overflow: auto;
  padding-right: 8px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.message-wrapper.user {
  align-items: flex-end;
}

.message-wrapper.assistant {
  align-items: flex-start;
}

.assistant-message {
  padding: 12px 16px;
  border-radius: 16px;
  max-width: 85%;
  line-height: 1.6;
}

.assistant-message.user {
  background: var(--primary);
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
}

.assistant-message.assistant {
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  color: var(--text);
  border-bottom-left-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.assistant-message.pending {
  border-style: dashed;
}

.message-head {
  gap: 12px;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 700;
}

.message-body {
  line-height: 1.7;
  white-space: pre-wrap;
}

.action-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.action-chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(13, 148, 136, 0.12);
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.result-row {
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.result-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.assistant-composer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #fff;
  padding: 12px 16px;
  border-radius: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.assistant-composer :deep(.el-textarea__inner) {
  border: none !important;
  box-shadow: none !important;
  background: transparent;
  padding: 0;
  resize: none;
}

@media (max-width: 768px) {
  .ai-dock {
    right: 16px;
    bottom: 16px;
  }

  .dock-trigger {
    width: 58px;
    height: 58px;
    border-radius: 18px;
  }

  .context-grid {
    grid-template-columns: 1fr;
  }
}
</style>
