<template>
  <div class="permissions">
    <div class="perm-header">
      <h2>用户管理</h2>
    </div>
    
    <el-table :data="users" border style="margin-bottom: 20px">
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column label="角色" width="120">
        <template #default="scope">
          <el-tag :type="getRoleTagType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="加入时间" width="180" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button text @click="openEditUserModal(scope.row)">编辑角色</el-button>
          <el-button text @click="openPermissionModal(scope.row)">分配权限</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 编辑用户角色对话框 -->
    <el-dialog v-model="showEditUserModal" title="编辑用户角色" width="400px">
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名">
          <span>{{ editingUser?.username }}</span>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" placeholder="选择角色" style="width: 100%">
            <el-option value="knowledge_user" label="知识使用者" />
            <el-option value="knowledge_admin" label="知识管理员" />
            <el-option value="superuser" label="超级管理员" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditUserModal = false">取消</el-button>
        <el-button type="primary" @click="saveUserRole">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 分配权限对话框 -->
    <el-dialog v-model="showPermissionModal" title="分配知识库/目录权限" width="800px">
      <div class="permission-form">
        <h4>当前用户: {{ editingUser?.username }}</h4>
        
        <el-divider content-position="left">知识管理权限</el-divider>
        
        <div class="perm-section">
          <div class="perm-label">可管理的知识库</div>
          <el-checkbox-group v-model="selectedKnowledgeBases" class="perm-group">
            <el-checkbox v-for="kb in knowledgeBases" :key="kb.id" :label="kb.id">
              {{ kb.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
        
        <div class="perm-section">
          <div class="perm-label">可管理的目录</div>
          <el-checkbox-group v-model="selectedDirectories" class="perm-group">
            <el-checkbox v-for="dir in directories" :key="dir.id" :label="dir.id">
              {{ dir.name }} <span class="kb-name">({{ dir.kb_name }})</span>
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showPermissionModal = false">取消</el-button>
        <el-button type="primary" @click="savePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from '../../axios'
import { ElMessage } from 'element-plus'

interface User {
  id: number
  username: string
  email: string
  role: string
  date_joined: string
}

interface KnowledgeBase {
  id: number
  name: string
  description: string
}

interface Directory {
  id: number
  name: string
  knowledge_base: number
  kb_name?: string
}

const users = ref<User[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const directories = ref<Directory[]>([])

const showEditUserModal = ref(false)
const showPermissionModal = ref(false)

const editingUser = ref<User | null>(null)

const userForm = reactive({
  role: ''
})

const selectedKnowledgeBases = ref<number[]>([])
const selectedDirectories = ref<number[]>([])

function getRoleTagType(role: string) {
  switch (role) {
    case 'superuser': return 'danger'
    case 'knowledge_admin': return 'primary'
    case 'knowledge_user': return 'info'
    default: return 'info'
  }
}

function getRoleText(role: string) {
  switch (role) {
    case 'superuser': return '超级管理员'
    case 'knowledge_admin': return '知识管理员'
    case 'knowledge_user': return '知识使用者'
    default: return '知识使用者'
  }
}

function loadUsers() {
  axios.get('/auth/users/')
    .then(response => {
      users.value = response.data
    })
    .catch(error => console.error('加载用户失败:', error))
}

function loadKnowledgeBases() {
  axios.get('/documents/knowledge-bases/')
    .then(response => {
      knowledgeBases.value = response.data
      
      // 先加载所有知识库，再加载目录，方便显示目录所属的知识库名称
      loadDirectories()
    })
    .catch(error => console.error('加载知识库失败:', error))
}

function loadDirectories() {
  axios.get('/documents/directories/')
    .then(response => {
      const dirs = response.data
      
      // 给每个目录添加 kb_name
      directories.value = dirs.map((dir: Directory) => {
        const kb = knowledgeBases.value.find(k => k.id === dir.knowledge_base)
        return {
          ...dir,
          kb_name: kb ? kb.name : ''
        }
      })
    })
    .catch(error => console.error('加载目录失败:', error))
}

function openEditUserModal(user: User) {
  editingUser.value = user
  userForm.role = user.role
  showEditUserModal.value = true
}

function openPermissionModal(user: User) {
  editingUser.value = user
  selectedKnowledgeBases.value = []
  selectedDirectories.value = []
  
  // 加载当前用户的权限
  axios.get(`/auth/users/${user.id}/permissions/`)
    .then(response => {
      selectedKnowledgeBases.value = response.data.knowledge_base_ids
      selectedDirectories.value = response.data.directory_ids
    })
    .catch(error => console.error('加载用户权限失败:', error))
  
  showPermissionModal.value = true
}

function saveUserRole() {
  if (!editingUser.value) return
  
  axios.put(`/auth/users/${editingUser.value.id}/`, { role: userForm.role })
    .then(() => {
      ElMessage.success('角色更新成功')
      showEditUserModal.value = false
      loadUsers()
    })
    .catch(error => {
      ElMessage.error('角色更新失败')
      console.error('更新用户角色失败:', error)
    })
}

function savePermissions() {
  if (!editingUser.value) return
  
  axios.put(`/auth/users/${editingUser.value.id}/permissions/`, {
    knowledge_base_ids: selectedKnowledgeBases.value,
    directory_ids: selectedDirectories.value
  })
    .then(() => {
      ElMessage.success('权限保存成功')
      showPermissionModal.value = false
      loadUsers()
    })
    .catch(error => {
      ElMessage.error('权限保存失败')
      console.error('保存权限失败:', error)
    })
}

onMounted(() => {
  loadUsers()
  loadKnowledgeBases()
})
</script>

<style scoped>
.permissions {
  padding: 20px;
}

.perm-header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.perm-header h2 {
  margin: 0;
}

.permission-form h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.perm-section {
  margin-bottom: 20px;
}

.perm-label {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.perm-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.kb-name {
  color: #999;
  font-size: 0.9em;
  margin-left: 5px;
}
</style>
