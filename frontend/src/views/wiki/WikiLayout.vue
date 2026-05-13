<template>
  <div class="wiki-layout">
    <header class="wiki-header">
      <div class="header-left">
        <h1 class="wiki-title">📖 {{ siteName }}</h1>
      </div>
      <div class="header-center">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索文档..."
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
        <button class="ai-btn" @click="showChat = true">
          <span class="ai-icon">🤖</span>
          <span>AI 助手</span>
        </button>
      </div>
    </header>

    <div v-if="selectedKB" class="wiki-content">
      <nav class="directory-tabs">
        <div 
          v-for="dir in directories" 
          :key="dir.id"
          class="tab-item"
          :class="{ active: selectedDirectory?.id === dir.id }"
          @click="selectDirectory(dir)"
        >
          {{ dir.name }}
        </div>
      </nav>

      <div v-if="showSearchResults && searchResults.length" class="search-results-overlay" @click="showSearchResults = false">
        <div class="search-results-panel" @click.stop>
          <div class="search-results-header">
            <div class="search-header-left">
              <span class="search-icon">🔍</span>
              <h3>搜索结果</h3>
            </div>
            <div class="search-header-right">
              <span class="results-count">共 {{ searchResults.length }} 条结果</span>
              <button class="close-btn" @click="showSearchResults = false">×</button>
            </div>
          </div>
          <div class="search-results-list">
            <div 
              v-for="result in searchResults" 
              :key="result.id"
              class="search-result-item"
              @click="selectSearchResult(result)"
            >
              <div class="result-title">{{ result.title }}</div>
              <div class="result-path">
                <span class="path-icon">📁</span>
                <span class="path-text">{{ result.path || '根目录' }}</span>
              </div>
              <div class="result-filename">
                <span class="file-icon">📄</span>
                <span>{{ result.filename }}</span>
              </div>
              <div v-if="result.summary" class="result-summary">
                {{ result.summary }}
              </div>
              <div class="result-footer">
                <span class="result-date">{{ formatTime(result.updated_at) }}</span>
                <span v-if="result.rank" class="result-score">相关度: {{ (result.rank * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="wiki-main-content">
        <aside class="sidebar">
          <div class="sidebar-header">
            <span class="sidebar-title">文件目录</span>
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
                  'is-directory': item.type === 'folder', 
                  active: selectedFile?.id === item.id
                }"
                @click="handleItemClick(item)"
              >
                <span class="tree-icon" v-if="item.type === 'folder'">
                  <span @click.stop="toggleExpand(item.id)">{{ item.expanded ? '▼' : '▶' }}</span>
                </span>
                <span class="tree-icon" v-else>📄</span>
                <span class="tree-label">{{ item.name }}</span>
              </div>
              
              <div 
                v-if="item.type === 'folder' && item.expanded && item.children?.length" 
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
                      'is-directory': child.type === 'folder', 
                      active: selectedFile?.id === child.id
                    }"
                    @click="handleItemClick(child)"
                  >
                    <span class="tree-icon" v-if="child.type === 'folder'">
                      <span @click.stop="toggleExpand(child.id)">{{ child.expanded ? '▼' : '▶' }}</span>
                    </span>
                    <span class="tree-icon" v-else>📄</span>
                    <span class="tree-label">{{ child.name }}</span>
                  </div>
                  
                  <div 
                    v-if="child.type === 'folder' && child.expanded && child.children?.length" 
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
                          'is-directory': subChild.type === 'folder',
                          active: selectedFile?.id === subChild.id
                        }"
                        @click="handleItemClick(subChild)"
                      >
                        <span class="tree-icon" v-if="subChild.type === 'folder'">📁</span>
                        <span class="tree-icon" v-else>📄</span>
                        <span class="tree-label">{{ subChild.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <main class="content-area" ref="contentAreaRef">
          <div v-if="selectedFile" class="document-viewer">
            <div class="document-header">
              <div class="breadcrumbs">
                <span v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
                  <a v-if="crumb.url" @click="navigateTo(crumb.url)">{{ crumb.name }}</a>
                  <span v-else>{{ crumb.name }}</span>
                  <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-separator">/</span>
                </span>
              </div>
              <h1 class="document-title">{{ selectedFile.name }}</h1>
              <div class="document-meta">
                <span>📅 更新于 {{ formatTime(selectedFile.updated_at) }}</span>
              </div>
            </div>
            <article class="document-content" v-html="renderedContent" @scroll="handleContentScroll"></article>
          </div>
          
          <div v-else class="empty-state">
            <span class="empty-icon">📚</span>
            <h2>选择文档开始浏览</h2>
            <p>从左侧目录选择一个文档进行查看</p>
          </div>
        </main>

        <aside class="toc-panel" :class="{ collapsed: tocCollapsed }">
          <div class="toc-header">
            <span class="toc-title">文档目录</span>
            <button class="toc-toggle" @click="tocCollapsed = !tocCollapsed">
              {{ tocCollapsed ? '▶' : '◀' }}
            </button>
          </div>
          <div v-if="!tocCollapsed && tocItems.length" class="toc-content">
            <nav class="toc-nav">
              <ul>
                <li 
                  v-for="(item, index) in tocItems" 
                  :key="index"
                  class="toc-item"
                  :class="{ active: activeTocItem === item.id, [`level-${item.level}`]: true }"
                  @click="scrollToHeading(item.id)"
                >
                  {{ item.text }}
                </li>
              </ul>
            </nav>
          </div>
        </aside>
      </div>
    </div>

    <div v-else class="no-kb-selected">
      <div class="no-kb-content">
        <span class="no-kb-icon">📋</span>
        <h2>请选择一个知识库</h2>
        <p>从顶部下拉菜单中选择要浏览的知识库</p>
      </div>
    </div>
    
    <!-- AI Chat -->
    <AIChat v-model="showChat" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from '../../axios'
import { marked } from 'marked'
import AIChat from '../../components/AIChat.vue'

const showChat = ref(false)

// 配置marked
marked.setOptions({
  breaks: true,
  gfm: true
})

// 创建自定义渲染器
const renderer = new marked.Renderer()
const headings: TocItem[] = []

// 重写标题渲染，添加id并收集标题
renderer.heading = function({ text, depth, raw }: any) {
  const id = `h-${raw.toLowerCase().replace(/\s+/g, '-').replace(/[^\w\-]/g, '')}`
  headings.push({ id, text, level: depth })
  return `<h${depth} id="${id}">${text}</h${depth}>`
}

// 重写代码块渲染，支持语言标识
renderer.code = function({ text, lang = '' }: any) {
  const language = lang || 'text'
  
  // HTML 转义
  const escapeHtml = (str: string) => {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
  }
  
  // 简单渲染，不使用高亮
  return `<pre><code class="language-${language}">${escapeHtml(text)}</code></pre>`
}

interface KnowledgeBase {
  id: number
  name: string
  description?: string
}

interface Directory {
  id: number
  name: string
  knowledge_base: number
}

interface TreeItem {
  id: number
  name: string
  type: 'document' | 'folder'
  expanded?: boolean
  children?: TreeItem[]
  directory_id?: number
  folder_id?: number
  updated_at?: string
}

interface TocItem {
  id: string
  text: string
  level: number
}

const siteName = ref('TinyWiki')
const searchQuery = ref('')
const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedKB = ref<KnowledgeBase | null>(null)
const directories = ref<Directory[]>([])
const selectedDirectory = ref<Directory | null>(null)
const selectedFile = ref<{ id: number; name: string; updated_at: string; directory_id?: number; folder_id?: number } | null>(null)
const renderedContent = ref('')
const tocCollapsed = ref(false)
const tocItems = ref<TocItem[]>([])
const activeTocItem = ref('')
const contentAreaRef = ref<HTMLElement | null>(null)

const expandedNodes = ref(new Set<number>())

const treeData = computed(() => {
  if (!selectedDirectory.value) return []
  
  const buildTree = (items: any[], parentId?: number): TreeItem[] => {
    return items
      .filter(item => item.parent === parentId)
      .map(item => ({
        id: item.id,
        name: item.name,
        type: item.type === 'folder' ? 'folder' : 'document',
        expanded: expandedNodes.value.has(item.id),
        children: item.type === 'folder' ? buildTree(items, item.id) : undefined,
        directory_id: item.directory_id,
        folder_id: item.folder_id,
        updated_at: item.updated_at
      }))
  }
  
  return buildTree(currentTreeItems.value)
})

const currentTreeItems = ref<any[]>([])

const breadcrumbs = computed(() => {
  if (!selectedFile.value) return []
  
  const crumbs = []
  
  if (selectedKB.value) {
    crumbs.push({ name: selectedKB.value.name, url: null })
  }
  
  if (selectedDirectory.value) {
    crumbs.push({ name: selectedDirectory.value.name, url: null })
  }
  
  if (selectedFile.value) {
    crumbs.push({ name: selectedFile.value.name, url: null })
  }
  
  return crumbs
})

onMounted(async () => {
  await loadKnowledgeBases()
})

const loadKnowledgeBases = async () => {
  try {
    const response = await axios.get('/documents/knowledge-bases/')
    knowledgeBases.value = response.data
    if (knowledgeBases.value.length > 0) {
      selectedKB.value = knowledgeBases.value[0]
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

watch(selectedKB, async (newKB) => {
  if (newKB) {
    await onKBChange()
  } else {
    directories.value = []
    currentTreeItems.value = []
  }
})

const onKBChange = async () => {
  // 重置所有状态
  selectedDirectory.value = null
  selectedFile.value = null
  renderedContent.value = ''
  tocItems.value = []
  currentTreeItems.value = []
  expandedNodes.value.clear()

  if (selectedKB.value) {
    await loadDirectories()
    // loadDirectories() 已经会自动选择第一个目录，watch(selectedDirectory) 会自动调用 loadTree()
  }
}

const loadDirectories = async () => {
  if (!selectedKB.value) return
  
  try {
    const response = await axios.get('/documents/directories/', {
      params: { knowledge_base: selectedKB.value.id }
    })
    directories.value = response.data
    if (directories.value.length > 0) {
      selectedDirectory.value = directories.value[0]
    }
  } catch (error) {
    console.error('Failed to load directories:', error)
  }
}

const selectDirectory = async (dir: Directory) => {
  selectedDirectory.value = dir
  selectedFile.value = null
  renderedContent.value = ''
  tocItems.value = []
  await loadTree()
}

const loadTree = async () => {
    if (!selectedKB.value || !selectedDirectory.value) return
    
    try {
        const response = await axios.get(`/documents/knowledge-bases/${selectedKB.value.id}/tree/`, {
          params: { directory: selectedDirectory.value.id }
        })
        const flatItems: any[] = []
        let firstDocument: any = null
        
        const flatten = (items: any[], parentId?: number) => {
            items.forEach(item => {
                const itemData = {
                    id: item.id,
                    name: item.name,
                    type: item.type,
                    parent: parentId,
                    directory_id: selectedDirectory.value?.id,
                    folder_id: item.type === 'folder' ? item.id : undefined,
                    updated_at: item.updated_at
                }
                flatItems.push(itemData)

                if (item.type === 'document' && !firstDocument) {
                    firstDocument = itemData
                }

                if (item.children?.length) {
                    flatten(item.children, item.id)
                }
            })
        }

        const rootNodes = Array.isArray(response.data)
          ? response.data.flatMap((d: any) => d.children || [])
          : []
        flatten(rootNodes)
        currentTreeItems.value = flatItems

        if (firstDocument && !selectedFile.value) {
            await handleItemClick(firstDocument)
        }
    } catch (error) {
        console.error('Failed to load tree:', error)
    }
}

const toggleExpand = (id: number) => {
  if (expandedNodes.value.has(id)) {
    expandedNodes.value.delete(id)
  } else {
    expandedNodes.value.add(id)
  }
}

const handleItemClick = async (item: TreeItem) => {
  if (item.type === 'document') {
    selectedFile.value = {
      id: item.id,
      name: item.name,
      updated_at: item.updated_at || '',
      directory_id: item.directory_id,
      folder_id: item.folder_id
    }
    await loadFileContent(item.id)
  } else if (item.type === 'folder') {
    toggleExpand(item.id)
  }
}

const loadFileContent = async (fileId: number) => {
  try {
    const response = await axios.get(`/documents/documents/${fileId}/`)
    const content = response.data.content || ''
    renderedContent.value = markdownToHtml(content)
    extractToc(content)
  } catch (error) {
    console.error('Failed to load file content:', error)
  }
}

const markdownToHtml = (content: string): string => {
  headings.length = 0 // 清空标题数组
  const html = marked.parse(content, { renderer }) as string
  tocItems.value = headings.filter(h => h.level <= 3) // 只保留h1-h3
  return html
}

const extractToc = (_content: string) => {
  // 提取目录的逻辑已经移到markdownToHtml中了
  // 这里保留函数名避免引用错误
}

const scrollToHeading = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const handleContentScroll = () => {
  const headings = document.querySelectorAll('h1, h2, h3')
  let currentHeading = ''
  
  headings.forEach((heading) => {
    const rect = heading.getBoundingClientRect()
    if (rect.top <= 100) {
      currentHeading = heading.id
    }
  })
  
  activeTocItem.value = currentHeading
}

interface SearchResult {
  id: number
  title: string
  filename: string
  content: string
  updated_at: string
  path?: string
  summary?: string
  rank?: number
}

const searchResults = ref<SearchResult[]>([])
const showSearchResults = ref(false)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    showSearchResults.value = false
    searchResults.value = []
    return
  }
  
  try {
    const response = await axios.get('/documents/documents/search/', {
      params: {
        q: searchQuery.value,
        directory: selectedDirectory.value?.id
      }
    })
    searchResults.value = response.data
    showSearchResults.value = true
  } catch (error) {
    console.error('Search failed:', error)
  }
}

const selectSearchResult = async (result: SearchResult) => {
  selectedFile.value = {
    id: result.id,
    name: result.title,
    updated_at: result.updated_at
  }
  showSearchResults.value = false
  searchQuery.value = ''
  await loadFileContent(result.id)
}

const formatTime = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const navigateTo = (url: string | null) => {
  if (url) {
    console.log('Navigate to:', url)
  }
}

watch(selectedDirectory, () => {
  loadTree()
})
</script>

<style scoped>
.wiki-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
  overflow: hidden;
}

.wiki-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  height: 60px;
}

.header-left {
  flex: 1;
}

.wiki-title {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.kb-select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  min-width: 200px;
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.ai-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.ai-icon {
  font-size: 18px;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f1f3f4;
  border-radius: 24px;
  padding: 8px 16px;
  width: 300px;
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

.wiki-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.directory-tabs {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid #e9ecef;
  overflow-x: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.tab-item {
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #5a6a7a;
  background: #ffffff;
  border: 1px solid #e0e5eb;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
}

.tab-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, #3498db, #667eea);
  border-radius: 0 0 4px 4px;
  transition: width 0.3s ease;
}

.tab-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.15);
  color: #2c3e50;
  border-color: #d0d8e0;
}

.tab-item:hover::before {
  width: 60%;
}

.tab-item.active {
  background: linear-gradient(135deg, #3498db 0%, #667eea 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.35);
}

.tab-item.active::before {
  width: 80%;
  background: rgba(255, 255, 255, 0.4);
}

.wiki-main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
  flex-shrink: 0;
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

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-width: 0;
  background: #f8f9fa;
}

.document-viewer {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.document-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background: #fafafa;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #6c757d;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item a {
  color: #3498db;
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  margin: 0 4px;
}

.document-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.document-meta {
  font-size: 13px;
  color: #6c757d;
}

.document-content {
  padding: 24px;
  line-height: 1.8;
  color: #333;
}

.document-content h1 {
  font-size: 24px;
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #3498db;
  color: #2c3e50;
}

.document-content h2 {
  font-size: 20px;
  margin: 20px 0 12px 0;
  color: #2c3e50;
}

.document-content h3 {
  font-size: 16px;
  margin: 16px 0 10px 0;
  color: #2c3e50;
}

.document-content p {
  margin: 12px 0;
}

.document-content ul,
.document-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.document-content li {
  margin: 6px 0;
}

.document-content a {
  color: #3498db;
  text-decoration: none;
}

.document-content a:hover {
  text-decoration: underline;
}

.document-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.document-content pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 16px 0;
}

.document-content pre code {
  background: none;
  padding: 0;
  color: #ccc;
}

.document-content blockquote {
  border-left: 4px solid #3498db;
  padding-left: 16px;
  margin: 16px 0;
  color: #6c757d;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 0 4px 4px 0;
}

.document-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.document-content th,
.document-content td {
  border: 1px solid #ddd;
  padding: 10px 12px;
  text-align: left;
}

.document-content th {
  background: #f8f9fa;
  font-weight: 600;
}

.document-content img {
  max-width: 100%;
  width: auto;
  height: auto;
  display: block;
  border-radius: 4px;
  margin: 16px 0;
  object-fit: contain;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  color: #6c757d;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
}

.empty-state h2 {
  font-size: 24px;
  margin: 0 0 12px 0;
  color: #2c3e50;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.toc-panel {
  width: 240px;
  background: #ffffff;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
  flex-shrink: 0;
}

.toc-panel.collapsed {
  width: 40px;
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
  flex-shrink: 0;
}

.toc-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.toc-toggle {
  background: none;
  border: none;
  font-size: 12px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.toc-toggle:hover {
  background: #e9ecef;
}

.toc-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.toc-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  padding: 6px 8px;
  cursor: pointer;
  font-size: 13px;
  color: #6c757d;
  border-radius: 4px;
  transition: all 0.2s;
}

.toc-item:hover {
  background: #f1f3f4;
  color: #2c3e50;
}

.toc-item.active {
  background: #e3f2fd;
  color: #1976d2;
}

.toc-item.level-2 {
  padding-left: 20px;
}

.toc-item.level-3 {
  padding-left: 36px;
}

.no-kb-selected {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8f9fa;
}

.search-results-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.search-results-panel {
  width: 800px;
  max-width: 95vw;
  height: 70vh;
  max-height: 800px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
}

.search-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-header-left .search-icon {
  font-size: 20px;
}

.search-results-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.search-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.results-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.search-results-header .close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.2s;
  line-height: 1;
}

.search-results-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.search-results-list {
  flex: 1;
  overflow-y: auto;
}

.search-result-item {
  padding: 18px 24px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.search-result-item:hover {
  background: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.result-path {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #667eea;
  margin-bottom: 6px;
}

.path-icon, .file-icon {
  font-size: 14px;
}

.path-text {
  opacity: 0.9;
}

.result-filename {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6c757d;
  margin-bottom: 10px;
}

.result-summary {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.result-score {
  padding: 2px 8px;
  background: #e8f0fe;
  color: #667eea;
  border-radius: 4px;
  font-size: 12px;
}

/* Prism.js 代码高亮样式 */
pre[class*="language-"] {
  background: #2d2d2d;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 16px 0;
}

code[class*="language-"],
pre[class*="language-"] {
  color: #ccc;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.token.comment,
.token.block-comment,
.token.prolog,
.token.doctype,
.token.cdata {
  color: #999;
}

.token.punctuation {
  color: #ccc;
}

.token.tag,
.token.attr-name,
.token.namespace,
.token.deleted {
  color: #e2777a;
}

.token.function-name {
  color: #6196cc;
}

.token.boolean,
.token.number,
.token.function {
  color: #f08d49;
}

.token.property,
.token.class-name,
.token.constant,
.token.symbol {
  color: #f8c555;
}

.token.selector,
.token.important,
.token.atrule,
.token.keyword,
.token.builtin {
  color: #cc99cd;
}

.token.string,
.token.char,
.token.attr-value,
.token.regex,
.token.variable {
  color: #7ec699;
}

.token.operator,
.token.entity,
.token.url {
  color: #67cdcc;
}

.token.important,
.token.bold {
  font-weight: bold;
}

.token.italic {
  font-style: italic;
}

.token.entity {
  cursor: help;
}

.token.inserted {
  color: green;
}

/* 修正markdown内容样式 */
.document-content h1,
.document-content h2,
.document-content h3 {
  margin-top: 24px;
  margin-bottom: 12px;
  color: #2c3e50;
  font-weight: 600;
}

.document-content h1 {
  font-size: 28px;
  padding-bottom: 8px;
  border-bottom: 2px solid #3498db;
}

.document-content h2 {
  font-size: 22px;
}

.document-content h3 {
  font-size: 18px;
}

.document-content p {
  margin: 12px 0;
  line-height: 1.8;
}

.document-content ul,
.document-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.document-content li {
  margin: 6px 0;
  line-height: 1.6;
}

.document-content a {
  color: #3498db;
  text-decoration: none;
}

.document-content a:hover {
  text-decoration: underline;
}

.document-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.document-content pre code {
  background: transparent;
  padding: 0;
}

.document-content blockquote {
  border-left: 4px solid #3498db;
  padding-left: 16px;
  margin: 16px 0;
  color: #6c757d;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 0 4px 4px 0;
}

.document-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.document-content th,
.document-content td {
  border: 1px solid #ddd;
  padding: 10px 12px;
  text-align: left;
}

.document-content th {
  background: #f8f9fa;
  font-weight: 600;
}

.document-content img {
  max-width: 100%;
  width: auto;
  height: auto;
  display: block;
  border-radius: 4px;
  margin: 16px 0;
  object-fit: contain;
}
</style>

<!-- 全局样式，用于 v-html 渲染的内容 -->
<style>
/* Markdown 渲染内容中的图片限制 */
.document-content img {
  max-width: 100% !important;
  width: auto !important;
  height: auto !important;
  display: block !important;
  border-radius: 4px !important;
  margin: 16px 0 !important;
  object-fit: contain !important;
}
</style>