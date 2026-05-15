<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="logo">
        <h2>TinyWiki</h2>
      </div>
      <el-menu :default-active="activeMenu" class="sidebar-menu" router>
        <el-menu-item index="/">
          <el-icon><Document /></el-icon>
          <span>文档</span>
        </el-menu-item>
        <el-menu-item index="/knowledge-base">
          <el-icon><FolderOpened /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/permissions">
          <el-icon><Lock /></el-icon>
          <span>权限管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>大模型配置</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <el-button type="primary" @click="switchToWiki">切换 Wiki</el-button>
        <el-button type="primary" plain @click="handleLogout">退出登录</el-button>
      </div>
    </aside>
    
    <main class="main-content">
      <header class="top-header">
        <div class="header-left">
          <el-select v-model="currentKnowledgeBase" placeholder="选择知识库" @change="onKnowledgeBaseChange">
            <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
        </div>
        <div class="header-center">
          <el-input v-model="searchQuery" placeholder="搜索文档" prefix-icon="Search" />
        </div>
        <div class="header-right">
          <el-dropdown>
            <el-button text>
              {{ authStore.user?.username }}
              <el-icon class="el-icon--right"><CaretBottom /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <router-view class="router-view-content" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from '../../axios'
import { Document, FolderOpened, Setting, CaretBottom, Lock } from '@element-plus/icons-vue'

interface KnowledgeBase {
  id: number
  name: string
  description: string
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const knowledgeBases = ref<KnowledgeBase[]>([])
const currentKnowledgeBase = ref<number | null>(null)
const searchQuery = ref('')

const activeMenu = computed(() => route.path)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function switchToWiki() {
  router.push('/wiki')
}

function loadKnowledgeBases() {
  axios.get('/documents/knowledge-bases/')
    .then(response => {
      knowledgeBases.value = response.data
      if (knowledgeBases.value.length > 0) {
        // 优先检查路由query中是否有kb参数
        if (route.query.kb) {
          const kbFromQuery = Number(route.query.kb)
          const validKb = knowledgeBases.value.find(kb => kb.id === kbFromQuery)
          if (validKb) {
            console.log('AdminLayout: 从query设置知识库:', kbFromQuery)
            currentKnowledgeBase.value = kbFromQuery
            // 立即通知DocumentList
            window.dispatchEvent(new CustomEvent('knowledgeBaseChanged', { 
              detail: { knowledgeBaseId: currentKnowledgeBase.value } 
            }))
          } else if (currentKnowledgeBase.value === null) {
            currentKnowledgeBase.value = knowledgeBases.value[0].id
          }
        } else if (currentKnowledgeBase.value === null) {
          currentKnowledgeBase.value = knowledgeBases.value[0].id
        }
      }
    })
    .catch(error => console.error('加载知识库失败:', error))
}

function onKnowledgeBaseChange() {
  console.log('AdminLayout: 知识库切换到:', currentKnowledgeBase.value)
  // 通过自定义事件通知子组件
  window.dispatchEvent(new CustomEvent('knowledgeBaseChanged', { 
    detail: { knowledgeBaseId: currentKnowledgeBase.value } 
  }))
}

function handleDocumentListKnowledgeBaseChange(event: CustomEvent) {
  const newKnowledgeBaseId = event.detail.knowledgeBaseId
  console.log('AdminLayout: 收到DocumentList知识库切换事件:', newKnowledgeBaseId)
  if (currentKnowledgeBase.value !== newKnowledgeBaseId) {
    currentKnowledgeBase.value = newKnowledgeBaseId
  }
}

onMounted(() => {
  loadKnowledgeBases()
  // 监听来自DocumentList的知识库切换事件
  window.addEventListener('documentListKnowledgeBaseChanged', handleDocumentListKnowledgeBaseChange as EventListener)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('documentListKnowledgeBaseChanged', handleDocumentListKnowledgeBaseChange as EventListener)
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.sidebar {
  width: 200px;
  background: #2a2a3a;
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #3a3a4a;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  color: #667eea;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #b0b0c0;
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #3a3a4a;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #667eea;
  color: white;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #3a3a4a;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.sidebar-footer button {
  width: 100%;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  margin-left: 200px;
}

.router-view-content {
  flex: 1;
  overflow: hidden;
}

.top-header {
  height: 60px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  width: 200px;
}

.header-center {
  flex: 1;
  max-width: 400px;
  margin: 0 40px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}


</style>