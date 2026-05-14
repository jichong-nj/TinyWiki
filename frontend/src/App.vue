<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import axios from './axios'

const authStore = useAuthStore()

async function loadSystemConfig() {
  try {
    const response = await axios.get('/system/config/')
    if (response.data.success && response.data.data && response.data.data.name) {
      document.title = response.data.data.name
    }
  } catch (error) {
    console.error('Failed to load system config:', error)
  }
}

onMounted(() => {
  authStore.loadFromStorage()
  loadSystemConfig()
})
</script>

<template>
  <router-view />
</template>

<style scoped>
</style>
