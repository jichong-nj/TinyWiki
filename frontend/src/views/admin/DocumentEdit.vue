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
    
    <div class="edit-content">
      <div class="editor-tabs">
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane label="编辑" name="edit">
            <div class="editor-wrapper">
              <div class="editor-toolbar">
                <el-button text @click="insertHeading">H1</el-button>
                <el-button text @click="insertHeading(2)">H2</el-button>
                <el-button text @click="insertHeading(3)">H3</el-button>
                <el-divider direction="vertical" />
                <el-button text @click="insertBold">Bold</el-button>
                <el-button text @click="insertItalic">Italic</el-button>
                <el-button text @click="insertCode">Code</el-button>
                <el-divider direction="vertical" />
                <el-button text @click="insertList('ul')">UL</el-button>
                <el-button text @click="insertList('ol')">OL</el-button>
                <el-button text @click="insertTable">Table</el-button>
              </div>
              <textarea v-model="form.content" class="editor-textarea" placeholder="开始编写文档..." />
            </div>
          </el-tab-pane>
          <el-tab-pane label="预览" name="preview">
            <div class="preview-wrapper" v-html="renderMarkdown(form.content)" />
          </el-tab-pane>
          <el-tab-pane label="版本历史" name="history">
            <div v-if="versions.length > 0">
              <el-table :data="versions" border>
                <el-table-column prop="version_number" label="版本号" />
                <el-table-column prop="modified_by" label="修改人" />
                <el-table-column prop="change_summary" label="变更摘要" />
                <el-table-column prop="created_at" label="修改时间" />
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button text @click="viewVersion(scope.row)">查看</el-button>
                    <el-button text @click="rollbackToVersion(scope.row)">回滚</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div v-else class="empty-history">
              暂无版本记录
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <el-dialog v-model="showVersionView" title="版本内容" width="800px">
      <div class="version-content" v-html="renderMarkdown(selectedVersion?.content || '')" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../../axios'

interface Document {
  id: number
  title: string
  filename: string
  content: string
  publish_status: string
  analysis_status: string
}

interface DocumentVersion {
  id: number
  document: number
  version_number: number
  content: string
  modified_by: string
  change_summary: string
  created_at: string
}

const route = useRoute()
const router = useRouter()

const isNew = computed(() => route.params.id === 'new')
const documentData = ref<Document | null>(null)
const versions = ref<DocumentVersion[]>([])
const activeTab = ref('edit')
const showVersionView = ref(false)
const selectedVersion = ref<DocumentVersion | null>(null)

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
        loadVersions()
      })
      .catch(error => console.error('加载文档失败:', error))
  }
}

function loadVersions() {
  if (!isNew.value) {
    axios.get(`/documents/documents/${route.params.id}/versions/`)
      .then(response => {
        versions.value = response.data
      })
      .catch(error => console.error('加载版本历史失败:', error))
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
        loadVersions()
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

function renderMarkdown(text: string) {
  let html = text
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  return html
}

function insertHeading(level = 1) {
  const prefix = '#'.repeat(level) + ' '
  form.content += prefix + '标题\n\n'
}

function insertBold() {
  form.content += '**粗体文本**'
}

function insertItalic() {
  form.content += '*斜体文本*'
}

function insertCode() {
  form.content += '`代码`'
}

function insertList(type: string) {
  const bullet = type === 'ul' ? '- ' : '1. '
  form.content += `${bullet}列表项\n`
}

function insertTable() {
  form.content += `| 列1 | 列2 |\n| --- | --- |\n| 值1 | 值2 |\n\n`
}

function viewVersion(version: DocumentVersion) {
  selectedVersion.value = version
  showVersionView.value = true
}

function rollbackToVersion(version: DocumentVersion) {
  if (confirm(`确定要回滚到版本 v${version.version_number} 吗？`)) {
    form.content = version.content
    saveDraft()
  }
}

onMounted(() => {
  loadDocument()
})
</script>

<style scoped>
.document-edit {
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-input {
  width: 400px;
  font-size: 20px;
}

.edit-content {
  flex: 1;
  overflow: hidden;
}

.editor-tabs {
  height: 100%;
}

.editor-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
}

.editor-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  padding: 10px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  resize: none;
  border: none;
  padding: 15px;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}

.preview-wrapper {
  height: 100%;
  padding: 20px;
  overflow: auto;
  background: white;
}

.preview-wrapper :deep(h1) {
  font-size: 24px;
  margin: 20px 0 10px;
}

.preview-wrapper :deep(h2) {
  font-size: 20px;
  margin: 18px 0 8px;
}

.preview-wrapper :deep(h3) {
  font-size: 16px;
  margin: 16px 0 6px;
}

.preview-wrapper :deep(strong) {
  font-weight: bold;
}

.preview-wrapper :deep(em) {
  font-style: italic;
}

.preview-wrapper :deep(code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.empty-history {
  text-align: center;
  padding: 40px;
  color: #999;
}

.version-content {
  max-height: 400px;
  overflow: auto;
  padding: 10px;
}
</style>