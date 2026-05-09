<template>
  <div class="wiki-home">
    <el-card title="Wiki 首页">
      <p>欢迎访问知识库 Wiki 站点</p>
      <el-button type="primary" @click="goToDocument">浏览文档</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDocument() {
  router.push('/wiki/document/1')
}
</script>

<style scoped>
.wiki-home {
  padding: 24px;
}
</style>
