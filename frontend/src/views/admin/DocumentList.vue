<template>
  <div class="document-list">
    <div class="list-header">
      <div class="breadcrumb-section">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">知识库</el-breadcrumb-item>
          <el-breadcrumb-item v-if="selectedDirectory">{{ getCurrentDirectoryName() }}</el-breadcrumb-item>
          <el-breadcrumb-item v-for="(folder, index) in breadcrumbFolders" :key="folder.id">
            <span @click="navigateToFolder(index)">{{ folder.name }}</span>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="stats-section">
        <span class="stats-text">未发布{{ draftCount }}条，待分析{{ pendingAnalysisCount }}条</span>
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
      
      <div class="document-list-container">
        <div class="list-header-row">
          <span class="total-count">共 {{ documents.length }} 个文档</span>
          <div class="header-actions">
            <el-dropdown trigger="click">
              <el-button type="text">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="createDocument">创建文档</el-dropdown-item>
                  <el-dropdown-item @click="showSubfolderDialog = true">创建子文件夹</el-dropdown-item>
                  <el-dropdown-item @click="showImportDialog = true">导入文件</el-dropdown-item>
                  <el-dropdown-item>批量删除</el-dropdown-item>
                  <el-dropdown-item>导出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <div class="document-items">
          <div 
            v-for="folder in folders" 
            :key="folder.id" 
            class="document-item folder-item"
            @click="drillIntoFolder(folder)"
          >
            <div class="item-left">
              <el-icon class="folder-icon"><FolderOpened /></el-icon>
              <span class="doc-name">{{ folder.name }}</span>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            
            <div class="item-center">
            </div>
            
            <div class="item-right">
              <span class="update-time">-</span>
              <el-dropdown trigger="click" @click.stop>
                <el-button type="text" class="menu-btn">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editFolder(folder)">修改</el-dropdown-item>
                    <el-dropdown-item @click="deleteFolder(folder.id)">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <div 
            v-for="doc in documents" 
            :key="doc.id" 
            class="document-item"
          >
            <div class="item-left">
              <el-icon class="doc-icon"><Document /></el-icon>
              <span class="doc-name">{{ doc.filename }}</span>
            </div>
            
            <div class="item-center">
              <el-tag :type="doc.publish_status === 'published' ? 'success' : 'warning'" size="small">
                {{ doc.publish_status === 'published' ? '已发布' : '未发布' }}
              </el-tag>
              <el-tag :type="getAnalysisTagType(doc.analysis_status)" size="small">
                {{ getAnalysisStatusText(doc.analysis_status) }}
              </el-tag>
            </div>
            
            <div class="item-right">
              <span class="update-time">{{ doc.updated_at }}</span>
              <el-dropdown trigger="click">
                <el-button type="text" class="menu-btn">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editDocument(doc.id)">编辑</el-dropdown-item>
                    <el-dropdown-item @click="deleteDocument(doc.id)">删除</el-dropdown-item>
                    <el-dropdown-item v-if="doc.publish_status === 'draft'" @click="publishDocument(doc.id)">发布</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog :title="editingDir ? '修改目录' : (editingFolder ? '修改文件夹' : '添加目录')" v-model="showAddDialog" @close="cancelCreateDirectory">
      <el-form>
        <el-form-item label="名称">
          <el-input v-model="newDirName" placeholder="请输入名称" @keyup.enter="handleSubmit" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelCreateDirectory">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog title="创建子文件夹" v-model="showSubfolderDialog" @close="cancelCreateSubfolder">
      <el-form>
        <el-form-item label="子文件夹名称">
          <el-input v-model="newSubfolderName" placeholder="请输入子文件夹名称" @keyup.enter="createSubfolder" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelCreateSubfolder">取消</el-button>
        <el-button type="primary" @click="createSubfolder">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog title="导入文件" v-model="showImportDialog" @close="cancelImport">
      <div class="import-area">
        <el-upload
          ref="uploadRef"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :data="uploadData"
          :multiple="true"
          accept=".md"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          class="upload-demo"
        >
          <el-button type="primary" icon="Upload">选择文件</el-button>
          <template #tip>
            <div class="el-upload__tip">支持 .md 格式文件，可多选</div>
          </template>
        </el-upload>
        
        <div v-if="importFiles.length > 0" class="file-list">
          <div v-for="(file, index) in importFiles" :key="index" class="file-item">
            <el-icon class="file-icon"><File /></el-icon>
            <span class="file-name">{{ file.name }}</span>
            <el-button type="text" size="small" @click="removeImportFile(index)">移除</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelImport">取消</el-button>
        <el-button type="primary" @click="startUpload">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../../axios'
import { MoreFilled, FolderOpened, Plus, Document, ArrowRight } from '@element-plus/icons-vue'

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

interface Folder {
  id: number
  name: string
  directory: number
  parent: number | null
}



const router = useRouter()

const documents = ref<Document[]>([])
const directories = ref<Directory[]>([])
const folders = ref<Folder[]>([])
const selectedDirectory = ref<number | null>(null)
const selectedFolder = ref<number | null>(null)
const breadcrumbFolders = ref<Folder[]>([])
const showAddDialog = ref(false)
const newDirName = ref('')
const editingDir = ref<Directory | null>(null)
const editingFolder = ref<Folder | null>(null)

const showSubfolderDialog = ref(false)
const newSubfolderName = ref('')

const showImportDialog = ref(false)
const importFiles = ref<File[]>([])
const uploadRef = ref()

const uploadUrl = computed(() => '/documents/documents/')
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('accessToken')
  return { Authorization: `Bearer ${token}` }
})
const uploadData = computed(() => ({
  directory: selectedDirectory.value || ''
}))

const draftCount = ref(0)
const pendingAnalysisCount = ref(0)

function updateStats() {
  draftCount.value = documents.value.filter(doc => doc.publish_status === 'draft').length
  pendingAnalysisCount.value = documents.value.filter(doc => doc.analysis_status !== 'completed').length
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
  if (selectedFolder.value) {
    params.folder = selectedFolder.value
  }
  axios.get('/documents/documents/', { params })
    .then(response => {
      documents.value = response.data
      updateStats()
    })
    .catch(error => console.error('加载文档失败:', error))
}

function loadFolders() {
  const params: Record<string, number> = {}
  if (selectedFolder.value) {
    params.parent = selectedFolder.value
  } else if (selectedDirectory.value) {
    params.directory = selectedDirectory.value
    params.parent = null
  }
  axios.get('/documents/folders/', { params })
    .then(response => {
      folders.value = response.data
    })
    .catch(error => console.error('加载文件夹失败:', error))
}

function loadDirectories() {
  axios.get('/documents/directories/')
    .then(response => {
      directories.value = response.data
      if (directories.value.length > 0 && !selectedDirectory.value) {
        selectedDirectory.value = directories.value[0].id
        loadDocuments()
      }
    })
    .catch(error => console.error('加载目录失败:', error))
}



function selectDirectory(id: number) {
  selectedDirectory.value = id
  selectedFolder.value = null
  breadcrumbFolders.value = []
  loadDocuments()
  loadFolders()
}

function drillIntoFolder(folder: Folder) {
  selectedFolder.value = folder.id
  breadcrumbFolders.value.push(folder)
  loadDocuments()
  loadFolders()
}

function navigateToFolder(index: number) {
  breadcrumbFolders.value = breadcrumbFolders.value.slice(0, index + 1)
  const lastFolder = breadcrumbFolders.value[breadcrumbFolders.value.length - 1]
  selectedFolder.value = lastFolder?.id || null
  loadDocuments()
  loadFolders()
}

function getCurrentDirectoryName() {
  const dir = directories.value.find(d => d.id === selectedDirectory.value)
  return dir?.name || ''
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
  editingDir.value = null
  editingFolder.value = null
}

function handleSubmit() {
  if (editingDir.value) {
    updateDirectory()
  } else if (editingFolder.value) {
    updateFolder()
  } else {
    createDirectory()
  }
}

function createSubfolder() {
  if (!newSubfolderName.value.trim()) {
    return
  }
  
  const data: Record<string, any> = {
    name: newSubfolderName.value
  }
  
  if (selectedFolder.value) {
    data.parent = selectedFolder.value
  } else if (selectedDirectory.value) {
    data.directory = selectedDirectory.value
  } else {
    return
  }
  
  axios.post('/documents/folders/', data)
  .then(() => {
    loadFolders()
    showSubfolderDialog.value = false
    newSubfolderName.value = ''
  })
  .catch(error => console.error('创建子文件夹失败:', error))
}

function cancelCreateSubfolder() {
  showSubfolderDialog.value = false
  newSubfolderName.value = ''
}

function cancelImport() {
  showImportDialog.value = false
  importFiles.value = []
}

function handleFileChange(file: any, fileList: any[]) {
  const newFiles = fileList.map(f => f.raw)
  
  const uniqueFiles: File[] = []
  const seenNames = new Set<string>()
  
  for (const f of newFiles) {
    if (!seenNames.has(f.name)) {
      seenNames.add(f.name)
      uniqueFiles.push(f)
    } else {
      alert(`文件 "${f.name}" 已存在于选择列表中，将跳过重复文件`)
    }
  }
  
  importFiles.value = uniqueFiles
}

function removeImportFile(index: number) {
  importFiles.value.splice(index, 1)
}

function startUpload() {
  if (importFiles.value.length === 0) {
    return
  }
  
  importFiles.value.forEach(file => {
    const formData = new FormData()
    formData.append('file', file)
    if (selectedFolder.value) {
      formData.append('folder', selectedFolder.value.toString())
    } else if (selectedDirectory.value) {
      formData.append('directory', selectedDirectory.value.toString())
    }
    
    axios.post('/documents/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    })
    .then(() => {
      loadDocuments()
    })
    .catch(error => console.error('导入文件失败:', error))
  })
  
  cancelImport()
}

function handleUploadSuccess() {
  loadDocuments()
}

function handleUploadError() {
  console.error('上传失败')
}

function editFolder(folder: Folder) {
  editingFolder.value = folder
  newDirName.value = folder.name
  showAddDialog.value = true
}

function updateFolder() {
  if (!newDirName.value.trim() || !editingFolder.value) {
    return
  }
  axios.put(`/documents/folders/${editingFolder.value.id}/`, {
    name: newDirName.value,
    directory: editingFolder.value.directory
  })
  .then(() => {
    loadFolders()
    showAddDialog.value = false
    newDirName.value = ''
    editingFolder.value = null
  })
  .catch(error => console.error('更新文件夹失败:', error))
}

function deleteFolder(id: number) {
  if (confirm('确定要删除这个文件夹吗？')) {
    axios.delete(`/documents/folders/${id}/`)
      .then(() => {
        loadFolders()
      })
      .catch(error => console.error('删除文件夹失败:', error))
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
  loadFolders()
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
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
}

.breadcrumb-section {
  flex: 1;
}

.stats-section {
  margin-left: 20px;
}

.stats-text {
  font-size: 14px;
  color: #666;
}

.arrow-icon {
  font-size: 14px;
  color: #999;
  margin-left: 4px;
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
  padding: 4px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin: 2px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #fafafa;
}

.tree-item:hover {
  background-color: #f0f2f5;
}

.tree-item.active {
  background-color: #e8f4fd;
  border-left: 3px solid #1890ff;
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

.document-list-container {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.list-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.total-count {
  font-size: 14px;
  color: #666;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.document-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.document-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  margin: 2px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.document-item:hover {
  background-color: #f5f7fa;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.doc-icon {
  color: #1890ff;
  font-size: 16px;
}

.folder-icon {
  color: #e6a23c;
  font-size: 16px;
}

.import-area {
  padding: 10px;
}

.file-list {
  margin-top: 15px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  padding: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px;
  margin-bottom: 5px;
  background: #fafafa;
  border-radius: 4px;
}

.file-item:last-child {
  margin-bottom: 0;
}

.file-icon {
  color: #1890ff;
  margin-right: 8px;
}

.file-name {
  flex: 1;
  font-size: 13px;
}

.upload-demo {
  margin-bottom: 10px;
}

.doc-name {
  font-size: 14px;
  color: #333;
}

.item-center {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 2;
  justify-content: center;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.update-time {
  font-size: 12px;
  color: #999;
}

.menu-btn {
  padding: 4px;
  color: #999;
  opacity: 0;
}

.document-item:hover .menu-btn {
  opacity: 1;
}

.menu-btn:hover {
  color: #666;
}
</style>