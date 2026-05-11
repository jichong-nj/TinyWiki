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
import { ElMessage } from 'element-plus'
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
  directory: null,
  folder: null
})

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

function loadDocument() {
  if (!isNew.value) {
    console.log('开始加载文档，ID:', route.params.id)
    axios.get(`/documents/documents/${route.params.id}/`)
      .then(response => {
        console.log('文档加载成功:', response.data)
        documentData.value = response.data
        form.title = response.data.title
        form.content = response.data.content || ''
        form.directory = response.data.directory
        form.folder = response.data.folder
        console.log('设置表单:', form)
      })
      .catch(error => {
        console.error('加载文档失败:', error)
        ElMessage.error('加载文档失败，请查看控制台')
      })
  }
}

function saveDraft() {
  const data = {
    title: form.title,
    content: form.content,
    directory: form.directory,
    folder: form.folder,
    filename: documentData.value?.filename || (form.title.toLowerCase().replace(/\s+/g, '-') + '.md')
  }
  
  console.log('保存草稿，数据:', data)
  
  if (isNew.value) {
    axios.post('/documents/documents/', data)
      .then(() => {
        ElMessage.success('保存成功')
        goBack()
      })
      .catch(error => {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      })
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then(() => {
        ElMessage.success('保存成功')
        goBack()
      })
      .catch(error => {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      })
  }
}

function saveAndPublish() {
  const data = {
    title: form.title,
    content: form.content,
    directory: form.directory,
    folder: form.folder,
    filename: documentData.value?.filename || (form.title.toLowerCase().replace(/\s+/g, '-') + '.md')
  }
  
  console.log('保存并发布，数据:', data)
  
  if (isNew.value) {
    axios.post('/documents/documents/', data)
      .then(response => {
        const docId = response.data.id
        axios.post(`/documents/documents/${docId}/publish/`)
          .then(() => {
            ElMessage.success('发布成功')
            goBack()
          })
      })
      .catch(error => {
        console.error('发布失败:', error)
        ElMessage.error('发布失败')
      })
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then(() => {
        axios.post(`/documents/documents/${route.params.id}/publish/`)
          .then(() => {
            ElMessage.success('发布成功')
            goBack()
          })
      })
      .catch(error => {
        console.error('发布失败:', error)
        ElMessage.error('发布失败')
      })
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
