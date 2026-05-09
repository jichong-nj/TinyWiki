<template>
  <div class="wiki-browser">
    <div class="wiki-header">
      <div class="header-left">
        <button class="menu-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
          ☰
        </button>
        <h1 class="wiki-title">📖 {{ selectedKB?.name || 'Wiki' }}</h1>
      </div>
      <div class="header-center">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索知识库..."
            @keyup.enter="handleSearch"
          />
        </div>
      </div>
      <div class="header-right">
        <select v-model="selectedKB" @change="onKBChange" class="kb-select">
          <option :value="null">选择知识库</option>
          <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb">
            {{ kb.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div class="wiki-content">
      <aside class="wiki-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header" v-if="!sidebarCollapsed">
          <span class="sidebar-title">目录</span>
          <button class="sidebar-refresh" @click="loadTree">🔄</button>
        </div>
        
        <div class="sidebar-tree">
          <div 
            v-for="item in treeData" 
            :key="item.id"
            class="tree-node"
          >
            <div 
              class="tree-item"
              :class="{ 
                'is-file': item.type === 'file', 
                'is-directory': item.type === 'directory',
                active: selectedFile?.id === item.id
              }"
              @click="handleItemClick(item)"
            >
              <span class="tree-icon" v-if="item.type === 'directory' && !sidebarCollapsed">
                <span @click.stop="toggleExpand(item.id)">{{ item.expanded ? '▼' : '▶' }}</span>
              </span>
              <span class="tree-icon" v-else-if="item.type === 'directory'">📁</span>
              <span class="tree-icon" v-else>📄</span>
              <span class="tree-label">{{ sidebarCollapsed ? '' : item.name }}</span>
            </div>
            
            <div 
              v-if="item.type === 'directory' && item.expanded && item.children?.length" 
              class="tree-children"
            >
              <div 
                v-for="child in item.children" 
                :key="child.id"
                class="tree-node"
              >
                <div 
                  class="tree-item"
                  :class="{ 
                    'is-file': child.type === 'file', 
                    'is-directory': child.type === 'directory',
                    active: selectedFile?.id === child.id
                  }"
                  @click="handleItemClick(child)"
                >
                  <span class="tree-icon" v-if="child.type === 'directory' && !sidebarCollapsed">
                    <span @click.stop="toggleExpand(child.id)">{{ child.expanded ? '▼' : '▶' }}</span>
                  </span>
                  <span class="tree-icon" v-else-if="child.type === 'directory'">📁</span>
                  <span class="tree-icon" v-else>📄</span>
                  <span class="tree-label">{{ sidebarCollapsed ? '' : child.name }}</span>
                </div>
                
                <div 
                  v-if="child.type === 'directory' && child.expanded && child.children?.length" 
                  class="tree-children"
                >
                  <div 
                    v-for="subChild in child.children" 
                    :key="subChild.id"
                    class="tree-node"
                  >
                    <div 
                      class="tree-item"
                      :class="{ 
                        'is-file': subChild.type === 'file', 
                        active: selectedFile?.id === subChild.id
                      }"
                      @click="handleItemClick(subChild)"
                    >
                      <span class="tree-icon">📄</span>
                      <span class="tree-label">{{ sidebarCollapsed ? '' : subChild.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
      
      <main class="wiki-main">
        <div v-if="selectedFile" class="wiki-article">
          <div class="article-header">
            <h1 class="article-title">{{ selectedFile.name }}</h1>
            <div class="article-meta">
              <span class="meta-item">📅 更新于 {{ formatTime(selectedFile.updated_at) }}</span>
            </div>
          </div>
          <article class="article-content" v-html="renderedContent"></article>
        </div>
        
        <div v-else class="wiki-welcome">
          <div class="welcome-content">
            <span class="welcome-icon">📚</span>
            <h2>欢迎来到 Wiki</h2>
            <p>从左侧目录选择一个文档开始浏览</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from '../axios'

interface KnowledgeBase {
  id: number
  name: string
  files?: Array<{ id: number; name: string; updated_at: string }>
  directories?: Array<any>
}

interface FileItem {
  id: number
  name: string
  type: string
  data?: any
  expanded?: boolean
  children?: FileItem[]
}

const sidebarCollapsed = ref(false)
const searchQuery = ref('')
const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedKB = ref<KnowledgeBase | null>(null)
const selectedFile = ref<{ id: number; name: string; updated_at: string } | null>(null)
const renderedContent = ref('')

const expandedNodes = ref(new Set<number>())

const treeData = computed(() => {
  if (!selectedKB.value) return []
  
  const result: FileItem[] = []
  
  if (selectedKB.value.files?.length) {
    selectedKB.value.files.filter((f: any) => !f.directory).forEach((file: any) => {
      result.push({
        id: file.id,
        name: file.name,
        type: 'file',
        data: file
      })
    })
  }
  
  const buildTree = (dirs: any[]): FileItem[] => {
    return dirs.map((dir: any) => ({
      id: dir.id,
      name: dir.name,
      type: 'directory',
      expanded: expandedNodes.value.has(dir.id),
      children: [
        ...(dir.files || []).map((file: any) => ({
          id: file.id,
          name: file.name,
          type: 'file',
          data: file
        })),
        ...buildTree(dir.children || [])
      ]
    }))
  }
  
  if (selectedKB.value.directories?.length) {
    result.push(...buildTree(selectedKB.value.directories))
  }
  
  return result
})

onMounted(async () => {
  await loadKnowledgeBases()
})

const loadKnowledgeBases = async () => {
  try {
    const response = await axios.get('/knowledge-base/')
    knowledgeBases.value = response.data
    if (knowledgeBases.value.length > 0) {
      selectedKB.value = knowledgeBases.value[0]
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

const loadTree = async () => {
  if (selectedKB.value) {
    try {
      const response = await axios.get(`/knowledge-base/${selectedKB.value.id}/`)
      selectedKB.value = response.data
    } catch (error) {
      console.error('Failed to load tree:', error)
    }
  }
}

const onKBChange = () => {
  selectedFile.value = null
  renderedContent.value = ''
}

const toggleExpand = (id: number) => {
  if (expandedNodes.value.has(id)) {
    expandedNodes.value.delete(id)
  } else {
    expandedNodes.value.add(id)
  }
}

const handleItemClick = async (item: FileItem) => {
  if (item.type === 'file') {
    selectedFile.value = item.data || item as any
    await loadFileContent(selectedFile.value.id)
  } else if (item.type === 'directory') {
    toggleExpand(item.id)
  }
}

const loadFileContent = async (fileId: number) => {
  try {
    const response = await axios.get(`/documents/documents/${fileId}/`)
    const content = response.data.content || ''
    renderedContent.value = markdownToHtml(content)
  } catch (error) {
    console.error('Failed to load file content:', error)
  }
}

const markdownToHtml = (content: string): string => {
  let html = content
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/```(\w+)?\n([\s\S]*?)```/gim, '<pre><code>$2</code></pre>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
    .replace(/\n/gim, '<br>')
  return html
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  console.log('Search:', searchQuery.value)
}

const formatTime = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

watch(selectedKB, () => {
  loadTree()
})
</script>

<style scoped>
.wiki-browser {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}

.wiki-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.menu-toggle:hover {
  background: #f1f3f4;
}

.wiki-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f1f3f4;
  border-radius: 24px;
  padding: 8px 16px;
  width: 400px;
}

.search-icon {
  font-size: 14px;
  margin-right: 10px;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 14px;
  color: #2c3e50;
}

.search-box input::placeholder {
  color: #95a5a6;
}

.header-right {
  display: flex;
  align-items: center;
}

.kb-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.wiki-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.wiki-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.wiki-sidebar.collapsed {
  width: 50px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.sidebar-refresh {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.sidebar-refresh:hover {
  background: #e9ecef;
}

.sidebar-tree {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.tree-node {
  user-select: none;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
}

.wiki-sidebar.collapsed .tree-item {
  padding: 8px;
  justify-content: center;
}

.tree-item:hover {
  background: #f1f3f4;
}

.tree-item.active {
  background: #e3f2fd;
}

.tree-item.active .tree-label {
  color: #1976d2;
  font-weight: 500;
}

.tree-icon {
  font-size: 12px;
  color: #6c757d;
  flex-shrink: 0;
}

.tree-label {
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-children {
  padding-left: 16px;
}

.wiki-sidebar.collapsed .tree-children {
  display: none;
}

.wiki-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.wiki-article {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.article-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background: #fafafa;
}

.article-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.article-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 13px;
  color: #6c757d;
}

.article-content {
  padding: 24px;
  line-height: 1.8;
  color: #333;
}

.article-content h1 {
  font-size: 24px;
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #3498db;
  color: #2c3e50;
}

.article-content h2 {
  font-size: 20px;
  margin: 20px 0 12px 0;
  color: #2c3e50;
}

.article-content h3 {
  font-size: 16px;
  margin: 16px 0 10px 0;
  color: #2c3e50;
}

.article-content p {
  margin: 12px 0;
}

.article-content ul,
.article-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.article-content li {
  margin: 6px 0;
}

.article-content a {
  color: #3498db;
  text-decoration: none;
}

.article-content a:hover {
  text-decoration: underline;
}

.article-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.article-content pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 16px 0;
}

.article-content pre code {
  background: none;
  padding: 0;
  color: #ccc;
}

.article-content blockquote {
  border-left: 4px solid #3498db;
  padding-left: 16px;
  margin: 16px 0;
  color: #6c757d;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 0 4px 4px 0;
}

.article-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.article-content th,
.article-content td {
  border: 1px solid #ddd;
  padding: 10px 12px;
  text-align: left;
}

.article-content th {
  background: #f8f9fa;
  font-weight: 600;
}

.article-content img {
  max-width: 100%;
  border-radius: 4px;
}

.wiki-welcome {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-content {
  text-align: center;
  color: #6c757d;
}

.welcome-icon {
  font-size: 80px;
  display: block;
  margin-bottom: 24px;
}

.welcome-content h2 {
  font-size: 24px;
  margin: 0 0 12px 0;
  color: #2c3e50;
}

.welcome-content p {
  font-size: 14px;
  margin: 0;
}
</style>