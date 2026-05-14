<template>
  <div class="app-wrapper">
    <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    <AIChat v-else @logout="handleLogout" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Login from './components/Login.vue'
import AIChat from './components/AIChat.vue'

const isLoggedIn = ref(false)

const checkLogin = () => {
  const token = localStorage.getItem('tinywiki_access_token')
  isLoggedIn.value = !!token
}

const handleLoginSuccess = () => {
  isLoggedIn.value = true
}

const handleLogout = () => {
  localStorage.removeItem('tinywiki_access_token')
  localStorage.removeItem('tinywiki_refresh_token')
  isLoggedIn.value = false
}

onMounted(() => {
  checkLogin()
})
</script>

<style scoped>
.app-wrapper {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
}
</style>
