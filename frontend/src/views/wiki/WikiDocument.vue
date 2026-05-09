<template>
  <div class="wiki-document">
    <el-card>
      <template #header>
        <span>{{ documentTitle }}</span>
      </template>
      <div class="document-content" v-html="renderedContent"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const documentTitle = ref('文档标题')
const renderedContent = ref('<p>文档内容加载中...</p>')

onMounted(() => {
  documentTitle.value = `文档 ${route.params.id}`
  renderedContent.value = `<h1>文档 ${route.params.id}</h1><p>这是 Wiki 文档的内容区域。</p>`
})
</script>

<style scoped>
.wiki-document {
  padding: 24px;
}

.document-content {
  line-height: 1.8;
}
</style>
