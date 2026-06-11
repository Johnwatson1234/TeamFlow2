<template>
  <div class="ai-page">
    <div class="ai-main">
      <div class="teamflow-card ai-chat">
        <div class="thread-title">TeamFlow AI 助手</div>
        <div class="page-desc">你好，我是你的 AI 项目经理。我可以帮你进行任务拆解与规划、制定进度计划、风险识别与建议、生成项目报告。</div>
        <div class="chat-bubbles app-scroll" style="max-height: 400px; overflow-y: auto;">
          <div class="bubble assistant">请帮我为 {{ projectStore.currentProject?.name || '当前项目' }} 制定详细的任务规划，并给出里程碑建议和风险提示。</div>
          <div v-for="(msg, idx) in chatHistory" :key="idx" :class="['bubble', msg.role]">
            {{ msg.content }}
          </div>
          <div class="bubble assistant typing" v-if="isGenerating">
            <span></span><span></span><span></span>
          </div>
        </div>
        <el-input v-model="prompt" :rows="4" type="textarea" placeholder="输入你想让 AI 协助的内容..." @keyup.enter.ctrl="generate" />
        <div class="editor-actions" style="margin-top: 12px;">
          <div class="tiny-muted">AI 生成内容仅供参考，请结合实际情况判断 (Ctrl+Enter 发送)</div>
          <el-button type="primary" :loading="isGenerating" @click="generate">发送</el-button>
        </div>
      </div>

      <div class="teamflow-card ai-result" v-if="result">
        <div class="panel-header">
          <div class="thread-title">AI 任务规划结果</div>
          <div class="editor-actions">
            <el-button @click="confirmPlan">确认写入项目</el-button>
            <el-button type="primary" @click="weeklyReport">生成周报</el-button>
          </div>
        </div>
        <div class="result-scroll app-scroll">
          <div class="phase-track">
            <div v-for="phase in result.phases" :key="phase.step" class="phase-node">
              <div class="phase-index">{{ phase.step }}</div>
              <div class="phase-title">{{ phase.title }}</div>
              <div class="tiny-muted">{{ phase.date }}</div>
            </div>
          </div>
          <el-table :data="result.tasks">
            <el-table-column label="任务名称" prop="name" min-width="180" />
            <el-table-column label="负责人" prop="owner" width="100" />
            <el-table-column label="优先级" prop="priority" width="100" />
            <el-table-column label="预计工时" prop="hours" width="100" />
            <el-table-column label="截止日期" prop="deadline" width="100" />
            <el-table-column label="状态" prop="status" width="100" />
          </el-table>
          <div class="grid-2 ai-section-grid">
            <div class="teamflow-card inner-card">
              <div class="section-title">进度建议</div>
              <ul class="suggestion-list app-scroll">
                <li v-for="item in result.suggestions" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="teamflow-card inner-card">
              <div class="section-title">风险提示</div>
              <div class="risk-table-wrap app-scroll">
                <el-table :data="result.risks">
                  <el-table-column label="风险项" prop="name" />
                  <el-table-column label="等级" prop="level" width="90" />
                  <el-table-column label="建议" prop="suggestion" min-width="160" />
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <aside class="ai-side teamflow-card">
      <div class="section-title">项目概览（实时）</div>
      <div class="repo-item"><label>当前阶段</label><span>系统设计</span></div>
      <div class="repo-item"><label>整体进度</label><span>28%</span></div>
      <div class="repo-item"><label>已完成任务</label><span>12 / 43</span></div>
      <div class="repo-item"><label>延期任务</label><span>2</span></div>
      <div class="repo-item"><label>项目截止</label><span>2024-06-12（剩余 25 天）</span></div>
      <div class="section-title side-gap">智能快捷入口</div>
      <div class="quick-grid">
        <div class="quick-card">任务拆解</div>
        <div class="quick-card">进度建议</div>
        <div class="quick-card">风险扫描</div>
        <div class="quick-card">周报生成</div>
      </div>
      <div class="section-title side-gap">历史对话</div>
      <div class="history-item">为项目制定任务规划</div>
      <div class="history-item">给出下周工作建议</div>
      <div class="history-item">生成本周项目周报</div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { aiApi } from '@/api'
import { useProjectStore } from '@/stores/project'

const route = useRoute()
const projectStore = useProjectStore()
const projectId = computed(() => route.params.id as string)
const prompt = ref('请帮我拆解当前阶段任务，并给出风险建议。')
const result = ref<any>(null)
const suggestionId = ref<number | null>(null)
const isGenerating = ref(false)
const chatHistory = ref<{role: string, content: string}[]>([])

const generate = async () => {
  if (!prompt.value.trim() || isGenerating.value) return
  
  const userPrompt = prompt.value
  chatHistory.value.push({ role: 'user', content: userPrompt })
  prompt.value = ''
  isGenerating.value = true
  result.value = null // 清空旧结果以展示动画
  
  try {
    // 模拟大模型思考的真实延迟
    await new Promise(r => setTimeout(r, 1500))
    
    const current = projectStore.currentProject
    const { data } = await aiApi.planning({
      project_id: Number(projectId.value),
      project_name: current?.name || '课设项目',
      deadline: current?.due_date || '2024-06-30',
      tech_stack: 'Vue 3, TypeScript, FastAPI, SQLite',
      members: [
        { name: '张三', role: '组长' },
        { name: '李四', role: '后端开发' },
        { name: '王五', role: '前端开发' },
        { name: '赵六', role: '数据库设计' },
        { name: '孙七', role: '文档负责人' },
      ],
      user_prompt: userPrompt
    })
    
    result.value = data.result
    suggestionId.value = data.id
    chatHistory.value.push({ role: 'assistant', content: '已为您深度拆解当前阶段任务，并生成里程碑建议与风险提示，请查阅右侧面板。' })
  } catch (err) {
    chatHistory.value.push({ role: 'assistant', content: '抱歉，连接 AI 引擎失败，请检查网络或后端服务。' })
  } finally {
    isGenerating.value = false
  }
}

const confirmPlan = async () => {
  if (!suggestionId.value) return
  await aiApi.confirm(suggestionId.value)
  ElMessage.success('AI 规划已写入项目')
}

const weeklyReport = async () => {
  const { data } = await aiApi.weeklyReport(projectId.value)
  ElMessage.success(data.content)
}

</script>

<style scoped>
.ai-page {
  display: grid;
  height: 100%;
  min-height: 0;
  gap: 18px;
  grid-template-columns: 1fr 320px;
}

.ai-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 0;
}

.ai-chat,
.ai-result,
.ai-side,
.inner-card {
  padding: 18px;
}

.ai-chat,
.ai-result,
.ai-side {
  min-height: 0;
}

.ai-result,
.inner-card {
  display: flex;
  flex-direction: column;
}

.ai-result {
  flex: 1;
  overflow: hidden;
}

.result-scroll {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  overflow: auto;
}

.chat-bubbles {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin: 18px 0;
}

.bubble {
  padding: 14px 16px;
  border-radius: 16px;
}

.bubble.assistant {
  background: #f8fafc;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.bubble.user {
  background: linear-gradient(180deg, #eef4ff 0%, #f7fbff 100%);
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.bubble.typing {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 48px;
}

.bubble.typing span {
  display: block;
  width: 6px;
  height: 6px;
  background: #cbd5e1;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out both;
}

.bubble.typing span:nth-child(1) { animation-delay: -0.32s; }
.bubble.typing span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.panel-header,
.editor-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.phase-track {
  display: grid;
  gap: 12px;
  margin: 18px 0;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.phase-node {
  text-align: center;
}

.phase-index {
  display: grid;
  width: 44px;
  height: 44px;
  margin: 0 auto 10px;
  border: 2px solid #4f46e5;
  border-radius: 50%;
  place-items: center;
  color: var(--primary);
  font-weight: 700;
}

.ai-section-grid {
  margin-top: 18px;
  align-items: stretch;
}

.inner-card {
  min-height: 260px;
  overflow: hidden;
}

.suggestion-list {
  flex: 1;
  margin: 14px 0 0;
  padding-left: 20px;
  overflow: auto;
}

.suggestion-list li + li {
  margin-top: 10px;
}

.risk-table-wrap {
  flex: 1;
  min-height: 0;
  margin-top: 12px;
  overflow: auto;
}

.repo-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.repo-item label {
  color: var(--text-muted);
}

.side-gap {
  margin-top: 24px;
}

.quick-grid {
  display: grid;
  gap: 12px;
  margin-top: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.quick-card,
.history-item {
  padding: 14px;
  border: 1px solid #eef2ff;
  border-radius: 14px;
}

.history-item + .history-item {
  margin-top: 10px;
}

.ai-side {
  overflow: auto;
}

@media (max-width: 1200px) {
  .ai-page,
  .phase-track,
  .ai-section-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .panel-header,
  .editor-actions {
    align-items: flex-start;
    gap: 10px;
    flex-direction: column;
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }

  .phase-track {
    gap: 10px;
  }
}
</style>
