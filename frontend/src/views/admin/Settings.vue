<template>
  <div class="settings">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="AI 模型配置" name="ai">
        <div class="ai-settings">
          <el-card title="文本生成模型">
            <el-form :model="aiConfig.textGeneration" label-width="120px">
              <el-form-item label="模型提供商">
                <el-select v-model="aiConfig.textGeneration.provider">
                  <el-option value="openai" label="OpenAI" />
                  <el-option value="anthropic" label="Anthropic" />
                  <el-option value="ollama" label="Ollama (本地)" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key">
                <el-input v-model="aiConfig.textGeneration.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL">
                <el-input v-model="aiConfig.textGeneration.baseUrl" placeholder="如: https://api.openai.com/v1" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-input v-model="aiConfig.textGeneration.modelName" placeholder="如: gpt-4o" />
              </el-form-item>
              <el-form-item label="Temperature">
                <el-input v-model="aiConfig.textGeneration.temperature" type="number" min="0" max="2" step="0.1" />
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card title="Embedding 模型">
            <el-form :model="aiConfig.embedding" label-width="120px">
              <el-form-item label="模型提供商">
                <el-select v-model="aiConfig.embedding.provider">
                  <el-option value="openai" label="OpenAI" />
                  <el-option value="cohere" label="Cohere" />
                  <el-option value="ollama" label="Ollama (本地)" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key">
                <el-input v-model="aiConfig.embedding.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL">
                <el-input v-model="aiConfig.embedding.baseUrl" placeholder="请输入 API 地址" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-input v-model="aiConfig.embedding.modelName" placeholder="如: text-embedding-3-large" />
              </el-form-item>
              <el-form-item label="向量维度">
                <el-input v-model="aiConfig.embedding.dimension" type="number" />
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card title="Rerank 模型">
            <el-form :model="aiConfig.rerank" label-width="120px">
              <el-form-item label="模型提供商">
                <el-select v-model="aiConfig.rerank.provider">
                  <el-option value="cohere" label="Cohere" />
                  <el-option value="bge" label="BGE" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key">
                <el-input v-model="aiConfig.rerank.apiKey" type="password" placeholder="请输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL">
                <el-input v-model="aiConfig.rerank.baseUrl" placeholder="请输入 API 地址" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-input v-model="aiConfig.rerank.modelName" placeholder="如: bge-reranker-v2-m3" />
              </el-form-item>
            </el-form>
          </el-card>
          
          <div class="settings-actions">
            <el-button type="primary" @click="saveSettings">保存配置</el-button>
            <el-button @click="testConnection">测试连接</el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="系统设置" name="system">
        <el-card title="基本设置">
          <el-form :model="systemConfig" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="systemConfig.name" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-textarea v-model="systemConfig.description" />
            </el-form-item>
            <el-form-item label="默认语言">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

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
    dimension: 1024
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

function saveSettings() {
  alert('AI 模型配置已保存')
}

function testConnection() {
  alert('测试连接功能开发中...')
}

function saveSystemSettings() {
  alert('系统配置已保存')
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.ai-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>