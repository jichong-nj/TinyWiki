<template>
  <div class="permissions">
    <div class="perm-header">
      <el-button type="primary" @click="showAssignModal = true">分配权限</el-button>
    </div>
    
    <el-table :data="permissions" border>
      <el-table-column prop="user" label="用户" />
      <el-table-column prop="directory" label="目录" />
      <el-table-column prop="role" label="角色">
        <template #default="scope">
          <el-tag :type="getRoleTagType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button text @click="editPermission(scope.row)">编辑</el-button>
          <el-button text type="danger" @click="deletePermission(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAssignModal" title="分配权限" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户">
          <el-select v-model="form.user" placeholder="选择用户">
            <el-option v-for="user in users" :key="user.id" :label="user.email" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="目录">
          <el-select v-model="form.directory" placeholder="选择目录">
            <el-option v-for="dir in directories" :key="dir.id" :label="dir.name" :value="dir.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" placeholder="选择角色">
            <el-option value="admin" label="目录管理员" />
            <el-option value="editor" label="编辑者" />
            <el-option value="viewer" label="查看者" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAssignModal = false">取消</el-button>
        <el-button type="primary" @click="savePermission">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from '../../axios'

interface Permission {
  id: number
  user: string
  directory: string
  role: string
  created_at: string
}

interface User {
  id: number
  email: string
}

interface Directory {
  id: number
  name: string
}

const permissions = ref<Permission[]>([])
const users = ref<User[]>([])
const directories = ref<Directory[]>([])
const showAssignModal = ref(false)

const form = reactive({
  user: '',
  directory: '',
  role: ''
})

function getRoleTagType(role: string) {
  switch (role) {
    case 'admin': return 'primary'
    case 'editor': return 'success'
    default: return 'info'
  }
}

function getRoleText(role: string) {
  switch (role) {
    case 'admin': return '目录管理员'
    case 'editor': return '编辑者'
    default: return '查看者'
  }
}

function loadPermissions() {
  axios.get('/documents/permissions/')
    .then(response => {
      permissions.value = response.data
    })
    .catch(error => console.error('加载权限失败:', error))
}

function loadUsers() {
  axios.get('/auth/users/')
    .then(response => {
      users.value = response.data
    })
    .catch(error => console.error('加载用户失败:', error))
}

function loadDirectories() {
  axios.get('/documents/directories/')
    .then(response => {
      directories.value = response.data
    })
    .catch(error => console.error('加载目录失败:', error))
}

function savePermission() {
  axios.post('/documents/permissions/', form)
    .then(() => {
      showAssignModal.value = false
      form.user = ''
      form.directory = ''
      form.role = ''
      loadPermissions()
    })
    .catch(error => console.error('分配权限失败:', error))
}

function editPermission(perm: Permission) {
  form.user = perm.user
  form.directory = perm.directory
  form.role = perm.role
  showAssignModal.value = true
}

function deletePermission(id: number) {
  if (confirm('确定要删除这个权限吗？')) {
    axios.delete(`/documents/permissions/${id}/`)
      .then(() => {
        loadPermissions()
      })
      .catch(error => console.error('删除权限失败:', error))
  }
}

onMounted(() => {
  loadPermissions()
  loadUsers()
  loadDirectories()
})
</script>

<style scoped>
.permissions {
  padding: 20px;
}

.perm-header {
  margin-bottom: 20px;
}
</style>