<template>
  <div class="document-list">
    <div class="list-header">
      <div class="header-left">
        <el-select v-model="selectedDirectory" placeholder="选择目录">
          <el-option v-for="dir in directories" :key="dir.id" :label="dir.name" :value="dir.id" />
        </el-select>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createDocument">创建文档</el-button>
      </div>
    </div>
    
    <div class="list-content">
      <div class="directory-tree">
        <el-tree
          :data="treeData"
          :props="treeProps"
          @node-click="handleTreeClick"
          class="tree"
        />
      </div>
      
      <div class="document-table">
        <el-table :data="documents" border>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="publish_status" label="发布状态">
            <template #default="scope">
              <el-tag :type="scope.row.publish_status === 'published' ? 'success' : 'warning'">
                {{ scope.row.publish_status === 'published' ? '已发布' : '未发布' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="analysis_status" label="分析状态">
            <template #default="scope">
              <el-tag :type="getAnalysisTagType(scope.row.analysis_status)">
                {{ getAnalysisStatusText(scope.row.analysis_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button text @click="editDocument(scope.row.id)">编辑</el-button>
              <el-button text type="danger" @click="deleteDocument(scope.row.id)">删除</el-button>
              <el-button v-if="scope.row.publish_status === 'draft'" text type="primary" @click="publishDocument(scope.row.id)">发布</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../../axios'

interface Document {
  id: number
  title: string
  filename: string
  publish_status: string
  analysis_status: string
  updated_at: string
}

interface Directory {
  id: number
  name: string
  knowledge_base: number
}

interface TreeItem {
  id: number
  name: string
  type: string
  children?: TreeItem[]
}

const router = useRouter()

const documents = ref<Document[]>([])
const directories = ref<Directory[]>([])
const selectedDirectory = ref<number | null>(null)
const treeData = ref<TreeItem[]>([])

const treeProps = {
  label: 'name',
  children: 'children'
}

function getAnalysisTagType(status: string) {
  switch (status) {
    case 'completed': return 'success'
    case 'analyzing': return 'warning'
    default: return 'info'
  }
}

function getAnalysisStatusText(status: string) {
  switch (status) {
    case 'completed': return '已分析'
    case 'analyzing': return '分析中'
    default: return '未分析'
  }
}

function loadDocuments() {
  const params: Record<string, number> = {}
  if (selectedDirectory.value) {
    params.directory = selectedDirectory.value
  }
  axios.get('/documents/documents/', { params })
    .then(response => {
      documents.value = response.data
    })
    .catch(error => console.error('加载文档失败:', error))
}

function loadDirectories() {
  axios.get('/documents/directories/')
    .then(response => {
      directories.value = response.data
    })
    .catch(error => console.error('加载目录失败:', error))
}

function loadTree() {
  axios.get('/documents/knowledge-bases/1/tree/')
    .then(response => {
      treeData.value = response.data
    })
    .catch(error => console.error('加载目录树失败:', error))
}

function handleTreeClick(node: TreeItem) {
  if (node.type === 'directory') {
    selectedDirectory.value = node.id
    loadDocuments()
  } else if (node.type === 'document') {
    router.push(`/document/${node.id}`)
  }
}

function createDocument() {
  router.push('/document/new')
}

function editDocument(id: number) {
  router.push(`/document/${id}`)
}

function deleteDocument(id: number) {
  if (confirm('确定要删除这个文档吗？')) {
    axios.delete(`/documents/documents/${id}/`)
      .then(() => {
        loadDocuments()
      })
      .catch(error => console.error('删除文档失败:', error))
  }
}

function publishDocument(id: number) {
  axios.post(`/documents/documents/${id}/publish/`)
    .then(() => {
      loadDocuments()
    })
    .catch(error => console.error('发布文档失败:', error))
}

onMounted(() => {
  loadDocuments()
  loadDirectories()
  loadTree()
})
</script>

<style scoped>
.document-list {
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  width: 200px;
}

.list-content {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
}

.directory-tree {
  width: 250px;
  background: white;
  border-radius: 8px;
  padding: 10px;
  overflow-y: auto;
}

.tree :deep(.el-tree-node__content) {
  height: 36px;
  line-height: 36px;
}

.document-table {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: auto;
}
</style>