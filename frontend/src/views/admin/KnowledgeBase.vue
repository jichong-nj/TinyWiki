<template>
  <div class="knowledge-base">
    <div class="kb-header">
      <el-button type="primary" @click="showCreateModal = true">创建知识库</el-button>
    </div>
    
    <el-table :data="knowledgeBases" border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column prop="updated_at" label="更新时间" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button text @click="viewDirectories(scope.row.id)">管理目录</el-button>
          <el-button text @click="editKnowledgeBase(scope.row)">编辑</el-button>
          <el-button text type="danger" @click="deleteKnowledgeBase(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showCreateModal" :title="isEditing ? '编辑知识库' : '创建知识库'" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入知识库描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" @click="saveKnowledgeBase">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showDirectoryModal" title="管理目录" width="600px">
      <div class="directory-management">
        <div class="directory-list">
          <el-table :data="directories" border>
            <el-table-column prop="name" label="目录名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button text @click="editDirectory(scope.row)">编辑</el-button>
                <el-button text type="danger" @click="deleteDirectory(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="directory-form">
          <el-form :model="directoryForm" label-width="80px">
            <el-form-item label="目录名称">
              <el-input v-model="directoryForm.name" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="directoryForm.description" type="textarea" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveDirectory">添加目录</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from '../../axios'

interface KnowledgeBase {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
}

interface Directory {
  id: number
  name: string
  description: string
  knowledge_base: number
}

const knowledgeBases = ref<KnowledgeBase[]>([])
const showCreateModal = ref(false)
const showDirectoryModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const currentKBId = ref<number | null>(null)
const directories = ref<Directory[]>([])

const form = reactive({
  name: '',
  description: ''
})

const directoryForm = reactive({
  name: '',
  description: ''
})

function loadKnowledgeBases() {
  axios.get('/documents/knowledge-bases/')
    .then(response => {
      knowledgeBases.value = response.data
    })
    .catch(error => console.error('加载知识库失败:', error))
}

function saveKnowledgeBase() {
  if (isEditing.value && editingId.value) {
    axios.put(`/documents/knowledge-bases/${editingId.value}/`, form)
      .then(() => {
        showCreateModal.value = false
        loadKnowledgeBases()
      })
      .catch(error => console.error('更新知识库失败:', error))
  } else {
    axios.post('/documents/knowledge-bases/', form)
      .then(() => {
        showCreateModal.value = false
        loadKnowledgeBases()
      })
      .catch(error => console.error('创建知识库失败:', error))
  }
}

function editKnowledgeBase(kb: KnowledgeBase) {
  isEditing.value = true
  editingId.value = kb.id
  form.name = kb.name
  form.description = kb.description
  showCreateModal.value = true
}

function deleteKnowledgeBase(id: number) {
  if (confirm('确定要删除这个知识库吗？')) {
    axios.delete(`/documents/knowledge-bases/${id}/`)
      .then(() => {
        loadKnowledgeBases()
      })
      .catch(error => console.error('删除知识库失败:', error))
  }
}

function viewDirectories(kbId: number) {
  currentKBId.value = kbId
  loadDirectories(kbId)
  showDirectoryModal.value = true
}

function loadDirectories(kbId: number) {
  axios.get('/documents/directories/', { params: { knowledge_base: kbId } })
    .then(response => {
      directories.value = response.data
    })
    .catch(error => console.error('加载目录失败:', error))
}

function saveDirectory() {
  if (!currentKBId.value) return
  
  axios.post('/documents/directories/', {
    name: directoryForm.name,
    description: directoryForm.description,
    knowledge_base: currentKBId.value
  })
    .then(() => {
      directoryForm.name = ''
      directoryForm.description = ''
      loadDirectories(currentKBId.value!)
    })
    .catch(error => console.error('创建目录失败:', error))
}

function editDirectory(dir: Directory) {
  directoryForm.name = dir.name
  directoryForm.description = dir.description
}

function deleteDirectory(id: number) {
  if (confirm('确定要删除这个目录吗？')) {
    axios.delete(`/documents/directories/${id}/`)
      .then(() => {
        if (currentKBId.value) {
          loadDirectories(currentKBId.value)
        }
      })
      .catch(error => console.error('删除目录失败:', error))
  }
}

onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.knowledge-base {
  padding: 20px;
}

.kb-header {
  margin-bottom: 20px;
}

.directory-management {
  display: flex;
  gap: 20px;
}

.directory-list {
  flex: 1;
}

.directory-form {
  width: 280px;
}
</style>