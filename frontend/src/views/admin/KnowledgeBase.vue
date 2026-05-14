<template>
  <div class="knowledge-base">
    <div class="kb-header">
      <el-button type="primary" @click="showCreateModal = true">创建知识库</el-button>
    </div>
    
    <draggable 
      v-model="knowledgeBases" 
      item-key="id" 
      @end="handleKnowledgeBasesReorder"
      handle=".drag-handle"
      class="kb-list"
    >
      <template #item="{ element }">
        <div class="kb-item">
          <div class="drag-handle">
            <el-icon><MoreFilled /></el-icon>
          </div>
          <div class="kb-info">
            <div class="kb-name">{{ element.name }}</div>
            <div class="kb-desc">{{ element.description }}</div>
          </div>
          <div class="kb-meta">
            <span class="kb-time">创建: {{ formatDateTime(element.created_at) }}</span>
            <span class="kb-time">更新: {{ formatDateTime(element.updated_at) }}</span>
          </div>
          <div class="kb-actions">
            <el-button text @click="viewDirectories(element.id)">管理目录</el-button>
            <el-button text @click="editKnowledgeBase(element)">编辑</el-button>
            <el-button text type="danger" @click="deleteKnowledgeBase(element.id)">删除</el-button>
          </div>
        </div>
      </template>
    </draggable>
    
    <el-dialog v-model="showCreateModal" :title="isEditing ? '编辑知识库' : '创建知识库'" width="400px">
      <el-form :model="form" label-width="80px" @submit.prevent="saveKnowledgeBase">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入知识库描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" native-type="submit" @click="saveKnowledgeBase">保存</el-button>
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
import { MoreFilled } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

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
let isDragging = false

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

async function handleKnowledgeBasesReorder() {
  if (isDragging) return
  isDragging = true
  
  const orderedIds = knowledgeBases.value.map(kb => kb.id)
  
  try {
    await axios.post('/documents/knowledge-bases/reorder/', {
      ordered_ids: orderedIds
    })
  } catch (error: any) {
    console.error('知识库排序失败:', error)
  } finally {
    isDragging = false
  }
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

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
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

.kb-list {
  min-height: 100px;
}

.kb-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  margin-bottom: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.kb-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  padding: 4px;
  color: #999;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s;
  margin-right: 12px;
}

.kb-item:hover .drag-handle {
  opacity: 1;
}

.drag-handle:hover {
  color: #666;
}

.kb-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.kb-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex-shrink: 0;
}

.kb-desc {
  font-size: 14px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.kb-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-right: 20px;
}

.kb-time {
  font-size: 12px;
  color: #999;
}

.kb-actions {
  display: flex;
  gap: 8px;
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

.sortable-chosen {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.sortable-ghost {
  opacity: 0.5;
}
</style>