<template>
  <div class="document-list">
    <div class="list-header">
      <div class="breadcrumb-section">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item v-if="selectedDirectory">
            <span @click="selectDirectory(selectedDirectory)">{{ getCurrentDirectoryName() }}</span>
          </el-breadcrumb-item>
          <el-breadcrumb-item v-for="(folder, index) in breadcrumbFolders" :key="folder.id">
            <span @click="navigateToFolder(index)">{{ folder.name }}</span>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="stats-section">
        <span class="stats-text" @click="showQueueDialog = true">未发布{{ publishingCount }}/{{ draftCount + publishingCount }}条，待分析{{ analyzingCount }}/{{ pendingAnalysisCount + analyzingCount }}条</span>
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
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              导入文件
            </el-button>
            <el-button @click="showZipImportDialog = true">
              <el-icon><Files /></el-icon>
              导入ZIP
            </el-button>
            <el-dropdown trigger="click">
              <el-button type="text">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="createDocument">创建文档</el-dropdown-item>
                  <el-dropdown-item @click="showSubfolderDialog = true">创建子文件夹</el-dropdown-item>
                  <el-dropdown-item @click="bulkPublish">批量发布</el-dropdown-item>
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
              <span class="update-time">{{ formatDateTime(folder.updated_at) }}</span>
              <el-dropdown trigger="click" @click.stop>
                <el-button type="text" class="menu-btn" @click.stop>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editFolder(folder)">修改</el-dropdown-item>
                    <el-dropdown-item @click="openMoveFolderDialog(folder)">移动</el-dropdown-item>
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
            @click="editDocument(doc.id)"
          >
            <div class="item-left">
              <el-icon class="doc-icon"><Document /></el-icon>
              <span class="doc-name">{{ doc.filename }}</span>
            </div>
            
            <div class="item-right">
              <div class="status-tags">
                <el-tag :type="getPublishTagType(doc.publish_status)" size="small">
                  {{ getPublishStatusText(doc.publish_status) }}
                </el-tag>
                <el-tag :type="getAnalysisTagType(doc.analysis_status)" size="small">
                  {{ getAnalysisStatusText(doc.analysis_status) }}
                </el-tag>
              </div>
              <span class="update-time">{{ formatDateTime(doc.updated_at) }}</span>
              <el-dropdown trigger="click" @click.stop>
                <el-button type="text" class="menu-btn" @click.stop>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editDocument(doc.id)">编辑</el-dropdown-item>
                    <el-dropdown-item @click="openMoveDocumentDialog(doc)">移动</el-dropdown-item>
                    <el-dropdown-item @click="deleteDocument(doc.id)">删除</el-dropdown-item>
                    <el-dropdown-item v-if="doc.publish_status === 'draft'" @click="queuePublishDocument(doc.id)">加入发布队列</el-dropdown-item>
                    <el-dropdown-item v-if="doc.publish_status === 'published' && doc.analysis_status !== 'completed'" @click="queueAnalyzeDocument(doc.id)">加入分析队列</el-dropdown-item>
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
    
    <el-dialog title="导入文件" v-model="showImportDialog" @close="cancelImport" width="600px">
      <div class="import-area">
        <div class="upload-drop-zone">
          <el-upload
            ref="uploadRef"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :data="uploadData"
            :multiple="true"
            accept=".md,.txt,.docx,.doc,.pptx,.ppt,.pdf,.xlsx,.xls"
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            class="upload-demo"
          >
            <el-button type="primary" icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="upload-tip">支持 .md, .txt, .docx, .doc, .pptx, .ppt, .pdf, .xlsx, .xls 格式文件，可多选</div>
            </template>
          </el-upload>
        </div>
        
        <div v-if="importFiles.length > 0" class="file-list-container">
          <div class="file-list-header">
            <span class="file-list-title">待上传文件 ({{ importFiles.length }})</span>
            <el-button type="text" size="small" @click="clearAllFiles">清空列表</el-button>
          </div>
          <div class="file-list-scroll">
            <div v-for="(item, index) in importFiles" :key="item.id" class="file-item">
              <div class="file-icon-wrapper">
                <el-icon v-if="item.status === 'pending'" class="file-icon"><Files /></el-icon>
                <el-icon v-else-if="item.status === 'uploading'" class="file-icon uploading"><Loading /></el-icon>
                <el-icon v-else-if="item.status === 'success'" class="file-icon success"><CircleCheck /></el-icon>
                <el-icon v-else class="file-icon error"><CircleClose /></el-icon>
              </div>
              <div class="file-info">
                <span class="file-name">{{ item.file.name }}</span>
                <span v-if="item.errorMessage" class="file-error">{{ item.errorMessage }}</span>
              </div>
              <el-button 
                v-if="item.status === 'pending'" 
                type="text" 
                size="small" 
                class="remove-btn"
                @click="removeImportFile(index)"
              >
                移除
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelImport">取消</el-button>
        <el-button 
          type="primary" 
          @click="startUpload" 
          :loading="uploading"
          :disabled="importFiles.length === 0"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog title="导入ZIP文件" v-model="showZipImportDialog" @close="cancelZipImport" width="700px">
      <div v-if="!zipFileList.length" class="zip-upload-area">
        <el-upload
          ref="zipUploadRef"
          :auto-upload="false"
          :on-change="handleZipFileChange"
          :show-file-list="false"
          accept=".zip"
          class="zip-upload-demo"
          :disabled="parsingZip"
        >
          <el-button type="primary" icon="Upload" :loading="parsingZip" :disabled="parsingZip">
            {{ parsingZip ? '解析中...' : '选择ZIP文件' }}
          </el-button>
          <template #tip>
            <div class="upload-tip">
              选择一个.zip文件，支持包含文件夹结构
              <div class="supported-types">
                <strong>支持的文件类型：</strong>
                .md, .txt, .docx, .doc, .pptx, .ppt, .pdf, .xlsx, .xls
              </div>
            </div>
          </template>
        </el-upload>
        
        <div v-if="zipFile" class="selected-zip-file">
          <el-icon class="zip-icon"><Files /></el-icon>
          <span class="zip-name">{{ zipFile.name }}</span>
          <el-button type="text" size="small" @click="clearZipFile" :disabled="parsingZip">移除</el-button>
        </div>
      </div>
      
      <div v-else class="zip-file-list-area">
        <div class="zip-list-header">
          <div class="zip-list-title">
            <el-icon><Folder /></el-icon>
            <span>ZIP文件内容 (共 {{ zipFileList.length }} 个文件)</span>
          </div>
          <div class="zip-list-actions">
            <el-button type="text" size="small" @click="selectAllZipFiles">
              全选
            </el-button>
            <el-button type="text" size="small" @click="deselectAllZipFiles">
              取消全选
            </el-button>
          </div>
        </div>
        
        <div class="zip-file-list-scroll">
          <div v-for="(file, index) in zipFileList" :key="index" class="zip-file-item">
            <el-checkbox v-model="file.selected" />
            <div class="zip-file-info">
              <div class="zip-file-path">
                <span class="path-text">{{ file.relative_path || '/' }}</span>
                <span class="file-name-text">{{ file.filename }}</span>
              </div>
              <span class="zip-file-size">{{ formatFileSize(file.size) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="cancelZipImport">取消</el-button>
        <el-button 
          type="primary" 
          @click="startZipImport" 
          :loading="importingZip"
          :disabled="!zipFileList.length || !selectedZipFilesCount"
        >
          {{ importingZip ? '导入中...' : `开始导入 (${selectedZipFilesCount}/${zipFileList.length})` }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="showQueueDialog" 
      title="队列文档管理" 
      width="80%" 
      @open="loadQueueDocuments"
    >
      <div class="queue-list-header">
        <div class="queue-list-title">
          <span>共 {{ queueDocuments.length }} 个文档在队列中</span>
        </div>
        <div class="queue-list-actions">
          <el-button type="text" size="small" @click="selectAllQueueDocs">
            全选
          </el-button>
          <el-button type="text" size="small" @click="deselectAllQueueDocs">
            取消全选
          </el-button>
        </div>
      </div>
      
      <div class="queue-document-list">
        <div v-for="doc in queueDocuments" :key="doc.id" class="queue-doc-item">
          <el-checkbox v-model="selectedQueueDocs" :value="doc.id" />
          <div class="queue-doc-info">
            <div class="queue-doc-name">{{ doc.filename }}</div>
            <div class="queue-doc-status">
              <el-tag :type="getPublishTagType(doc.publish_status)" size="small">
                {{ getPublishStatusText(doc.publish_status) }}
              </el-tag>
              <el-tag :type="getAnalysisTagType(doc.analysis_status)" size="small">
                {{ getAnalysisStatusText(doc.analysis_status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showQueueDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="bulkPublishSelected" 
          :loading="bulkPublishing"
          :disabled="!selectedQueueDocs.length"
        >
          {{ bulkPublishing ? '发布中...' : `批量发布 (${selectedQueueDocs.length})` }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 移动文档对话框 -->
    <el-dialog v-model="showMoveDocumentDialog" title="移动文档" width="500px" @open="loadFullTree">
      <div class="move-target-selector">
        <div class="tree-container">
          <div v-for="dir in fullTree" :key="dir.id" class="tree-item">
            <div 
              class="tree-node"
              :class="{ active: selectedMoveTarget?.type === 'directory' && selectedMoveTarget?.id === dir.id }"
              @click="selectMoveTarget(dir)"
            >
              <el-icon><Folder /></el-icon>
              <span>{{ dir.name }}</span>
            </div>
            <div v-if="dir.children && dir.children.length" class="tree-children">
              <TreeNode 
                :nodes="dir.children" 
                :selected-id="selectedMoveTarget?.id"
                :excluded-id="movingDocument?.folder"
                @select="selectMoveTarget"
              />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showMoveDocumentDialog = false">取消</el-button>
        <el-button type="primary" @click="moveDocument" :disabled="!selectedMoveTarget">确定</el-button>
      </template>
    </el-dialog>

    <!-- 移动文件夹对话框 -->
    <el-dialog v-model="showMoveFolderDialog" title="移动文件夹" width="500px" @open="loadFullTree">
      <div class="move-target-selector">
        <div class="tree-container">
          <div v-for="dir in fullTree" :key="dir.id" class="tree-item">
            <div 
              class="tree-node"
              :class="{ active: selectedMoveTarget?.type === 'directory' && selectedMoveTarget?.id === dir.id }"
              @click="selectMoveTarget(dir)"
            >
              <el-icon><Folder /></el-icon>
              <span>{{ dir.name }}</span>
            </div>
            <div v-if="dir.children && dir.children.length" class="tree-children">
              <TreeNode 
                :nodes="dir.children" 
                :selected-id="selectedMoveTarget?.id"
                :excluded-id="movingFolder?.id"
                @select="selectMoveTarget"
              />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showMoveFolderDialog = false">取消</el-button>
        <el-button type="primary" @click="moveFolder" :disabled="!selectedMoveTarget">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, defineComponent, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '../../axios'
import { ElMessage } from 'element-plus'
import { MoreFilled, FolderOpened, Plus, Document, ArrowRight, Files, Loading, CircleCheck, CircleClose, Upload, Folder } from '@element-plus/icons-vue'

// 树节点组件
const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    nodes: {
      type: Array,
      required: true
    },
    selectedId: {
      type: Number,
      default: null
    },
    excludedId: {
      type: Number,
      default: null
    }
  },
  emits: ['select'],
  setup(props, { emit }) {
    const expanded = ref(true);
    
    return () => h('div', {}, 
      props.nodes.map(node => {
        if (props.excludedId && node.id === props.excludedId) {
          return null; // 排除不能选择的节点
        }
        
        return h('div', { key: node.id, class: 'tree-item' }, [
          h('div', {
            class: ['tree-node', { active: props.selectedId === node.id }],
            onClick: () => emit('select', node)
          }, [
            h('div', { class: 'node-content' }, [
              node.type === 'folder' && h(Folder, { class: 'node-icon' }),
              h('span', { class: 'node-name' }, node.name)
            ]),
            node.children && node.children.length > 0 && h(ArrowRight, {
              class: ['expand-icon', { rotated: expanded.value }],
              onClick: (e) => {
                e.stopPropagation();
                expanded.value = !expanded.value;
              }
            })
          ]),
          node.children && node.children.length > 0 && expanded.value && h(TreeNode, {
            nodes: node.children,
            selectedId: props.selectedId,
            excludedId: props.excludedId,
            onSelect: (selectedNode) => emit('select', selectedNode)
          })
        ]);
      })
    );
  }
});

interface Document {
  id: number
  title: string
  filename: string
  publish_status: string
  analysis_status: string
  updated_at: string
  directory: number | null
  folder: number | null
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
  updated_at: string
}

interface KnowledgeBase {
  id: number
  name: string
  description?: string
}

const router = useRouter()
const route = useRoute()

const knowledgeBases = ref<KnowledgeBase[]>([])
const currentKnowledgeBase = ref<number | null>(null)
const documents = ref<Document[]>([])
const directories = ref<Directory[]>([])
const folders = ref<Folder[]>([])
const selectedDirectory = ref<number | null>(null)
const selectedFolder = ref<number | null>(null)
const breadcrumbFolders = ref<Folder[]>([])

// Initialize state from route query parameters
function initStateFromQuery() {
  if (route.query.directory) {
    selectedDirectory.value = Number(route.query.directory)
  }
  if (route.query.folder) {
    selectedFolder.value = Number(route.query.folder)
  }
}
const showAddDialog = ref(false)
const newDirName = ref('')
const editingDir = ref<Directory | null>(null)
const editingFolder = ref<Folder | null>(null)

const showSubfolderDialog = ref(false)
const newSubfolderName = ref('')

const showImportDialog = ref(false)
const showZipImportDialog = ref(false)
const showQueueDialog = ref(false)

// 队列文档相关
const queueDocuments = ref<Document[]>([])
const selectedQueueDocs = ref<number[]>([])
const bulkPublishing = ref(false)

// 移动相关
const showMoveDocumentDialog = ref(false)
const showMoveFolderDialog = ref(false)
const movingDocument = ref<Document | null>(null)
const movingFolder = ref<Folder | null>(null)
const fullTree = ref<any[]>([])
const selectedMoveTarget = ref<any>(null)

interface ImportFileItem {
  id: number
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  errorMessage?: string
}

const importFiles = ref<ImportFileItem[]>([])
let fileIdCounter = 0
const uploadRef = ref()
const uploading = ref(false)

// ZIP 导入相关
interface ZipFileItem {
  filename: string
  path: string
  relative_path: string
  size: number
  selected: boolean
}

const zipFile = ref<File | null>(null)
const zipUploadRef = ref()
const zipFileList = ref<ZipFileItem[]>([])
const parsingZip = ref(false)
const importingZip = ref(false)

const selectedZipFilesCount = computed(() => {
  return zipFileList.value.filter(f => f.selected).length
})

const uploadUrl = computed(() => '/documents/files/upload-multiple/')
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('accessToken')
  return { Authorization: `Bearer ${token}` }
})
const uploadData = computed(() => ({
  directory: selectedDirectory.value || ''
}))

const draftCount = ref(0)
const publishingCount = ref(0)
const pendingAnalysisCount = ref(0)
const analyzingCount = ref(0)
let statsTimer: number | null = null

function updateStats() {
  draftCount.value = documents.value.filter(doc => doc.publish_status === 'draft').length
  publishingCount.value = documents.value.filter(doc => doc.publish_status === 'pending').length
  pendingAnalysisCount.value = documents.value.filter(doc => 
    doc.analysis_status === 'pending'
  ).length
  analyzingCount.value = documents.value.filter(doc => 
    doc.analysis_status === 'analyzing'
  ).length
}

function loadStats() {
  const params: Record<string, any> = {}
  if (currentKnowledgeBase.value) {
    params.knowledge_base = currentKnowledgeBase.value
  }
  axios.get('/documents/documents/stats/', { params })
    .then(response => {
      draftCount.value = response.data.draft_count
      publishingCount.value = response.data.publishing_count
      pendingAnalysisCount.value = response.data.pending_analysis_count
      analyzingCount.value = response.data.analyzing_count
    })
    .catch(error => console.error('加载统计数据失败:', error))
}

function loadKnowledgeBases() {
  console.log('Loading knowledge bases...')
  axios.get('/documents/knowledge-bases/')
    .then(response => {
      console.log('Knowledge bases loaded:', response.data)
      knowledgeBases.value = response.data
      if (knowledgeBases.value.length > 0) {
        if (currentKnowledgeBase.value === null) {
          console.log('Setting default knowledge base:', knowledgeBases.value[0].id)
          currentKnowledgeBase.value = knowledgeBases.value[0].id
        }
        // Load directories and restore saved state
        loadDirectories()
        // Load stats for entire knowledge base
        loadStats()
      }
    })
    .catch(error => console.error('加载知识库失败:', error))
}

function onKnowledgeBaseChange() {
  console.log('DocumentList: 知识库切换到:', currentKnowledgeBase.value)
  selectedDirectory.value = null
  selectedFolder.value = null
  breadcrumbFolders.value = []
  directories.value = []
  folders.value = []
  documents.value = []
  loadDirectories()
  loadStats()
  
  // 通知AdminLayout更新选择器
  window.dispatchEvent(new CustomEvent('documentListKnowledgeBaseChanged', { 
    detail: { knowledgeBaseId: currentKnowledgeBase.value } 
  }))
}

function getPublishTagType(status: string) {
  switch (status) {
    case 'published': return 'success'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

function getPublishStatusText(status: string) {
  switch (status) {
    case 'published': return '已发布'
    case 'pending': return '发布中'
    default: return '未发布'
  }
}

function getAnalysisTagType(status: string) {
  switch (status) {
    case 'completed': return 'success'
    case 'analyzing': return 'warning'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

function getAnalysisStatusText(status: string) {
  switch (status) {
    case 'completed': return '已分析'
    case 'analyzing': return '分析中'
    case 'pending': return '待分析'
    default: return '未分析'
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

function loadDocuments() {
  const params: Record<string, number> = {}
  if (selectedFolder.value) {
    params.folder = selectedFolder.value
  } else if (selectedDirectory.value) {
    params.directory = selectedDirectory.value
  } else {
    documents.value = []
    return
  }
  axios.get('/documents/documents/', { params })
    .then(response => {
      documents.value = response.data
    })
    .catch(error => console.error('加载文档失败:', error))
}

function loadFolders() {
  console.log('loadFolders 被调用')
  if (!selectedDirectory.value) {
    console.log('selectedDirectory.value 为空，清除 folders')
    folders.value = []
    return
  }
  const params: Record<string, any> = {
    directory: selectedDirectory.value
  }
  
  // 只有当selectedFolder有值时才添加parent参数
  if (selectedFolder.value !== null) {
    params.parent = selectedFolder.value
    console.log('添加 parent 参数:', selectedFolder.value)
  } else {
    console.log('不添加 parent 参数（显示顶层文件夹）')
  }
  
  console.log('最终 loadFolders 参数:', params)
  console.log('发送请求到 /documents/folders/')
  axios.get('/documents/folders/', { params })
    .then(response => {
      console.log('loadFolders 响应成功，数据长度:', response.data.length)
      console.log('返回的文件夹数据:', response.data)
      folders.value = response.data
    })
    .catch(error => {
      console.error('加载文件夹失败:', error)
      console.error('错误详情:', error.response?.data)
    })
}

function loadDirectories() {
  console.log('loadDirectories called, currentKnowledgeBase:', currentKnowledgeBase.value)
  if (!currentKnowledgeBase.value) {
    console.log('No knowledge base selected, clearing data')
    directories.value = []
    selectedDirectory.value = null
    documents.value = []
    folders.value = []
    updateStats()
    return
  }

  const params: Record<string, any> = {
    knowledge_base: currentKnowledgeBase.value
  }
  console.log('Sending request to /documents/directories/ with params:', params)
  axios.get('/documents/directories/', { params })
    .then(response => {
      console.log('loadDirectories response:', response.data)
      directories.value = response.data
      if (directories.value.length > 0) {
        // Check if saved directory exists in loaded directories
        const savedDirExists = directories.value.some(d => d.id === selectedDirectory.value)
        if (!savedDirExists) {
          // Reset to first directory if saved one doesn't exist
          selectedDirectory.value = directories.value[0].id
          selectedFolder.value = null
          breadcrumbFolders.value = []
        }
        loadDocuments()
        loadFolders()
      }
    })
    .catch(error => {
      console.error('加载目录失败:', error)
    })
}

function selectDirectory(id: number) {
  selectedDirectory.value = id
  selectedFolder.value = null
  breadcrumbFolders.value = []
  loadDocuments()
  loadFolders()
}

function drillIntoFolder(folder: Folder) {
  console.log('drillIntoFolder 被调用，folder:', folder)
  selectedFolder.value = folder.id
  console.log('设置 selectedFolder.value 为:', selectedFolder.value)
  breadcrumbFolders.value.push(folder)
  console.log('breadcrumbFolders 现在包含:', breadcrumbFolders.value.length, '个文件夹')
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
  if (!newDirName.value.trim() || !currentKnowledgeBase.value) {
    return
  }
  axios.post('/documents/directories/', {
    name: newDirName.value,
    knowledge_base: currentKnowledgeBase.value
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
  fileIdCounter = 0
}

function handleFileChange(_file: any, fileList: any[]) {
  const newFiles = fileList.map(f => f.raw)
  
  const existingNames = new Set(importFiles.value.map(item => item.file.name))
  
  for (const f of newFiles) {
    if (!existingNames.has(f.name)) {
      importFiles.value.push({
        id: fileIdCounter++,
        file: f,
        status: 'pending'
      })
    } else {
      ElMessage.warning(`文件 "${f.name}" 已存在于选择列表中，将跳过重复文件`)
    }
  }
}

function removeImportFile(index: number) {
  importFiles.value.splice(index, 1)
}

function clearAllFiles() {
  importFiles.value = []
  fileIdCounter = 0
}

async function startUpload() {
  if (importFiles.value.length === 0) {
    return
  }
  
  uploading.value = true
  
  // 更新所有文件状态为上传中
  importFiles.value.forEach(item => {
    item.status = 'uploading'
  })
  
  try {
    const formData = new FormData()
    importFiles.value.forEach(item => {
      formData.append('files', item.file)
    })
    
    if (selectedFolder.value) {
      formData.append('folder_id', selectedFolder.value.toString())
    } else if (selectedDirectory.value) {
      formData.append('directory_id', selectedDirectory.value.toString())
    }
    
    const response = await axios.post('/documents/files/upload-multiple/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    })
    
    // 更新每个文件的状态
    if (response.data && response.data.files) {
      response.data.files.forEach((result: any, index: number) => {
        if (importFiles.value[index]) {
          if (result.status) {
            importFiles.value[index].status = 'success'
          } else {
            importFiles.value[index].status = 'error'
            importFiles.value[index].errorMessage = result.error || '上传失败'
          }
        }
      })
    }
    
    const successCount = importFiles.value.filter(item => item.status === 'success').length
    ElMessage.success(`成功导入 ${successCount}/${importFiles.value.length} 个文件`)
    
    loadDocuments()
  } catch (error: any) {
    console.error('导入文件失败:', error)
    
    // 所有文件标记为失败
    importFiles.value.forEach(item => {
      item.status = 'error'
      item.errorMessage = error.response?.data?.error || '上传失败'
    })
    
    ElMessage.error('导入文件失败')
  } finally {
    uploading.value = false
  }
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
  const query: any = {}
  if (selectedDirectory.value) {
    query.directory = selectedDirectory.value
  }
  if (selectedFolder.value) {
    query.folder = selectedFolder.value
  }
  router.push({ path: '/document/new', query })
}

function editDocument(id: number) {
  const doc = documents.value.find(d => d.id === id)
  const query: any = {}
  if (doc?.directory) {
    query.directory = doc.directory
  }
  if (doc?.folder) {
    query.folder = doc.folder
  }
  router.push({ path: `/document/${id}`, query })
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

function queuePublishDocument(id: number) {
  axios.post(`/documents/documents/${id}/publish/`)
    .then(() => {
      loadDocuments()
    })
    .catch(error => console.error('加入发布队列失败:', error))
}

function queueAnalyzeDocument(id: number) {
  axios.post(`/documents/documents/${id}/queue-analyze/`)
    .then(() => {
      loadDocuments()
    })
    .catch(error => console.error('加入分析队列失败:', error))
}

async function bulkPublish() {
  const draftDocs = documents.value.filter(doc => doc.publish_status === 'draft')
  if (draftDocs.length === 0) {
    ElMessage.info('没有需要发布的文档')
    return
  }
  
  if (!confirm(`确定要将当前 ${draftDocs.length} 个未发布文档加入发布队列吗？`)) {
    return
  }
  
  let successCount = 0
  let failCount = 0
  
  for (const doc of draftDocs) {
    try {
      await axios.post(`/documents/documents/${doc.id}/publish/`)
      successCount++
    } catch (error) {
      failCount++
      console.error(`文档 ${doc.filename} 加入发布队列失败:`, error)
    }
  }
  
  loadDocuments()
  
  if (failCount === 0) {
    ElMessage.success(`成功将 ${successCount} 个文档加入发布队列`)
  } else {
    ElMessage.warning(`成功将 ${successCount} 个文档加入发布队列，${failCount} 个失败`)
  }
}

// 队列管理相关函数
function loadQueueDocuments() {
  const params: Record<string, any> = {}
  if (currentKnowledgeBase.value) {
    params.knowledge_base = currentKnowledgeBase.value
  }
  axios.get('/documents/documents/queue/', { params })
    .then(response => {
      queueDocuments.value = response.data
      selectedQueueDocs.value = []
    })
    .catch(error => console.error('加载队列文档失败:', error))
}

function selectAllQueueDocs() {
  selectedQueueDocs.value = queueDocuments.value.map(doc => doc.id)
}

function deselectAllQueueDocs() {
  selectedQueueDocs.value = []
}

async function bulkPublishSelected() {
    if (selectedQueueDocs.value.length === 0) {
        ElMessage.info('请选择要发布的文档')
        return
    }
    
    if (!confirm(`确定要将选中的 ${selectedQueueDocs.value.length} 个文档加入发布队列吗？`)) {
        return
    }
    
    bulkPublishing.value = true
    
    try {
        const response = await axios.post('/documents/documents/bulk-publish/', {
            document_ids: selectedQueueDocs.value
        })
        
        const { success_count, skipped_count, skipped_documents } = response.data
        
        let message = `成功将 ${success_count} 个文档加入发布队列`
        if (skipped_count > 0) {
            message += `，跳过 ${skipped_count} 个文档`
            console.log('Skipped documents:', skipped_documents)
        }
        
        ElMessage.success(message)
        
    } catch (error: any) {
        console.error('批量发布失败:', error)
        ElMessage.error(error.response?.data?.error || '批量发布失败')
    } finally {
        bulkPublishing.value = false
        // 重新加载队列文档和统计
        loadQueueDocuments()
        loadStats()
        loadDocuments()
    }
}

// 移动相关函数
function openMoveDocumentDialog(doc: Document) {
  movingDocument.value = doc
  selectedMoveTarget.value = null
  showMoveDocumentDialog.value = true
}

function openMoveFolderDialog(folder: Folder) {
  movingFolder.value = folder
  selectedMoveTarget.value = null
  showMoveFolderDialog.value = true
}

function loadFullTree() {
  if (!currentKnowledgeBase.value) {
    return
  }
  
  axios.get(`/documents/knowledge-bases/${currentKnowledgeBase.value}/full-tree/`)
    .then(response => {
      fullTree.value = response.data
    })
    .catch(error => {
      console.error('加载完整树失败:', error)
      ElMessage.error('加载失败')
    })
}

function selectMoveTarget(node: any) {
  selectedMoveTarget.value = node
}

async function moveDocument() {
  if (!movingDocument.value || !selectedMoveTarget.value) {
    return
  }
  
  try {
    const data: any = {}
    
    if (selectedMoveTarget.value.type === 'directory') {
      data.directory = selectedMoveTarget.value.id
      data.folder = null
    } else if (selectedMoveTarget.value.type === 'folder') {
      // 查找文件夹所属的目录
      const dir = findDirectoryForFolder(selectedMoveTarget.value.id)
      data.directory = dir
      data.folder = selectedMoveTarget.value.id
    }
    
    await axios.post(`/documents/documents/${movingDocument.value.id}/move/`, data)
    ElMessage.success('移动成功')
    showMoveDocumentDialog.value = false
    loadDocuments()
  } catch (error: any) {
    console.error('移动文档失败:', error)
    ElMessage.error(error.response?.data?.error || '移动失败')
  }
}

async function moveFolder() {
  if (!movingFolder.value || !selectedMoveTarget.value) {
    return
  }
  
  try {
    const data: any = {}
    
    if (selectedMoveTarget.value.type === 'directory') {
      data.directory = selectedMoveTarget.value.id
      data.parent = null
    } else if (selectedMoveTarget.value.type === 'folder') {
      // 查找文件夹所属的目录
      const dir = findDirectoryForFolder(selectedMoveTarget.value.id)
      data.directory = dir
      data.parent = selectedMoveTarget.value.id
    }
    
    await axios.post(`/documents/folders/${movingFolder.value.id}/move/`, data)
    ElMessage.success('移动成功')
    showMoveFolderDialog.value = false
    loadFolders()
  } catch (error: any) {
    console.error('移动文件夹失败:', error)
    ElMessage.error(error.response?.data?.error || '移动失败')
  }
}

function findDirectoryForFolder(folderId: number): number | null {
  // 在fullTree中查找文件夹所属的目录
  for (const dir of fullTree.value) {
    const found = findFolderInTree(dir, folderId)
    if (found) {
      return dir.id
    }
  }
  return null
}

function findFolderInTree(node: any, folderId: number): boolean {
  if (node.type === 'folder' && node.id === folderId) {
    return true
  }
  
  if (node.children) {
    for (const child of node.children) {
      if (findFolderInTree(child, folderId)) {
        return true
      }
    }
  }
  
  return false
}

// ZIP 导入相关方法
function handleZipFileChange(file: any) {
  zipFile.value = file.raw
  // 选择文件后自动解析
  if (zipFile.value) {
    uploadAndParseZip()
  }
}

function clearZipFile() {
  zipFile.value = null
  zipFileList.value = []
}

function cancelZipImport() {
  showZipImportDialog.value = false
  zipFile.value = null
  zipFileList.value = []
}

async function uploadAndParseZip() {
  if (!zipFile.value) {
    ElMessage.error('请先选择ZIP文件')
    return
  }
  
  parsingZip.value = true
  
  try {
    const formData = new FormData()
    formData.append('zip_file', zipFile.value)
    
    const response = await axios.post('/documents/zip/upload/', formData)
    
    // 按照相对路径排序，让嵌套结构更清晰
    const files = response.data.files.sort((a: any, b: any) => {
      const pathA = (a.relative_path || '') + '/' + a.filename
      const pathB = (b.relative_path || '') + '/' + b.filename
      return pathA.localeCompare(pathB)
    })
    
    zipFileList.value = files
    
    let message = `成功解析 ${response.data.total_files} 个文件`
    if (response.data.skipped_count > 0) {
      message += `（已跳过 ${response.data.skipped_count} 个不支持的文件）`
    }
    
    ElMessage.success(message)
    
  } catch (error: any) {
    console.error('解析ZIP文件失败:', error)
    ElMessage.error(error.response?.data?.error || '解析ZIP文件失败')
  } finally {
    parsingZip.value = false
  }
}

function selectAllZipFiles() {
  zipFileList.value.forEach(file => {
    file.selected = true
  })
}

function deselectAllZipFiles() {
  zipFileList.value.forEach(file => {
    file.selected = false
  })
}

async function startZipImport() {
  if (!zipFile.value) {
    ElMessage.error('请先选择ZIP文件')
    return
  }
  
  const selectedFiles = zipFileList.value
    .filter(f => f.selected)
    .map(f => f.path)
  
  if (selectedFiles.length === 0) {
    ElMessage.error('请至少选择一个文件')
    return
  }
  
  importingZip.value = true
  
  try {
    const formData = new FormData()
    formData.append('zip_file', zipFile.value)
    formData.append('selected_files', JSON.stringify(selectedFiles))
    
    if (selectedFolder.value) {
      formData.append('folder_id', selectedFolder.value.toString())
    } else if (selectedDirectory.value) {
      formData.append('directory_id', selectedDirectory.value.toString())
    }
    
    console.log('正在导入ZIP文件，参数:', {
      selectedFiles,
      selectedDirectory: selectedDirectory.value,
      selectedFolder: selectedFolder.value
    })
    
    const response = await axios.post('/documents/zip/import/', formData)
    
    console.log('导入响应:', response.data)
    
    const { success_count, total_count, results } = response.data
    
    // 只显示数量，不显示所有文件名
    ElMessage.success(`成功导入 ${success_count}/${total_count} 个文件`)
    
    // 延迟刷新，确保后端数据已保存
    setTimeout(() => {
      loadDocuments()
      loadFolders()
      
      // 如果选中了文件夹，重新加载该文件夹
      if (selectedFolder.value) {
        loadDocuments()
      }
    }, 500)
    
    // 关闭对话框
    showZipImportDialog.value = false
    zipFile.value = null
    zipFileList.value = []
    
  } catch (error: any) {
    console.error('导入ZIP文件失败:', error)
    ElMessage.error(error.response?.data?.error || '导入ZIP文件失败')
  } finally {
    importingZip.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function handleAdminLayoutKnowledgeBaseChange(event: CustomEvent) {
  const newKnowledgeBaseId = event.detail.knowledgeBaseId
  console.log('DocumentList: 收到AdminLayout知识库切换事件:', newKnowledgeBaseId)
  if (currentKnowledgeBase.value !== newKnowledgeBaseId) {
    currentKnowledgeBase.value = newKnowledgeBaseId
    onKnowledgeBaseChange()
  }
}

onMounted(() => {
  // Initialize state from route query parameters
  initStateFromQuery()
  loadKnowledgeBases()
  // 监听来自AdminLayout的知识库切换事件
  window.addEventListener('knowledgeBaseChanged', handleAdminLayoutKnowledgeBaseChange as EventListener)
  
  // 每10秒刷新一次统计数据
  statsTimer = window.setInterval(() => {
    if (currentKnowledgeBase.value) {
      loadStats()
    }
  }, 10000)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('knowledgeBaseChanged', handleAdminLayoutKnowledgeBaseChange as EventListener)
  // 清理定时器
  if (statsTimer) {
    clearInterval(statsTimer)
    statsTimer = null
  }
})
</script>

<style scoped>
.document-list {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.breadcrumb-section :deep(.el-breadcrumb__item) {
  cursor: pointer;
}

.breadcrumb-section :deep(.el-breadcrumb__item a) {
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.breadcrumb-section :deep(.el-breadcrumb__item a:hover) {
  color: #3498db;
}

.breadcrumb-section :deep(.el-breadcrumb__item span) {
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.breadcrumb-section :deep(.el-breadcrumb__item span:hover) {
  color: #3498db;
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

.stats-section .stats-text {
  cursor: pointer;
  transition: color 0.2s;
}

.stats-section .stats-text:hover {
  color: #1890ff;
}

.queue-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.queue-list-title {
  font-size: 14px;
  color: #666;
}

.queue-list-actions {
  display: flex;
  gap: 8px;
}

.queue-document-list {
  max-height: 400px;
  overflow-y: auto;
}

.queue-doc-item {
  display: flex;
  align-items: center;
  padding: 12px 8px;
  border-bottom: 1px solid #f0f0f0;
}

.queue-doc-item:hover {
  background-color: #fafafa;
}

.queue-doc-info {
  flex: 1;
  margin-left: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-doc-name {
  font-size: 14px;
  color: #333;
}

.queue-doc-status {
  display: flex;
  gap: 8px;
}

/* 移动相关样式 */
.move-target-selector {
  max-height: 400px;
  overflow-y: auto;
}

.tree-container {
  width: 100%;
}

.tree-container .tree-item {
  margin-bottom: 4px;
}

.tree-container .tree-node {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tree-container .tree-node:hover {
  background-color: #f5f7fa;
}

.tree-container .tree-node.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.tree-container .node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.tree-container .node-icon {
  font-size: 16px;
}

.tree-container .expand-icon {
  font-size: 14px;
  transition: transform 0.2s;
  color: #909399;
}

.tree-container .expand-icon.rotated {
  transform: rotate(90deg);
}

.tree-container .tree-children {
  margin-left: 24px;
  padding-left: 8px;
  border-left: 1px solid #e4e7ed;
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

.upload-drop-zone {
  margin-bottom: 20px;
}

.upload-tip {
  margin-top: 8px;
  color: #666;
  font-size: 13px;
}

.supported-types {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f7ff;
  border-radius: 6px;
  color: #409eff;
  font-size: 12px;
  line-height: 1.6;
}

.file-list-container {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fafafa;
  overflow: hidden;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.file-list-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.file-list-scroll {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  margin-bottom: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  transition: all 0.2s;
}

.file-item:last-child {
  margin-bottom: 0;
}

.file-item:hover {
  border-color: #667eea;
}

.file-icon-wrapper {
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.file-icon {
  font-size: 20px;
}

.file-icon.uploading {
  color: #e6a23c;
  animation: spin 1s linear infinite;
}

.file-icon.success {
  color: #67c23a;
}

.file-icon.error {
  color: #f56c6c;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  color: #2c3e50;
}

.file-error {
  font-size: 12px;
  color: #f56c6c;
}

.remove-btn {
  margin-left: 10px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

.status-tags {
  display: flex;
  align-items: center;
  gap: 8px;
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

/* ZIP 导入相关样式 */
.zip-upload-area {
  padding: 20px;
}

.zip-upload-demo {
  margin-bottom: 20px;
}

.selected-zip-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.zip-icon {
  font-size: 24px;
  color: #409eff;
}

.zip-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.upload-action {
  display: flex;
  justify-content: center;
}

.zip-file-list-area {
  padding: 10px;
}

.zip-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.zip-list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.zip-list-actions {
  display: flex;
  gap: 8px;
}

.zip-file-list-scroll {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.zip-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.zip-file-item:last-child {
  border-bottom: none;
}

.zip-file-item:hover {
  background: #f5f7fa;
}

.zip-file-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.zip-file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.path-text {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.file-name-text {
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.zip-file-size {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  margin-left: 16px;
}
</style>
