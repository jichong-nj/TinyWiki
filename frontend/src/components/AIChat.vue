<template>
  <div class="ai-chat-overlay" v-if="isOpen">
    <div class="ai-chat-panel">
      <div class="chat-header">
        <div class="chat-header-left">
          <span class="chat-icon">🤖</span>
          <span class="chat-title">AI 助手</span>
        </div>
        <button class="close-btn" @click="closeChat">×</button>
      </div>
      
      <div class="chat-body">
        <div class="session-list" v-if="showSessionList && chatMode === 'builtin'">
          <div class="session-header">
            <h3>会话列表</h3>
            <button class="new-session-btn" @click="createNewSession">
              + 新会话
            </button>
          </div>
          <div class="session-items">
            <div 
              v-for="session in sessions" 
              :key="session.id"
              class="session-item"
              :class="{ active: currentSession?.id === session.id }"
              @click="loadSession(session)"
            >
              <div class="session-title">{{ session.title }}</div>
              <div class="session-meta">
                <span class="session-kb">{{ session.knowledge_base_name }}</span>
                <span class="session-time">{{ formatTime(session.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chat-messages" v-else ref="messagesRef">
          <div class="message-list">
            <div v-if="messages.length === 0" class="empty-chat">
              <div class="empty-icon">💬</div>
              <p>选择知识库和 Agent 开始对话</p>
            </div>
            
            <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
              <div class="message-avatar">
                <span v-if="msg.role === 'user'">🧑</span>
                <span v-else>🤖</span>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMarkdown(msg.content)"></div>
                
                <div v-if="msg.role === 'assistant' && msg.retrieved_documents" class="sources">
                  <div class="sources-title">参考文档：</div>
                  <div 
                    v-for="(doc, idx) in msg.retrieved_documents" 
                    :key="idx"
                    class="source-item"
                  >
                    <span class="source-title">{{ doc.title }}</span>
                    <span class="source-score">相关性: {{ (doc.score * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="isLoading" class="message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-footer" v-if="!(showSessionList && chatMode === 'builtin')">
        <div class="mode-selector">
          <label>
            <input type="radio" v-model="chatMode" value="builtin" />
            内置 AI
          </label>
          <label>
            <input type="radio" v-model="chatMode" value="openclaw" />
            OpenClaw
          </label>
        </div>
        
        <div class="kb-selector" v-if="chatMode === 'builtin'">
          <select v-model="selectedKBId" @change="onKBChange">
            <option value="">选择知识库</option>
            <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb.id">
              {{ kb.name }}
            </option>
          </select>
        </div>
        
        <div class="kb-selector" v-if="chatMode === 'openclaw'">
          <select v-model="selectedKBId">
            <option value="">选择知识库（可选）</option>
            <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb.id">
              {{ kb.name }}
            </option>
          </select>
        </div>
        
        <div class="agent-selector" v-if="chatMode === 'openclaw'">
          <select v-model="selectedAgentId">
            <option value="">选择 Agent</option>
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
              {{ agent.name }}
            </option>
          </select>
        </div>
        
        <div class="input-area">
          <textarea 
            v-model="inputMessage" 
            placeholder="输入问题..." 
            @keydown.enter.prevent="sendMessage"
            rows="1"
            ref="textareaRef"
          ></textarea>
          <button 
            class="send-btn" 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isLoading || !canSend"
          >
            发送
          </button>
        </div>
      </div>
      
      <div class="chat-footer" v-else>
        <button class="back-btn" @click="showSessionList = false">返回对话</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import axios from '../axios'
import { marked } from 'marked'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const messagesRef = ref(null)
const textareaRef = ref(null)
const showSessionList = ref(false)
const sessions = ref([])
const currentSession = ref(null)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const knowledgeBases = ref([])
const selectedKBId = ref(null)
const chatMode = ref('builtin')
const agents = ref([])
const selectedAgentId = ref(null)

const canSend = computed(() => {
  if (chatMode.value === 'builtin') {
    return selectedKBId.value !== null && selectedKBId.value !== ''
  } else {
    return selectedAgentId.value !== null && selectedAgentId.value !== ''
  }
})

const closeChat = () => {
  isOpen.value = false
}

const loadKnowledgeBases = async () => {
  try {
    const response = await axios.get('/documents/knowledge-bases/')
    knowledgeBases.value = response.data
    if (knowledgeBases.value.length > 0) {
      selectedKBId.value = knowledgeBases.value[0].id
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

const loadAgents = async () => {
  try {
    const response = await axios.get('/openclaw/agents/')
    if (response.data.success) {
      agents.value = response.data.data || []
      if (agents.value.length > 0) {
        selectedAgentId.value = agents.value[0].id
      }
    }
  } catch (error) {
    console.error('Failed to load agents:', error)
  }
}

const loadSessions = async () => {
  try {
    const response = await axios.get('/documents/chat/sessions/', {
      params: { knowledge_base_id: selectedKBId.value }
    })
    sessions.value = response.data
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

const createNewSession = async () => {
  if (!selectedKBId.value) {
    alert('请先选择知识库')
    return
  }
  
  try {
    const response = await axios.post('/documents/chat/sessions/', {
      knowledge_base_id: selectedKBId.value,
      title: '新对话'
    })
    currentSession.value = response.data
    messages.value = []
    showSessionList.value = false
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

const loadSession = async (session) => {
  currentSession.value = session
  showSessionList.value = false
  try {
    const response = await axios.get(`/documents/chat/sessions/${session.id}/`)
    messages.value = response.data.messages
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

const onKBChange = async () => {
  await loadSessions()
  if (sessions.value.length > 0) {
    await loadSession(sessions.value[0])
  } else {
    currentSession.value = null
    messages.value = []
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value || !canSend.value) {
    return
  }
  
  isLoading.value = true
  const userContent = inputMessage.value
  inputMessage.value = ''
  
  // 立即添加用户消息到界面
  const tempUserMsg = {
    id: Date.now(),
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  }
  messages.value.push(tempUserMsg)
  await scrollToBottom()
  
  try {
    if (chatMode.value === 'builtin') {
      await sendBuiltinMessage(userContent, tempUserMsg.id)
    } else {
      await sendOpenClawMessage(userContent, tempUserMsg.id)
    }
    
    await scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    // 移除临时消息
    messages.value = messages.value.filter(m => m.id !== tempUserMsg.id)
    alert('发送消息失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const sendBuiltinMessage = async (userContent, tempMsgId) => {
  // 如果没有当前会话，创建一个
  if (!currentSession.value) {
    await createNewSession()
    if (!currentSession.value) {
      return
    }
  }
  
  const response = await axios.post(`/documents/chat/sessions/${currentSession.value.id}/send/`, {
    content: userContent
  })
  
  // 移除临时消息，添加服务器返回的消息
  messages.value = messages.value.filter(m => m.id !== tempMsgId)
  messages.value.push(response.data.user_message)
  messages.value.push(response.data.assistant_message)
  
  // 更新当前会话信息
  await loadSessions()
}

const sendOpenClawMessage = async (userContent, tempMsgId) => {
  const response = await axios.post('/openclaw/chat/', {
    agent_id: selectedAgentId.value,
    query: userContent,
    knowledge_base_id: selectedKBId.value
  })
  
  // 移除临时消息，添加服务器返回的消息
  messages.value = messages.value.filter(m => m.id !== tempMsgId)
  
  // 添加用户消息
  messages.value.push({
    id: Date.now() - 1,
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  })
  
  // 添加 AI 响应
  messages.value.push({
    id: Date.now(),
    role: 'assistant',
    content: response.data.data?.response || response.data.data || '未获取到响应',
    created_at: new Date().toISOString()
  })
}

const formatMarkdown = (content) => {
  if (!content) return ''
  return marked.parse(content, { breaks: true, gfm: true })
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

// 监听模式变化
watch(chatMode, async (newMode) => {
  if (newMode === 'openclaw') {
    await loadAgents()
  }
})

// 监听打开事件
watch(isOpen, async (val) => {
  if (val) {
    await loadKnowledgeBases()
    await loadSessions()
    if (chatMode.value === 'openclaw') {
      await loadAgents()
    }
  }
})
</script>

<style scoped>
.ai-chat-overlay {
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

.ai-chat-panel {
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

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-icon {
  font-size: 24px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chat-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.session-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.session-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.new-session-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: transform 0.2s;
}

.new-session-btn:hover {
  transform: translateY(-1px);
}

.session-items {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f8f9fa;
}

.session-item.active {
  background: #e8f0fe;
  border-left: 4px solid #667eea;
}

.session-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.session-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #888;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-chat {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #e3f2fd;
}

.message.assistant .message-avatar {
  background: #f3e5f5;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f5f5f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-text :deep(p) {
  margin: 8px 0;
}

.message-text :deep(pre) {
  background: #2d2d2d;
  color: #ccc;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.sources {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
}

.sources-title {
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.source-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}

.source-item:last-child {
  border-bottom: none;
}

.source-title {
  color: #667eea;
  font-weight: 500;
}

.source-score {
  color: #888;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #888;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

.chat-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  flex-shrink: 0;
}

.mode-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.mode-selector label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
}

.mode-selector input[type="radio"] {
  cursor: pointer;
}

.kb-selector {
  margin-bottom: 12px;
}

.agent-selector {
  margin-bottom: 12px;
}

.kb-selector select,
.agent-selector select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.kb-selector select:focus,
.agent-selector select:focus {
  border-color: #667eea;
}

.input-area {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  max-height: 120px;
  font-family: inherit;
}

.input-area textarea:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: transform 0.2s, opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-btn {
  width: 100%;
  padding: 12px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #e8e8e8;
}
</style>
