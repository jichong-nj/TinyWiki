<template>
  <div class="wiki-layout">
    <header class="wiki-header">
      <div class="header-left">
        <h1>Wiki</h1>
      </div>
      <div class="header-right">
        <el-button @click="goBack">返回管理</el-button>
      </div>
    </header>
    <main class="wiki-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.wiki-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.wiki-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
}

.wiki-main {
  flex: 1;
  overflow: auto;
}
</style>
