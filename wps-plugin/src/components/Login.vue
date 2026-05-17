<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="logo">🤖</div>
          <h1>AI 助手</h1>
          <p>请登录以继续使用</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              type="text"
              v-model="form.username"
              placeholder="请输入用户名"
              required
              autocomplete="username"
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              required
              autocomplete="current-password"
            />
          </div>
          
          <div class="remember-row">
            <label class="remember-checkbox">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住密码</span>
            </label>
          </div>
          
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
          
          <button type="submit" class="login-button" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../axios';
import { ref, reactive, onMounted } from 'vue';

export default {
  name: 'LoginPage',
  setup() {
    const form = reactive({
      username: '',
      password: ''
    });
    const loading = ref(false);
    const error = ref('');
    const rememberMe = ref(false);

    onMounted(() => {
      const savedUsername = localStorage.getItem('savedUsername');
      const savedPassword = localStorage.getItem('savedPassword');
      const remember = localStorage.getItem('rememberMe');
      
      if (remember === 'true' && savedUsername) {
        form.username = savedUsername;
        form.password = savedPassword || '';
        rememberMe.value = true;
      }
    });

    const handleLogin = async () => {
      if (!form.username || !form.password) {
        error.value = '请输入用户名和密码';
        return;
      }

      loading.value = true;
      error.value = '';

      try {
        console.log('正在登录...', form.username);
        
        const response = await axios.post('/auth/login/', {
          username: form.username,
          password: form.password
        });

        console.log('登录响应:', response);

        const { access, refresh } = response.data;
        
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);
        localStorage.setItem('currentUsername', form.username);
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        
        if (rememberMe.value) {
          localStorage.setItem('savedUsername', form.username);
          localStorage.setItem('savedPassword', form.password);
          localStorage.setItem('rememberMe', 'true');
        } else {
          localStorage.removeItem('savedUsername');
          localStorage.removeItem('savedPassword');
          localStorage.setItem('rememberMe', 'false');
        }
        
        console.log('登录成功，token 已保存');
        
        window.location.hash = '#/aichat';
        
      } catch (err) {
        console.error('登录失败:', err);
        if (err.response?.status === 401) {
          error.value = '用户名或密码错误';
        } else if (err.response?.data?.detail) {
          error.value = err.response.data.detail;
        } else {
          error.value = '登录失败，请检查网络连接';
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      loading,
      error,
      rememberMe,
      handleLogin
    };
  }
};
</script>

<style scoped>
.login-page {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
  overflow: auto;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo {
  font-size: 64px;
  margin-bottom: 15px;
}

.login-header h1 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  color: #d23f3f;
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: #fef2f2;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.remember-row {
  display: flex;
  justify-content: flex-start;
}

.remember-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.remember-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.login-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
