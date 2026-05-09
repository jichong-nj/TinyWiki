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
        <div class="tree-content">
          <div 
            v-for="dir in directories" 
            :key="dir.id" 
            class="tree-item"
            :class="{ active: selectedDirectory === dir.id }"
            @click="selectDirectory(dir.id)"
          >
            <el-icon class="dir-icon"><FolderOpened /></el-icon>
            <span class="dir-name">{{ dir.name }}</span>
            <el-dropdown trigger="click" @click.stop>
              <el-button type="text" class="item-menu-btn">
                <el-icon class="icon"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="editDirectory(dir)">修改</el-dropdown-item>
                  <el-dropdown-item @click="deleteDirectory(dir.id)">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="add-dir-item">
            <el-button type="text" class="add-dir-btn" @click="showAddDialog = true">
              <el-icon class="add-icon"><Plus /></el-icon>
              <span>添加目录</span>
            </el-button>
          </div>
        </div>
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
    
    <el-dialog :title="editingDir ? '修改目录' : '添加目录'" v-model="showAddDialog" @close="cancelCreateDirectory">
      <el-form>
        <el-form-item label="目录名称">
          <el-input v-model="newDirName" placeholder="请输入目录名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelCreateDirectory">取消</el-button>
        <el-button type="primary" @click="editingDir ? updateDirectory() : createDirectory()">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../../axios'
import { MoreFilled, FolderOpened, Plus } from '@element-plus/icons-vue'

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



const router = useRouter()

const documents = ref<Document[]>([])
const directories = ref<Directory[]>([])
const selectedDirectory = ref<number | null>(null)
const showAddDialog = ref(false)
const newDirName = ref('')
const editingDir = ref<Directory | null>(null)



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



function selectDirectory(id: number) {
  selectedDirectory.value = id
  loadDocuments()
}

function editDirectory(dir: Directory) {
  editingDir.value = dir
  newDirName.value = dir.name
  showAddDialog.value = true
}

function deleteDirectory(id: number) {
  if (confirm('确定要删除这个目录吗？')) {
    axios.delete(`/documents/directories/${id}/`)
      .then(() => {
        loadDirectories()
        if (selectedDirectory.value === id) {
          selectedDirectory.value = null
          loadDocuments()
        }
      })
      .catch(error => console.error('删除目录失败:', error))
  }
}

function updateDirectory() {
  if (!newDirName.value.trim() || !editingDir.value) {
    return
  }
  axios.put(`/documents/directories/${editingDir.value.id}/`, {
    name: newDirName.value,
    knowledge_base: editingDir.value.knowledge_base
  })
  .then(() => {
    loadDirectories()
    showAddDialog.value = false
    newDirName.value = ''
    editingDir.value = null
  })
  .catch(error => console.error('更新目录失败:', error))
}

function createDirectory() {
  if (!newDirName.value.trim()) {
    return
  }
  axios.post('/documents/directories/', {
    name: newDirName.value,
    knowledge_base: 1
  })
  .then(() => {
    loadDirectories()
    showAddDialog.value = false
    newDirName.value = ''
  })
  .catch(error => console.error('创建目录失败:', error))
}

function cancelCreateDirectory() {
  showAddDialog.value = false
  newDirName.value = ''
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
  overflow: hidden;
}

.tree-content {
  padding: 8px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tree-item:hover {
  background-color: #f5f7fa;
}

.tree-item.active {
  background-color: #e8f4fd;
}

.tree-item.active .dir-name {
  color: #1890ff;
}

.dir-icon {
  margin-right: 8px;
  color: #1890ff;
}

.dir-name {
  flex: 1;
  font-size: 13px;
  color: #333;
}

.item-menu-btn {
  padding: 4px;
  color: #999;
  opacity: 0;
}

.tree-item:hover .item-menu-btn {
  opacity: 1;
}

.item-menu-btn:hover {
  color: #666;
}

.add-dir-item {
  padding: 8px 12px;
}

.add-dir-btn {
  width: 100%;
  justify-content: center;
  color: #1890ff;
  font-size: 13px;
}

.add-dir-btn:hover {
  background-color: #e8f4fd;
}

.add-icon {
  margin-right: 4px;
}

.document-table {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: auto;
}
</style>