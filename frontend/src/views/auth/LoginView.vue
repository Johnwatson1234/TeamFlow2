<template>
  <AppViewport background="white">
  <div class="auth-shell">
    <div class="brand-header">
      <div class="brand-mark">⬡</div>
      <div class="brand-title">TeamFlow</div>
      <div class="brand-lang">简体中文</div>
    </div>

    <section class="auth-hero">
      <div class="hero-left">
        <h1>TeamFlow</h1>
        <h2>小组协作过程管理软件</h2>
        <p>助力团队高效协作，规范过程管理，提升研发效率与质量</p>

        <div class="hero-visual teamflow-card">
          <img :src="heroIllustration" alt="TeamFlow 协作平台示意图" class="hero-illustration" />
        </div>

        <div class="feature-list">
          <div class="feature" v-for="item in features" :key="item.title">
            <el-icon><component :is="item.icon" /></el-icon>
            <div class="feature-title">{{ item.title }}</div>
            <div class="tiny-muted">{{ item.desc }}</div>
          </div>
        </div>
      </div>

      <div class="auth-panel teamflow-card">
        <div class="panel-title">用户登录</div>
        <div class="panel-underline"></div>
        <el-alert v-if="errorMessage" :closable="false" :title="errorMessage" class="auth-error" show-icon type="error" />
        <el-form :model="form" @submit.prevent="submit">
          <el-form-item label="账号">
            <el-input v-model="form.username" size="large" placeholder="请输入账号" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" size="large" show-password placeholder="请输入密码" type="password" />
          </el-form-item>
          <div class="auth-row">
            <el-checkbox v-model="remember">记住我</el-checkbox>
            <a class="action-link">忘记密码？</a>
          </div>
          <el-button :loading="loading" class="auth-submit" size="large" type="primary" @click="submit">登录</el-button>
        </el-form>
        <div class="auth-split">其他方式登录</div>
        <div class="sso-box">SSO 登录</div>
        <div class="panel-footer">
          还没有账号？
          <router-link class="action-link" to="/register">立即注册</router-link>
        </div>
        <div class="demo-tip">演示账号：zhangsan / 123456、lisi / 123456</div>
      </div>
    </section>
  </div>
  </AppViewport>
</template>

<script setup lang="ts">
import { DataAnalysis, Files, Histogram, Monitor, UserFilled, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import heroIllustration from '@/assets/generated/login-hero-gpt.png'
import AppViewport from '@/components/common/AppViewport.vue'
import { useUserStore } from '@/stores/user'
import { getApiErrorMessage } from '@/utils/apiError'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const remember = ref(true)
const errorMessage = ref('')

const form = reactive({
  username: 'zhangsan',
  password: '123456',
})

const features = [
  { title: '过程可视化', desc: '项目进度透明可见，协作过程全程记录', icon: UserFilled },
  { title: '任务协同', desc: '任务分配与跟踪，高效协同推进', icon: Monitor },
  { title: '文档协作', desc: '在线编辑与版本管理，知识沉淀便捷共享', icon: Files },
  { title: '贡献分析', desc: '多维度贡献评估，激励团队成长', icon: Histogram },
  { title: '风险预警', desc: '智能风险识别，提前预警防范', icon: WarningFilled },
  { title: 'AI 项目经理', desc: '自动任务拆解与周报生成', icon: DataAnalysis },
]

const submit = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push('/projects')
  } catch (error: any) {
    errorMessage.value = getApiErrorMessage(error, '登录失败，请检查账号和密码')
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-shell {
  min-height: 100dvh;
  padding: 32px 52px 20px;
  background:
    radial-gradient(circle at 20% 24%, rgba(79, 70, 229, 0.1), transparent 25%),
    radial-gradient(circle at 80% 18%, rgba(6, 182, 212, 0.08), transparent 22%),
    white;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text);
}

.brand-title {
  font-size: 22px;
  font-weight: 700;
}

.brand-mark {
  display: grid;
  width: 44px;
  height: 44px;
  border-radius: 16px;
  place-items: center;
  background: linear-gradient(135deg, #4f6cf3 0%, #2f6ee9 100%);
  color: white;
}

.brand-lang {
  margin-left: auto;
  color: var(--text-muted);
}

.auth-hero {
  display: grid;
  align-items: center;
  min-height: calc(var(--app-height) - 110px);
  gap: 52px;
  grid-template-columns: 1fr 560px;
}

.hero-left h1 {
  margin: 0;
  font-size: 78px;
  color: #2f6ee9;
}

.hero-left h2 {
  margin: 10px 0 0;
  font-size: 54px;
}

.hero-left p {
  margin-top: 18px;
  color: var(--text-muted);
  font-size: 24px;
}

.hero-visual {
  margin-top: 44px;
  padding: 18px;
}

.hero-illustration {
  display: block;
  width: 100%;
  height: 420px;
  border-radius: 28px;
  object-fit: cover;
  object-position: center;
}

.feature-list {
  display: grid;
  gap: 18px;
  margin-top: 48px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.feature {
  padding-right: 14px;
}

.feature :deep(.el-icon) {
  display: grid;
  width: 48px;
  height: 48px;
  margin-bottom: 10px;
  border-radius: 14px;
  place-items: center;
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
}

.feature-title {
  margin-bottom: 6px;
  font-size: 18px;
  font-weight: 700;
}

.auth-panel {
  padding: 48px 40px 32px;
}

.auth-error {
  margin-bottom: 22px;
}

.panel-title {
  text-align: center;
  font-size: 40px;
  font-weight: 700;
}

.panel-underline {
  width: 56px;
  height: 4px;
  margin: 14px auto 34px;
  border-radius: 999px;
  background: var(--primary);
}

.auth-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 22px;
}

.auth-submit {
  width: 100%;
  height: 56px;
  font-size: 20px;
}

.auth-split {
  position: relative;
  margin: 32px 0 24px;
  color: var(--text-muted);
  text-align: center;
}

.auth-split::before,
.auth-split::after {
  position: absolute;
  top: 50%;
  width: 34%;
  height: 1px;
  background: #e8edf7;
  content: '';
}

.auth-split::before {
  left: 0;
}

.auth-split::after {
  right: 0;
}

.sso-box {
  display: grid;
  width: 108px;
  height: 108px;
  margin: 0 auto;
  border: 1px solid var(--border);
  border-radius: 50%;
  place-items: center;
  color: var(--text);
}

.panel-footer,
.demo-tip {
  margin-top: 32px;
  color: var(--text-muted);
  text-align: center;
}

@media (max-width: 1200px) {
  .auth-shell {
    padding: 24px 28px 18px;
  }

  .auth-hero {
    gap: 28px;
    grid-template-columns: 1fr;
  }

  .hero-left h1 {
    font-size: 56px;
  }

  .hero-left h2 {
    font-size: 38px;
  }

  .hero-left p {
    font-size: 20px;
  }

  .feature-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .auth-shell {
    padding: 18px 16px 20px;
  }

  .brand-header {
    flex-wrap: wrap;
  }

  .brand-lang {
    margin-left: 0;
  }

  .auth-hero {
    gap: 22px;
  }

  .hero-left h1 {
    font-size: 40px;
  }

  .hero-left h2 {
    font-size: 28px;
  }

  .hero-left p {
    font-size: 16px;
  }

  .hero-visual {
    margin-top: 24px;
    padding: 12px;
  }

  .hero-illustration {
    height: 240px;
    border-radius: 20px;
  }

  .feature-list {
    gap: 14px;
    margin-top: 28px;
    grid-template-columns: 1fr;
  }

  .auth-panel {
    padding: 28px 18px 22px;
  }

  .panel-title {
    font-size: 30px;
  }
}
</style>
