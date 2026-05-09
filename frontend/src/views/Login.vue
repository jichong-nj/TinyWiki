<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>知识库管理系统</h1>
        <p>欢迎登录</p>
      </div>
      
      <el-form :model="form" ref="formRef" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" class="login-btn">登录</el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-link">
        <span>还没有账号？</span>
        <el-button text @click="showRegister = true">注册</el-button>
      </div>
    </div>
    
    <el-dialog v-model="showRegister" title="注册" width="400px">
      <el-form :model="registerForm" ref="registerFormRef" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="passwordConfirm">
          <el-input v-model="registerForm.passwordConfirm" type="password" placeholder="请确认密码" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const showRegister = ref(false)

const form = reactive({
  email: '',
  password: ''
})

const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  passwordConfirm: ''
})

function handleLogin() {
  authStore.login(form.email, form.password)
    .then(() => {
      router.push('/')
    })
    .catch(error => {
      console.error('登录失败:', error)
      alert('登录失败，请检查邮箱和密码')
    })
}

function handleRegister() {
  if (registerForm.password !== registerForm.passwordConfirm) {
    alert('两次输入的密码不一致')
    return
  }
  
  authStore.register(registerForm.email, registerForm.username, registerForm.password)
    .then(() => {
      showRegister.value = false
      router.push('/')
    })
    .catch(error => {
      console.error('注册失败:', error)
      alert('注册失败')
    })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.login-header p {
  margin: 0;
  color: #666;
}

.login-btn {
  width: 100%;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.register-link button {
  margin-left: 8px;
}
</style>