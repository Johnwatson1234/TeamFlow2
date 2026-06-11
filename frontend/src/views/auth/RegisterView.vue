<template>
  <AppViewport background="linear-gradient(180deg, #f9fbff 0%, #eef4ff 100%)">
  <div class="register-shell">
    <div class="register-card teamflow-card">
      <div class="panel-title">创建 TeamFlow 账号</div>
      <p class="page-desc">加入协作空间，体验任务协同、文档协作、贡献审计与 AI 项目经理</p>
      <el-alert v-if="errorMessage" :closable="false" :title="errorMessage" class="register-error" show-icon type="error" />
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="form.display_name" placeholder="请输入显示名称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" show-password type="password" />
        </el-form-item>
        <el-button :loading="loading" class="register-submit" type="primary" @click="submit">立即注册</el-button>
      </el-form>
      <div class="panel-footer">
        已有账号？
        <router-link class="action-link" to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
  </AppViewport>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppViewport from '@/components/common/AppViewport.vue'
import { useUserStore } from '@/stores/user'
import { getApiErrorMessage } from '@/utils/apiError'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const errorMessage = ref('')
const form = reactive({
  username: '',
  display_name: '',
  email: '',
  password: '',
})

const submit = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await userStore.register(form)
    ElMessage.success('注册成功')
    router.push('/projects')
  } catch (error: any) {
    errorMessage.value = getApiErrorMessage(error, '注册失败，请检查输入内容')
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-shell {
  display: grid;
  min-height: 100dvh;
  padding: 24px 16px;
  place-items: center;
  background: radial-gradient(circle at top left, rgba(79, 70, 229, 0.1), transparent 24%);
}

.register-card {
  width: 520px;
  max-width: 100%;
  padding: 42px 40px;
}

.register-error {
  margin-bottom: 18px;
}

.panel-title {
  font-size: 30px;
  font-weight: 700;
}

.register-submit {
  width: 100%;
  margin-top: 8px;
}

.panel-footer {
  margin-top: 22px;
  text-align: center;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .register-shell {
    padding: 16px 12px;
  }

  .register-card {
    padding: 28px 18px;
  }
}
</style>
