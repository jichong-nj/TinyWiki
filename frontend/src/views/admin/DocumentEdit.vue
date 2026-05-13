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
        <el-button type="primary" @click="saveAndPublish" v-if="isNew || (documentData && documentData.publish_status === 'draft')">保存并加入发布队列</el-button>
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

const isNew = computed(() => {
  const id = route.params.id
  console.log('DocumentEdit route.params:', route.params)
  console.log('DocumentEdit id:', id, 'type:', typeof id)
  return id === 'new' || id === undefined || id === 'undefined'
})
const documentData = ref<Document | null>(null)

const form = reactive({
  title: '',
  content: '',
  directory: null as number | null,
  folder: null as number | null
})

function goBack() {
  router.push('/')
}

function loadDocument() {
  console.log('loadDocument called, isNew:', isNew.value, 'route.params.id:', route.params.id)
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
      .then((response) => {
        ElMessage.success('保存成功')
        // 保存后不退出，继续编辑
        router.replace({ path: `/document/${response.data.id}`, query: route.query })
        documentData.value = response.data
      })
      .catch(error => {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      })
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then((response) => {
        ElMessage.success('保存成功')
        // 保存后不退出，继续编辑
        documentData.value = response.data
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
            ElMessage.success('文档已加入发布队列')
            // 保存后不退出，继续编辑
            router.replace({ path: `/document/${docId}`, query: route.query })
            documentData.value = { ...response.data, publish_status: 'published' }
          })
          .catch(error => {
            console.error('加入发布队列失败:', error)
            ElMessage.error('加入发布队列失败')
          })
      })
      .catch(error => {
        console.error('加入发布队列失败:', error)
        ElMessage.error('加入发布队列失败')
      })
  } else {
    axios.put(`/documents/documents/${route.params.id}/`, data)
      .then((response) => {
        axios.post(`/documents/documents/${route.params.id}/publish/`)
          .then(() => {
            ElMessage.success('文档已加入发布队列')
            // 保存后不退出，继续编辑
            documentData.value = { ...response.data, publish_status: 'published' }
          })
          .catch(error => {
            console.error('加入发布队列失败:', error)
            ElMessage.error('加入发布队列失败')
          })
      })
      .catch(error => {
        console.error('加入发布队列失败:', error)
        ElMessage.error('加入发布队列失败')
      })
  }
}

onMounted(() => {
  // 从查询参数中读取directory和folder
  const query = route.query
  if (query.directory) {
    form.directory = Number(query.directory)
  }
  if (query.folder) {
    form.folder = Number(query.folder)
  }
  console.log('从查询参数设置的directory和folder:', form.directory, form.folder)
  
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
