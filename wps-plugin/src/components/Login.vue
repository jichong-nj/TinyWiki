<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <span class="logo-icon">🤖</span>
        <h1>TinyWiki AI</h1>
        <p>登录您的账号</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>服务器地址</label>
          <input
            v-model="serverUrl"
            type="text"
            placeholder="http://localhost:8000/api"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            class="form-input"
            required
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            class="form-input"
            required
          />
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios, { updateBaseURL } from '../axios'

const emit = defineEmits(['login-success'])

const serverUrl = ref(localStorage.getItem('tinywiki_base_url') || 'http://localhost:8000/api')
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!serverUrl.value) {
    error.value = '请输入服务器地址'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // 更新基础 URL
    updateBaseURL(serverUrl.value.replace(/\/api$/, '') + '/api')

    const response = await axios.post('/auth/login/', {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('tinywiki_access_token', response.data.access)
    localStorage.setItem('tinywiki_refresh_token', response.data.refresh)
    emit('login-success')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查账号密码和服务器地址'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 360px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 8px;
}

.login-header h1 {
  font-size: 24px;
  color: #333;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #667eea;
}

.login-btn {
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #d23f3f;
  font-size: 13px;
  text-align: center;
  margin-top: 8px;
}
</style>
