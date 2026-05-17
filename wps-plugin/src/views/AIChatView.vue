<template>
  <div class="ai-chat-view-container">
    <div v-if="isLoading" class="loading-container">
      加载中...
    </div>
    <Login v-else-if="!isLoggedIn" />
    <AIChat v-else :modelValue="true" :username="username" />
  </div>
</template>

<script>
import AIChat from '../components/AIChat.vue';
import Login from '../components/Login.vue';

export default {
  name: 'AIChatView',
  components: {
    AIChat,
    Login
  },
  data() {
    return {
      isLoading: true,
      isLoggedIn: false,
      username: ''
    };
  },
  mounted() {
    console.log('AIChatView mounted');
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      console.log('Checking auth...');
      const token = localStorage.getItem('accessToken');
      const savedUsername = localStorage.getItem('currentUsername');
      console.log('Token found:', !!token);
      console.log('Username found:', savedUsername);
      
      if (token && savedUsername) {
        this.isLoggedIn = true;
        this.username = savedUsername;
      } else {
        this.isLoggedIn = false;
        this.username = '';
      }
      this.isLoading = false;
      console.log('isLoading:', this.isLoading, 'isLoggedIn:', this.isLoggedIn, 'username:', this.username);
    }
  }
};
</script>

<style scoped>
.ai-chat-view-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.loading-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
}
</style>
