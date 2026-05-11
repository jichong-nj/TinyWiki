<template>
  <div class="settings">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="AI 模型配置" name="ai">
        <div class="protocol-hint">
          <el-alert title="OpenAI 通用协议" type="info" :closable="false">
            <p>所有模型均采用 OpenAI 兼容协议，支持自定义 Base URL 接入各类兼容服务（如 Ollama、FastChat 等）。</p>
          </el-alert>
        </div>
        
        <div class="ai-settings">
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon color="#409EFF" size="24"><ChatDotRound /></el-icon>
                  <span>会话模型（文本生成）</span>
                </div>
                <el-tag type="primary">必填</el-tag>
              </div>
            </template>
            <div class="model-description">
              用于 AI 对话、文档摘要、内容理解等文本生成任务
            </div>
            <div class="test-result" v-if="testResults.textGeneration">
              <el-alert 
                :title="testResults.textGeneration.success ? '测试通过' : '测试失败'" 
                :type="testResults.textGeneration.success ? 'success' : 'error'"
                :closable="true"
                @close="testResults.textGeneration = null"
              >
                {{ testResults.textGeneration.message }}
              </el-alert>
            </div>
            
            <el-form :model="aiConfig.textGeneration" label-width="120px">
              <el-form-item label="模型提供商" required>
                <el-select v-model="aiConfig.textGeneration.provider">
                  <el-option value="openai" label="OpenAI" />
                  <el-option value="anthropic" label="Anthropic" />
                  <el-option value="ollama" label="Ollama (本地)" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key" required>
                <el-input v-model="aiConfig.textGeneration.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL" required>
                <el-input v-model="aiConfig.textGeneration.baseUrl" placeholder="如: https://api.openai.com/v1 或 http://localhost:11434/v1" />
              </el-form-item>
              <el-form-item label="模型名称" required>
                <el-input v-model="aiConfig.textGeneration.modelName" placeholder="如: gpt-4o" />
              </el-form-item>
              <el-form-item label="Temperature">
                <el-input v-model="aiConfig.textGeneration.temperature" type="number" min="0" max="2" step="0.1" />
              </el-form-item>
            </el-form>
            
            <div class="card-actions">
              <el-button type="primary" @click="testModel('textGeneration')" :loading="loadingModels.textGeneration">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </div>
          </el-card>
          
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon color="#67C23A" size="24"><MagicStick /></el-icon>
                  <span>Embedding 模型（向量化）</span>
                </div>
                <el-tag type="success">必填</el-tag>
              </div>
            </template>
            <div class="model-description">
              将文档和查询转换为向量，用于语义搜索和 RAG 知识库检索
            </div>
            <div class="test-result" v-if="testResults.embedding">
              <el-alert 
                :title="testResults.embedding.success ? '测试通过' : '测试失败'" 
                :type="testResults.embedding.success ? 'success' : 'error'"
                :closable="true"
                @close="testResults.embedding = null"
              >
                {{ testResults.embedding.message }}
              </el-alert>
            </div>
            
            <el-form :model="aiConfig.embedding" label-width="120px">
              <el-form-item label="模型提供商" required>
                <el-select v-model="aiConfig.embedding.provider">
                  <el-option value="openai" label="OpenAI" />
                  <el-option value="cohere" label="Cohere" />
                  <el-option value="ollama" label="Ollama (本地)" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key" required>
                <el-input v-model="aiConfig.embedding.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL" required>
                <el-input v-model="aiConfig.embedding.baseUrl" placeholder="请输入 API 地址" />
              </el-form-item>
              <el-form-item label="模型名称" required>
                <el-input v-model="aiConfig.embedding.modelName" placeholder="如: text-embedding-3-large" />
              </el-form-item>
              <el-form-item label="向量维度">
                <el-input v-model="aiConfig.embedding.dimension" type="number" />
              </el-form-item>
              <el-form-item label="Input Type">
                <el-select v-model="aiConfig.embedding.inputType">
                  <el-option value="query" label="query" />
                  <el-option value="document" label="document" />
                </el-select>
                <span style="margin-left: 10px; color: #999; font-size: 12px;">NVIDIA 非对称模型需要设置此项</span>
              </el-form-item>
            </el-form>
            
            <div class="card-actions">
              <el-button type="primary" @click="testModel('embedding')" :loading="loadingModels.embedding">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </div>
          </el-card>
          
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon color="#E6A23C" size="24"><Sort /></el-icon>
                  <span>Rerank 模型（重排序）</span>
                </div>
                <el-tag type="warning">可选</el-tag>
              </div>
            </template>
            <div class="model-description">
              对初步检索结果进行重新排序，提升搜索精准度
            </div>
            <div class="test-result" v-if="testResults.rerank">
              <el-alert 
                :title="testResults.rerank.success ? '测试通过' : '测试失败'" 
                :type="testResults.rerank.success ? 'success' : 'error'"
                :closable="true"
                @close="testResults.rerank = null"
              >
                {{ testResults.rerank.message }}
              </el-alert>
            </div>
            
            <el-form :model="aiConfig.rerank" label-width="120px">
              <el-form-item label="模型提供商" required>
                <el-select v-model="aiConfig.rerank.provider">
                  <el-option value="cohere" label="Cohere" />
                  <el-option value="bge" label="BGE" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key" required>
                <el-input v-model="aiConfig.rerank.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL" required>
                <el-input v-model="aiConfig.rerank.baseUrl" placeholder="请输入 API 地址" />
              </el-form-item>
              <el-form-item label="模型名称" required>
                <el-input v-model="aiConfig.rerank.modelName" placeholder="如: bge-reranker-v2-m3" />
              </el-form-item>
            </el-form>
            
            <div class="card-actions">
              <el-button type="primary" @click="testModel('rerank')" :loading="loadingModels.rerank">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </div>
          </el-card>
          
          <div class="settings-actions">
            <el-button type="primary" size="large" @click="saveSettings">
              <el-icon><Check /></el-icon>
              保存配置
            </el-button>
            <el-button size="large" @click="testAllModels">
              <el-icon><VideoPlay /></el-icon>
              测试所有模型
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="系统设置" name="system">
        <el-card title="基本设置">
          <el-form :model="systemConfig" label-width="120px">
            <el-form-item label="系统名称" required>
              <el-input v-model="systemConfig.name" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input v-model="systemConfig.description" type="textarea" />
            </el-form-item>
            <el-form-item label="默认语言" required>
              <el-select v-model="systemConfig.language">
                <el-option value="zh-CN" label="中文" />
                <el-option value="en-US" label="English" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
        
        <div class="settings-actions">
          <el-button type="primary" @click="saveSystemSettings">保存配置</el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <div class="test-history" v-if="testHistory.length > 0">
      <el-card title="测试历史记录">
        <el-table :data="testHistory" border>
          <el-table-column prop="model" label="模型类型" />
          <el-table-column prop="timestamp" label="测试时间" />
          <el-table-column prop="success" label="测试结果">
            <template #default="scope">
              <el-tag :type="scope.row.success ? 'success' : 'danger'">
                {{ scope.row.success ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="错误信息" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from '../../axios'
import { 
  ChatDotRound, 
  MagicStick, 
  Sort, 
  Connection, 
  Check, 
  VideoPlay 
} from '@element-plus/icons-vue'

const activeTab = ref('ai')

const aiConfig = reactive({
    textGeneration: {
        provider: 'openai',
        apiKey: '',
        baseUrl: 'https://api.openai.com/v1',
        modelName: 'gpt-4o',
        temperature: 0.7
    },
    embedding: {
        provider: 'openai',
        apiKey: '',
        baseUrl: 'https://api.openai.com/v1',
        modelName: 'text-embedding-3-large',
        dimension: 1024,
        inputType: 'query'
    },
    rerank: {
        provider: 'cohere',
        apiKey: '',
        baseUrl: 'https://api.cohere.com/v1',
        modelName: 'rerank-english-v3.0'
    }
})

const systemConfig = reactive({
    name: '知识库管理系统',
    description: '企业级知识库管理系统',
    language: 'zh-CN'
})

// Load config on mount
onMounted(async () => {
    try {
        const [aiRes, systemRes] = await Promise.all([
            axios.get('/ai/config/'),
            axios.get('/system/config/')
        ])
        
        if (aiRes.data.success && aiRes.data.data) {
            Object.assign(aiConfig, aiRes.data.data)
        }
        
        if (systemRes.data.success && systemRes.data.data) {
            Object.assign(systemConfig, systemRes.data.data)
        }
    } catch (error) {
        console.error('Failed to load config:', error)
    }
})

const loadingModels = reactive({
  textGeneration: false,
  embedding: false,
  rerank: false
})

const testResults = reactive({
  textGeneration: null as { success: boolean; message: string } | null,
  embedding: null as { success: boolean; message: string } | null,
  rerank: null as { success: boolean; message: string } | null
})

interface TestHistoryItem {
  model: string
  timestamp: string
  success: boolean
  message: string
}

const testHistory = ref<TestHistoryItem[]>([])

function addTestHistory(model: string, success: boolean, message: string) {
  testHistory.value.unshift({
    model,
    timestamp: new Date().toLocaleString(),
    success,
    message: success ? '测试通过' : message
  })
  if (testHistory.value.length > 10) {
    testHistory.value.pop()
  }
}

function testModel(modelType: 'textGeneration' | 'embedding' | 'rerank') {
  loadingModels[modelType] = true
  testResults[modelType] = null
  
  const config = aiConfig[modelType]
  const modelNames: Record<string, string> = {
    textGeneration: '文本生成模型',
    embedding: 'Embedding 模型',
    rerank: 'Rerank 模型'
  }
  
  const postData: Record<string, any> = {
    model_type: modelType,
    provider: config.provider,
    api_key: config.apiKey,
    base_url: config.baseUrl,
    model_name: config.modelName
  }
  
  if (modelType === 'embedding' && 'inputType' in config && config.inputType) {
    postData.input_type = config.inputType
  }
  
  axios.post('/ai/test-model/', postData)
  .then(response => {
    const result = response.data
    testResults[modelType] = {
      success: result.success,
      message: result.message || '测试通过'
    }
    addTestHistory(modelNames[modelType], result.success, result.message || '')
  })
  .catch(error => {
    const message = error.response?.data?.message || error.message || '连接失败'
    testResults[modelType] = {
      success: false,
      message
    }
    addTestHistory(modelNames[modelType], false, message)
  })
  .finally(() => {
    loadingModels[modelType] = false
  })
}

async function testAllModels() {
  await testModel('textGeneration')
  await new Promise(resolve => setTimeout(resolve, 500))
  await testModel('embedding')
  await new Promise(resolve => setTimeout(resolve, 500))
  await testModel('rerank')
}

function saveSettings() {
  axios.post('/ai/config/', aiConfig)
    .then(() => {
      showNotification('AI 模型配置已保存')
    })
    .catch(error => {
      console.error('保存失败:', error)
      showNotification('保存失败: ' + (error.response?.data?.message || error.message), 'error')
    })
}

function saveSystemSettings() {
  axios.post('/system/config/', systemConfig)
    .then(() => {
      showNotification('系统配置已保存')
    })
    .catch(error => {
      console.error('保存失败:', error)
      showNotification('保存失败: ' + (error.response?.data?.message || error.message), 'error')
    })
}

function showNotification(message: string | object, type: 'success' | 'error' | 'info' = 'success') {
  const msg = typeof message === 'object' ? JSON.stringify(message) : message
  const alert = document.createElement('div')
  alert.className = `el-alert el-alert--${type} is-light`
  alert.innerHTML = `
    <i class="el-alert__icon el-icon-${type === 'success' ? 'check-circle' : type === 'error' ? 'error' : 'info'}"></i>
    <span class="el-alert__title">${msg}</span>
  `
  alert.style.position = 'fixed'
  alert.style.top = '20px'
  alert.style.right = '20px'
  alert.style.zIndex = '9999'
  alert.style.padding = '15px 20px'
  alert.style.borderRadius = '4px'
  document.body.appendChild(alert)
  setTimeout(() => {
    alert.remove()
  }, 3000)
}
</script>

<style scoped>
.settings {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.protocol-hint {
  margin-bottom: 20px;
}

.ai-settings {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.model-description {
  color: #666;
  font-size: 14px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.test-result {
  margin-bottom: 15px;
}

.card-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.settings-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.test-history {
  margin-top: 20px;
}
</style>