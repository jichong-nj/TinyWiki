<template>
  <div class="document-edit">
    <div class="edit-header">
      <div class="header-left">
        <el-button @click="goBack">返回</el-button>
      </div>
      <div class="header-center">
        <el-input v-model="form.title" placeholder="文档标题" class="title-input" />
      </div>
      <div class="header-right">
        <el-button text @click="saveDraft">保存草稿</el-button>
        <el-button type="primary" @click="saveAndPublish" v-if="isNew || (documentData && documentData.publish_status === 'draft')">发布</el-button>
      </div>
    </div>
    
    <div class="edit-body">
      <MarkdownEditor v-model="form.content" height="100%" mode="split" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../../axios'
import MarkdownEditor from '../../components/MarkdownEditor.vue'

interface Document {
  id: number
  title: string
  filename: string
  content: string
  publish_status: string
  analysis_status: string
}

const route = useRoute()
const router = useRouter()

const isNew = computed(() => route.params.id === 'new')
const documentData = ref<Document | null>(null)

const form = reactive({
  title: '',
  content: '',
  directory: 1
})

function goBack() {
  router.push('/')
}

function loadDocument() {
  if (!isNew.value) {
    axios.get(`/documents/documents/${route.params.id}/`)
      .then(response => {
        documentData.value = response.data
        form.title = response.data.title
        form.content = response.data.content || ''
      })
      .catch(error => console.error('加载文档失败:', error))
  }
}

function saveDraft() {
  const data = {
    title: form.title,
    content: form.content,
    directory: form.directory,
    filename: form.title.toLowerCase().replace(/\s+/g, '-') + '.md'
  }
  
  if (isNew.value) {
    axios.post('/documents/documents/', data)
      .then(() => {
        alert('保存成功')
        router.push('/')
      })
      .catch(error => console.error('保存失败:', error))
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then(() => {
        alert('保存成功')
      })
      .catch(error => console.error('保存失败:', error))
  }
}

function saveAndPublish() {
  const data = {
    title: form.title,
    content: form.content,
    directory: form.directory,
    filename: form.title.toLowerCase().replace(/\s+/g, '-') + '.md'
  }
  
  if (isNew.value) {
    axios.post('/documents/documents/', data)
      .then(response => {
        const docId = response.data.id
        axios.post(`/documents/documents/${docId}/publish/`)
          .then(() => {
            alert('发布成功')
            router.push('/')
          })
      })
      .catch(error => console.error('发布失败:', error))
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then(() => {
        axios.post(`/documents/documents/${route.params.id}/publish/`)
          .then(() => {
            alert('发布成功')
            router.push('/')
          })
      })
      .catch(error => console.error('发布失败:', error))
  }
}

onMounted(() => {
  loadDocument()
})
</script>

<style scoped>
.document-edit {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.title-input {
  width: 400px;
  font-size: 20px;
}

.edit-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
